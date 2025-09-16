import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime
import os
import random
import uuid
import psycopg2  # pip install psycopg2-binary

# ======================
# Database Config
# ======================
DB_CONFIG = {
    "dbname": "Pizza_DB",
    "user": "postgres",
    "password": "Eng0802097@",
    "host": "localhost",
    "port": "5432"
}

# ======================
# Files and Directories
# ======================
orders_file = 'pizza_orders.json'
data_file = 'pizza_data.json'
receipts_dir = 'receipts'
os.makedirs(receipts_dir, exist_ok=True)

# ======================
# Pizza Data Handling
# ======================
def load_pizza_data():
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {
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

def save_pizza_data():
    with open(data_file, 'w') as f:
        json.dump(pizza_data, f, indent=4)

pizza_data = load_pizza_data()

# ======================
# Database Save
# ======================
def save_order(order_list):
    try:
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
                str(uuid.uuid4()),
                timestamp,
                item['name'],
                item['type'],
                item['qty'],
                item['total'],
                item['discount']
                # item['discount'] if you want discount o be in numeric
            ))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# ======================
# Helpers
# ======================
def get_least_ordered_pizzas(n=3):
    order_counts = {data['name']: 0 for data in pizza_data.values()}
    if os.path.exists(orders_file):
        with open(orders_file, 'r', encoding='utf-8') as f:
            try:
                orders = json.load(f)
                for order in orders:
                    name = order['pizza_type']
                    if name in order_counts:
                        order_counts[name] += 1
            except json.JSONDecodeError:
                pass
    sorted_pizzas = sorted(order_counts.items(), key=lambda x: x[1])
    least_names = [name for name, _ in sorted_pizzas[:n]]
    return [k for k, v in pizza_data.items() if v['name'] in least_names]

least_ordered_ids = get_least_ordered_pizzas()
PIZZA_OF_THE_DAY_ID = random.choice(least_ordered_ids) if least_ordered_ids else None
PIZZA_OF_THE_DAY_NAME = pizza_data[PIZZA_OF_THE_DAY_ID]['name'] if PIZZA_OF_THE_DAY_ID else "None"

