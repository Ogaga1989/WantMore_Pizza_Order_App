

# WantMore Pizza Ordering App 🍕  

Welcome to **WantMore Pizza Ordering App**, a full-featured Python application that lets users place pizza orders, generate receipts, and track order data with an integrated PostgreSQL database.  


## 📂 Repository Content

WantMore_Pizza_Ordering_App/
│
├─ WantMore_Pizza_App.py # Python source code for the ordering system
├─ order_receipt/ # Sample receipts generated from orders
├─ orders_data/ # CSV/ export of orders from PostgreSQL
├─ Pizza_DB.sql # SQL file to create Pizza_DB database and orders table
└─ README.md # Project documentation


## Features
- Place pizza orders through a Python application
- Generate and save detailed receipts for each order
- Apply discounts (including special Pizza of the Day)
- Store and retrieve orders in a PostgreSQL database
- Admin functions to add, edit, or delete pizzas

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/ogaga1989/WantMore_Pizza_Ordering_App.git
cd WantMore_Pizza_Ordering_App


2. Setup the database

 * Ensure PostgreSQL is installed.
 * Run the SQL script to create the database and orders table:
  
   psql -U <your_username> -f Pizza_DB.sql


3. Install Python dependencies
   pip install -r requirements.txt


4. Run the application
   python WantMore_Pizza_App.py


5. Usage

 * Place an order using the Python application.

 * View your receipt in the order_receipt/ folder.

 * Track all orders using the PostgreSQL database

Access sample data

 * Receipts are saved in the order_receipt/ folder.

 * Exported order data is in the orders_data/ folder.


License

This project is open source. Feel free to use, modify, or contribute

