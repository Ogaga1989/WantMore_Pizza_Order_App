
# Importing Libraries
import os
import random
import uuid
import smtplib
import psycopg2
from datetime import datetime
from email.message import EmailMessage
import shutil


# Pizza Menu
pizza_data = {
    "1": {"name": "Classic", "price": 3.4},
    "2": {"name": "Chicken", "price": 4.5},
    "3": {"name": "Pepperoni", "price": 4.0},
    "4": {"name": "Deluxe", "price": 6.0},
    "5": {"name": "Vegetable", "price": 4.0},
    "6": {"name": "Chocolate", "price": 12.0},
    "7": {"name": "Cheese", "price": 5.0},
    "8": {"name": "Hawaiian", "price": 7.0},
    "9": {"name": "Greek", "price": 8.0}
}



# Database connection configuration
DB_CONFIG = {
    'dbname': 'Pizza_DB',         
    'user': 'postgres',       
    'password': 'Eng0802097@',
    'host': 'localhost',
    'port': '5432'
}


# Configurations
RECEIPT_DIR = 'receipts'
os.makedirs(RECEIPT_DIR, exist_ok=True)

# Email configuration
EMAIL_CONFIG = {
    'sender': 'ogagaogaga05@gmail.com',
    'password': 'Eng0802097@',
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587
}

# Helper to get least ordered pizzas
def get_least_ordered_pizzas(n=3):
    order_counts = {data["name"]: 0 for data in pizza_data.values()}
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT pizza_type, COUNT(*) FROM orders GROUP BY pizza_type")
        for name, count in cur.fetchall():
            if name in order_counts:
                order_counts[name] = count
        cur.close()
        conn.close()
    except:
        pass
    sorted_pizzas = sorted(order_counts.items(), key=lambda x: x[1])
    least_ordered_names = [name for name, _ in sorted_pizzas[:n]]
    return [key for key, val in pizza_data.items() if val["name"] in least_ordered_names]

least_ordered_ids = get_least_ordered_pizzas()
PIZZA_OF_THE_DAY_ID = random.choice(least_ordered_ids) if least_ordered_ids else "1"
PIZZA_OF_THE_DAY = pizza_data[PIZZA_OF_THE_DAY_ID]["name"]

# Admin Functions
def delete_pizza():
    if input("Admin password: ") != "1234":
        print("Access denied.")
        return
    for key, val in pizza_data.items():
        print(f"{key}: {val['name']} - ${val['price']}")
    pid = input("Enter Pizza ID to delete: ").strip()
    if pid == PIZZA_OF_THE_DAY_ID:
        print("Cannot delete Pizza of the Day.")
    elif pid in pizza_data:
        print(f"{pizza_data.pop(pid)['name']} deleted.")
    else:
        print("Invalid ID.")

def edit_pizza():
    if input("Admin password: ") != "1234":
        print("Access denied.")
        return
    for key, val in pizza_data.items():
        print(f"{key}: {val['name']} - ${val['price']}")
    pid = input("Enter Pizza ID to edit: ").strip()
    if pid not in pizza_data:
        print("Invalid ID.")
        return
    name = input("New name (blank to skip): ").strip()
    price = input("New price (blank to skip): ").strip()
    if name:
        pizza_data[pid]["name"] = name
    if price:
        try:
            pizza_data[pid]["price"] = float(price)
        except ValueError:
            print("Invalid price. Skipped.")
    print("Pizza updated.")

def add_new_pizza():
    if input("Admin password: ") != "1234":
        print("Access denied.")
        return
    name = input("New pizza name: ").strip()
    try:
        price = float(input("Price: "))
        new_id = str(max(int(k) for k in pizza_data) + 1)
        pizza_data[new_id] = {"name": name, "price": price}
        print(f"{name} added with ID {new_id}.")
    except ValueError:
        print("Invalid price.")

# Order and Receipt
def calculate_payment(price, quantity, discount_rate=0.0):
    total = price * quantity
    discount = total * discount_rate
    return total - discount, discount_rate