def save_order_to_json(pizza_type, order_type, quantity, price, discount_amount):
    order = {
        'order_datetime': datetime.now().strftime('%Y-%m-%d-%H:%M:%S'),
        'pizza_type': pizza_type,
        'order_type': order_type,
        'quantity': quantity,
        'total_price': price,
        'discount_applied': discount_amount
    }
    if os.path.exists(orders_file):
        with open(orders_file, 'r+', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
            data.append(order)
            f.seek(0)
            json.dump(data, f, indent=4)
    else:
        with open(orders_file, 'w', encoding='utf-8') as f:
            json.dump([order], f, indent=4)

def calculate_payment(price, quantity, discount_rate=0.0):
    total = price * quantity
    discount_amount = total * discount_rate
    return total - discount_amount, discount_amount

def save_receipt(order_items, total, discount_info):
    receipt_id = str(uuid.uuid4())
    filename = os.path.join(receipts_dir, f"{receipt_id}.txt")
    with open(filename, 'w') as f:
        f.write("===== RUSHMORE PIZZERIA RECEIPT =====\n")
        for item in order_items:
            f.write(f"{item['pizza']} ({item['otype']}) x{item['qty']} = ${item['subtotal']:.2f}\n")
        f.write("--------------------------------------\n")
        f.write(f"Total     : ${total:.2f}\n")
        if discount_info:
            f.write(f"Discounts : {discount_info}\n")
        else:
            f.write("Discounts : None\n")
        f.write("======================================\n")

# ======================
# Discount Logic
# ======================
def get_discount_rate(name, otype, qty):
    if name == PIZZA_OF_THE_DAY_NAME:
        return 0.25
    if otype == "Box":
        if qty >= 10:
            return 0.20
        elif qty >= 5:
            return 0.10
    elif otype == "Slice":
        if qty >= 8:
            return 0.05
    return 0.0

# ======================
# GUI Functions
# ======================
def show_order_summary():
    if not os.path.exists(orders_file):
        messagebox.showinfo("Summary", "No order history found.")
        return
    try:
        with open(orders_file, 'r') as f:
            orders = json.load(f)
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Order data is corrupted.")
        return

    pizza_summary = {}
    type_summary = {"Box": {"quantity": 0, "revenue": 0.0}, "Slice": {"quantity": 0, "revenue": 0.0}}

    for order in orders:
        name = order['pizza_type']
        otype = order['order_type']
        qty = order['quantity']
        rev = order['total_price']

        if name not in pizza_summary:
            pizza_summary[name] = {"quantity": 0, "revenue": 0.0}
        pizza_summary[name]['quantity'] += qty
        pizza_summary[name]['revenue'] += rev

        if otype in type_summary:
            type_summary[otype]['quantity'] += qty
            type_summary[otype]['revenue'] += rev

    summary = "====== SUMMARY BY PIZZA NAME ======\n"
    summary += f"{'Pizza Name':<20} {'Qty':<5} {'Revenue($)':>10}\n"
    summary += "-" * 40 + "\n"
    for name, data in pizza_summary.items():
        summary += f"{name:<20} {data['quantity']:<5} {data['revenue']:>10.2f}\n"

    summary += "\n====== SUMMARY BY ORDER TYPE ======\n"
    summary += f"{'Order Type':<12} {'Qty':<5} {'Revenue($)':>10}\n"
    summary += "-" * 35 + "\n"
    for otype, data in type_summary.items():
        summary += f"{otype:<12} {data['quantity']:<5} {data['revenue']:>10.2f}\n"

    messagebox.showinfo("Order Summary", summary)

def handle_order(pizza_id):
    data = pizza_data[pizza_id]
    popup = tk.Toplevel()
    popup.title("Order Pizza")

    tk.Label(popup, text=f"Ordering: {data['name']}").pack()

    tk.Label(popup, text="Order Type (Box/Slice):").pack()
    order_type_entry = tk.Entry(popup)
    order_type_entry.pack()

    tk.Label(popup, text="Quantity:").pack()
    quantity_entry = tk.Entry(popup)
    quantity_entry.pack()

    def confirm():
        try:
            otype = order_type_entry.get().strip().capitalize()
            qty = int(quantity_entry.get())
            if otype not in ["Box", "Slice"] or qty < 1:
                raise ValueError

            price = data['price']
            slice_price = round(price / 8, 2)
            unit_price = price if otype == "Box" else slice_price

            discount_rate = get_discount_rate(data['name'], otype, qty)
            total, discount_amount = calculate_payment(unit_price, qty, discount_rate)

            save_order_to_json(data['name'], otype, qty, total, discount_amount)
            save_receipt(
                [{"pizza": data['name'], "otype": otype, "qty": qty, "subtotal": total}],
                total,
                f"{int(discount_rate*100)}%" if discount_rate > 0 else ""
            )
            save_order([{"name": data['name'], "type": otype, "qty": qty, "total": total, "discount": discount_amount}])

            messagebox.showinfo("Success", f"Order placed!\nTotal: ${total:.2f}")
            popup.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid input.")

    tk.Button(popup, text="Place Order", command=confirm).pack(pady=5)

def show_multi_order_window():
    popup = tk.Toplevel()
    popup.title("Order Multiple Pizzas")

    entries = []
    row = 0
    for pid, data in pizza_data.items():
        tk.Label(popup, text=f"{data['name']} (${data['price']:.2f})").grid(row=row, column=0)
        qty_entry = tk.Entry(popup, width=5)
        qty_entry.grid(row=row, column=1)
        type_entry = tk.Entry(popup, width=7)
        type_entry.insert(0, "Box")
        type_entry.grid(row=row, column=2)
        entries.append((pid, qty_entry, type_entry))
        row += 1

    def confirm():
        order_items = []
        db_orders = []
        total = 0
        discount_info = []
        for pid, qty_entry, type_entry in entries:
            try:
                qty = int(qty_entry.get())
                if qty <= 0:
                    continue
                otype = type_entry.get().strip().capitalize()
                if otype not in ["Box", "Slice"]:
                    raise ValueError
                data = pizza_data[pid]
                price = data['price']
                slice_price = round(price / 8, 2)
                unit_price = price if otype == "Box" else slice_price

                discount_rate = get_discount_rate(data['name'], otype, qty)
                subtotal, discount_amount = calculate_payment(unit_price, qty, discount_rate)
                total += subtotal

                save_order_to_json(data['name'], otype, qty, subtotal, discount_amount)
                order_items.append({"pizza": data['name'], "otype": otype, "qty": qty, "subtotal": subtotal})
                db_orders.append({"name": data['name'], "type": otype, "qty": qty, "total": subtotal, "discount": discount_amount})

                if discount_rate > 0:
                    discount_info.append(f"{data['name']} {int(discount_rate*100)}%")
            except ValueError:
                continue
        if not order_items:
            messagebox.showerror("Error", "No valid orders entered.")
            return

        save_receipt(order_items, total, ", ".join(discount_info))
        save_order(db_orders)

        messagebox.showinfo("Success", f"Order placed!\nTotal: ${total:.2f}")
        popup.destroy()

    tk.Button(popup, text="Place All Orders", command=confirm).grid(row=row, column=0, columnspan=3, pady=10)

# ======================
# GUI Setup
# ======================
root = tk.Tk()
root.title("WantMore Pizzeria")

header_label = tk.Label(root, text=f"Welcome to WantMore Pizzeria. Today's Pizza of the Day is: {PIZZA_OF_THE_DAY_NAME}! Get 25% off when you order it", font=("Arial", 14), fg="blue")
header_label.pack(pady=10)

menu_frame = tk.Frame(root)
menu_frame.pack(pady=20)

def render_menu():
    for widget in menu_frame.winfo_children():
        widget.destroy()
    row, col = 0, 0
    for pid, data in pizza_data.items():
        label = f"{data['name']} - ${data['price']:.2f}"
        if pid == PIZZA_OF_THE_DAY_ID:
            label += " (Special!)"
        tk.Button(menu_frame, text=label, width=25, command=lambda pid=pid: handle_order(pid)).grid(row=row, column=col, padx=5, pady=5)
        col += 1
        if col > 2:
            col = 0
            row += 1

render_menu()

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="View Summary", command=show_order_summary).grid(row=0, column=0, padx=10)
tk.Button(button_frame, text="Order Multiple Pizzas", command=show_multi_order_window).grid(row=0, column=1, padx=10)

root.mainloop()
