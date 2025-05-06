from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import qrcode
import os
from typing import List
import uvicorn
import streamlit as st

# FastAPI app
app = FastAPI()

# SQLite setup
def init_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS inventory 
                 (id TEXT PRIMARY KEY, name TEXT, quantity INTEGER, min_stock INTEGER)""")
    c.execute("""CREATE TABLE IF NOT EXISTS customers 
                 (id TEXT PRIMARY KEY, name TEXT, email TEXT, service_history TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS tickets 
                 (id TEXT PRIMARY KEY, customer_id TEXT, issue TEXT, status TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS tasks 
                 (id TEXT PRIMARY KEY, description TEXT, assigned_to TEXT, status TEXT)""")
    conn.commit()
    conn.close()

init_db()

# Pydantic models
class InventoryItem(BaseModel):
    id: str
    name: str
    quantity: int
    min_stock: int

class Customer(BaseModel):
    id: str
    name: str
    email: str
    service_history: str

class Ticket(BaseModel):
    id: str
    customer_id: str
    issue: str
    status: str

class Task(BaseModel):
    id: str
    description: str
    assigned_to: str
    status: str

# Inventory endpoints
@app.post("/inventory/", response_model=InventoryItem)
async def add_item(item: InventoryItem):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT INTO inventory (id, name, quantity, min_stock) VALUES (?, ?, ?, ?)",
              (item.id, item.name, item.quantity, item.min_stock))
    conn.commit()
    if item.quantity < item.min_stock:
        send_email_alert(item.name, item.quantity)
    conn.close()
    return item

@app.get("/inventory/", response_model=List[InventoryItem])
async def get_inventory():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM inventory")
    items = [InventoryItem(id=row[0], name=row[1], quantity=row[2], min_stock=row[3]) for row in c.fetchall()]
    conn.close()
    return items

@app.get("/inventory/qr/{item_id}")
async def generate_qr(item_id: str):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(item_id)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(f"static/{item_id}.png")
    return {"qr_url": f"/static/{item_id}.png"}

# Customer endpoints
@app.post("/customers/", response_model=Customer)
async def add_customer(customer: Customer):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT INTO customers (id, name, email, service_history) VALUES (?, ?, ?, ?)",
              (customer.id, customer.name, customer.email, customer.service_history))
    conn.commit()
    conn.close()
    return customer

@app.get("/customers/", response_model=List[Customer])
async def get_customers():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM customers")
    customers = [Customer(id=row[0], name=row[1], email=row[2], service_history=row[3]) for row in c.fetchall()]
    conn.close()
    return customers

# Ticket endpoints
@app.post("/tickets/", response_model=Ticket)
async def create_ticket(ticket: Ticket):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT INTO tickets (id, customer_id, issue, status) VALUES (?, ?, ?, ?)",
              (ticket.id, ticket.customer_id, ticket.issue, ticket.status))
    conn.commit()
    conn.close()
    return ticket

# Task endpoints
@app.post("/tasks/", response_model=Task)
async def create_task(task: Task):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT INTO tasks (id, description, assigned_to, status) VALUES (?, ?, ?, ?)",
              (task.id, task.description, task.assigned_to, task.status))
    conn.commit()
    conn.close()
    return task

# Email alert
def send_email_alert(item_name: str, quantity: int):
    msg = MIMEText(f"Low stock alert: {item_name} has {quantity} units remaining.")
    msg["Subject"] = "Inventory Alert"
    msg["From"] = "your_email@gmail.com"
    msg["To"] = "admin@yourcompany.com"
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("your_email@gmail.com", "your_app_password")
        server.send_message(msg)

# WebSocket for chat
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except Exception:
        await websocket.close()

# Streamlit frontend
def run_streamlit():
    import streamlit as st
    st.title("Starlink Reseller App")
    
    # Inventory section
    st.header("Inventory Management")
    item_id = st.text_input("Item ID")
    item_name = st.text_input("Item Name")
    quantity = st.number_input("Quantity", min_value=0)
    min_stock = st.number_input("Minimum Stock", min_value=0)
    if st.button("Add Item"):
        import requests
        requests.post("http://localhost:8000/inventory/", 
                     json={"id": item_id, "name": item_name, "quantity": quantity, "min_stock": min_stock})
        st.success("Item added!")
    
    # Display inventory
    response = requests.get("http://localhost:8000/inventory/")
    items = response.json()
    st.write(pd.DataFrame(items))
    
    # Customer section
    st.header("Customer Profiles")
    cust_id = st.text_input("Customer ID")
    cust_name = st.text_input("Customer Name")
    email = st.text_input("Email")
    history = st.text_area("Service History")
    if st.button("Add Customer"):
        requests.post("http://localhost:8000/customers/", 
                     json={"id": cust_id, "name": cust_name, "email": email, "service_history": history})
        st.success("Customer added!")
    
    # Display customers
    response = requests.get("http://localhost:8000/customers/")
    customers = response.json()
    st.write(pd.DataFrame(customers))

if __name__ == "__main__":
    # Run FastAPI
    uvicorn.run(app, host="0.0.0.0", port=8000)