def save_order(order_list):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    timestamp = datetime.now()
    
    for item in order_list:
        cursor.execute("""
            INSERT INTO orders (
                id, order_datetime, pizza_type, order_type,
                quantity, total_price, discount_applied
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            str(uuid.uuid4()),  # Convert UUID to string
            timestamp,
            item['name'],
            item['type'],
            item['qty'],
            item['total'],
            item['discount'] > 0
        ))
    
    conn.commit()
    cursor.close()
    conn.close()


def save_receipt(order_list, customer_email=None):
    receipt_id = str(uuid.uuid4())
    # Folder inside your project (VS Code)
    receipt_dir = 'receipts'
    os.makedirs(receipt_dir, exist_ok=True)
    filename = os.path.join(receipt_dir, f"{receipt_id}.txt")

    # Build receipt content
    lines = [
        "===== RUSHMORE PIZZERIA RECEIPT =====",
        f"Receipt ID   : {receipt_id}",
        f"Date/Time    : {datetime.now()}",
        "--------------------------------------"
    ]
    total_sum = 0
    for item in order_list:
        lines.append(f"{item['name']} ({item['type']}) x{item['qty']} = ${item['total']:.2f}")
        if item['discount'] > 0:
            lines.append(f"  -> Discount Applied: {int(item['discount'] * 100)}%")
            if item['discount'] == 0.25 and item['name'] == PIZZA_OF_THE_DAY:
                lines.append("  🎉 Special Pizza of the Day Discount Applied! Enjoy your 25% off!")
        total_sum += item['total']
    lines.extend([
        "--------------------------------------",
        f"TOTAL: ${total_sum:.2f}",
        "======================================"
    ])

    # Save in project folder
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("\n".join(lines))
    print(f"🧾 Receipt saved to: {filename}")

    # Copy receipt to a folder on your PC
    destination_folder = "C:\\Users\\Admin\\Desktop\\Data Engineering Materials\\RUSH PIZZA\\Updated_WantMore_Pizzaria"  # <-- change this 
    os.makedirs(destination_folder, exist_ok=True)
    shutil.copy(filename, destination_folder)
    print(f"📂 Receipt also copied to: {destination_folder}")

    # Optionally email receipt
    if customer_email:
        send_email_receipt("\n".join(lines), customer_email)


# Send Email to Customer
def send_email_receipt(content, to_email):
    msg = EmailMessage()
    msg['Subject'] = 'Your Pizza Order Receipt'
    msg['From'] = EMAIL_CONFIG['sender']
    msg['To'] = to_email
    msg.set_content(content)

    try:
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['sender'], EMAIL_CONFIG['password'])
            server.send_message(msg)
        print(f"📧 Receipt emailed to {to_email}")
    except Exception as e:
        print("Failed to send email:", e)

# Order Handling
def get_order_details(pizza_id):
    pizza = pizza_data[pizza_id]
    name = pizza["name"]
    price = pizza["price"]
    slice_price = round(price / 8, 2)

    while True:
        otype = input(f"{name}: (B)ox or (S)lice? ").strip().upper()
        if otype == "B":
            qty = input("Number of boxes: ")
            if not qty.isdigit():
                print("Invalid input.")
                continue
            qty = int(qty)
            discount = 0.25 if name == PIZZA_OF_THE_DAY else 0.2 if qty >= 10 else 0.1 if qty >= 5 else 0.0
            total, disc = calculate_payment(price, qty, discount)
            return {"name": name, "type": "Box", "qty": qty, "total": total, "discount": disc}
        elif otype == "S":
            qty = input("Number of slices (max 16): ")
            if not qty.isdigit() or int(qty) > 16:
                print("Invalid or too many slices.")
                continue
            qty = int(qty)
            discount = 0.25 if name == PIZZA_OF_THE_DAY else 0.05 if qty >= 8 else 0.0
            total, disc = calculate_payment(slice_price, qty, discount)
            return {"name": name, "type": "Slice", "qty": qty, "total": total, "discount": disc}
        else:
            print("Choose B or S.")

# Display
def show_summary():
    admin_pw = int(input("Please enter authorisation password ").strip())
    if admin_pw !=1234:
        print("Access Denied!")
        return
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT pizza_type, SUM(quantity), SUM(total_price) FROM orders GROUP BY pizza_type")
        rows = cur.fetchall()
        print("\n====== SUMMARY BY PIZZA NAME ======")
        print(f"{'Pizza':<20}{'Qty':<6}{'Revenue ($)':>12}")
        for row in rows:
            print(f"{row[0]:<20}{row[1]:<6}{row[2]:>12.2f}")
        cur.close()
        conn.close()
    except Exception as e:
        print("Error fetching summary:", e)

def print_menu():
    print(f"\n🎉 The Pizza of the Day is: {PIZZA_OF_THE_DAY}, get 25% OFF if ordered!")
    print("------ Pizza Menu ------")
    for key, val in pizza_data.items():
        tag = " (Special!)" if key == PIZZA_OF_THE_DAY_ID else ""
        print(f"{key}: {val['name']} - ${val['price']:.2f}{tag}")

# Main
def main():
    while True:
        print(f"\nWelcome to WantMore Pizzeria, the home for top taste pizzas")
        print("\nPlease Select: 'q' to Quit | 's' for orders summary | 'a' to add to menu | 'e' to edit menu | 'd' to delete | 'o' to order")
        cmd = input("Enter choice: ").strip().lower()

        if cmd.lower() == 'q':
            print("Thank you. Goodbye!")
            break
        elif cmd == 's':
            show_summary()
        elif cmd == 'a':
            add_new_pizza()
        elif cmd == 'd':
            delete_pizza()
        elif cmd == 'e':
            edit_pizza()
        elif cmd == 'o':
            session_orders = []
            while True:
                print_menu()
                choice = input("Choose Pizza ID or type 'done' to checkout: ").strip()
                if choice == 'done':
                    if session_orders:
                        save_order(session_orders)
                        email = input("Enter your email for receipt (leave blank to skip): ").strip()
                        save_receipt(session_orders, email if email else None)
                        print("Order complete.")
                    else:
                        print("No items ordered.")
                    break
                elif choice in pizza_data:
                    order = get_order_details(choice)
                    session_orders.append(order)
                else:
                    print("Invalid Pizza ID.")
        elif cmd in pizza_data:
            order = get_order_details(cmd)
            save_order([order])
            save_receipt([order])
        else:
            print("Invalid option.")
        

if __name__ == "__main__":
    main()
