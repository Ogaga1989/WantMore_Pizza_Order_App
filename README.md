
# WantMore Pizzaria Ordering App 🍕 

A full-featured pizza ordering application with sample order receipts and integrated PostgreSQL database for tracking and managing orders.

## 📂 Repository Contents

This repository includes:  

- **WantMore_Pizza_App/** – The Python source code for the pizza ordering for both terminal and graphic user interface systems  
- **order_receipt/** – Sample text receipts generated from orders.  
- **orders_data/** – Sample order data exported from the integrated PostgreSQL database.  
- **Pizza_DB.sql** – SQL file to create the `Pizza_DB` database and `orders` table.  


## 🚀 Getting Started

### 1. Clone the Repository

git clone https://github.com/ogaga1989/WantMore_Pizza_Ordering_App.git

cd WantMore_Pizza_Ordering_App

### 2. Set Up the Database

- Make sure PostgreSQL is installed and running, then run the `Pizza_DB.sql` script to create the   database and orders table:

psql -U <your_postgres_user> -f Pizza_DB.sql

- Update the database credentials in `WantMore_Pizza_App` if needed (`DB_CONFIG` dictionary).  

### 3. Install Dependencies

- Ensure you have Python installed (3.8+ recommended), then install required packages:

pip install psycopg2

- Add any other dependencies if needed

### 4. Run the Application

- Navigate to the Python source folder and run the app:

python WantMore_Pizza_App.py

- Follow the on-screen prompts to place orders, generate receipts, and manage pizzas.  


## 📄 Sample Outputs

- Receipts are saved in the `order_receipt/` folder.  
- Sample order data is stored in `orders_data/`.  

---

## 🔧 Features

- Place pizza orders by box or slice.  
- Special **Pizza of the Day** discounts automatically applied.  
- Generate and save receipts locally and via email.  
- Admin functions to add, edit, or delete pizzas.  
- Integrated PostgreSQL database for tracking and managing orders.  

---

## 💻 License

This project is open-source and available for educational and personal use.

