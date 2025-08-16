

# Create Pizza_DB Database
create database Pizza_DB;

# Create Orders Table
CREATE TABLE orders (
    id UUID PRIMARY KEY,
    order_datetime TIMESTAMP NOT NULL,
    pizza_type VARCHAR(50) NOT NULL,
    order_type VARCHAR(10) NOT NULL,
    quantity INT NOT NULL,
    total_price NUMERIC(10,2) NOT NULL,
    discount_applied BOOLEAN NOT NULL
);
