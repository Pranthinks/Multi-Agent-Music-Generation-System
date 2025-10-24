"""
Billing and subscription management tools for the Billing Agent
"""
from langchain_core.tools import tool
from datetime import datetime
from utils.database import load_database, save_database


@tool
def process_payment(amount: float, customer_name: str) -> str:
    """Processes monthly payment and updates customer database.
    
    Args:
        amount: Payment amount (must be 1.0 for $1/month subscription)
        customer_name: Full name of the customer
    
    Returns:
        Payment confirmation with details
    """
    print("Processing payment...")
    
    if amount != 1.0:
        return f"Invalid amount. Subscription is $1/month (received: ${amount})"
    
    db = load_database()
    now = datetime.now()
    payment_id = f"PAY_{now.strftime('%Y%m%d%H%M%S')}"
    
    if customer_name not in db["customers"]:
        db["customers"][customer_name] = {
            "status": "active",
            "payments": [],
            "created_at": now.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    db["customers"][customer_name]["payments"].append({
        "amount": amount,
        "payment_id": payment_id,
        "timestamp": now.strftime('%Y-%m-%d %H:%M:%S')
    })
    db["customers"][customer_name]["status"] = "active"
    db["customers"][customer_name]["last_payment"] = now.strftime('%Y-%m-%d %H:%M:%S')
    
    save_database(db)
    
    return f"Payment processed for {customer_name}!\n- Amount: ${amount}\n- Payment ID: {payment_id}\n- Status: Active"


@tool
def check_subscription_status(customer_name: str) -> str:
    """Checks real subscription status from database.
    
    Args:
        customer_name: Full name of the customer
    
    Returns:
        Subscription status details
    """
    print("Checking subscription...")
    
    db = load_database()
    
    if customer_name not in db["customers"]:
        return f"Customer '{customer_name}' not found in system.\nPlease process payment first to activate subscription."
    
    customer = db["customers"][customer_name]
    status = customer.get("status", "inactive")
    payment_count = len(customer.get("payments", []))
    last_payment = customer.get("last_payment", "Never")
    
    if status == "active":
        return f"{customer_name}: Active subscription\n- Plan: $1/month\n- Total payments: {payment_count}\n- Last payment: {last_payment}"
    else:
        return f"{customer_name}: Inactive subscription\n- Total payments: {payment_count}\n- Status: Payment required"


@tool
def list_all_customers() -> str:
    """Lists all customers in the database with their status.
    
    Returns:
        List of all customers and their subscription status
    """
    print("Listing all customers...")
    
    db = load_database()
    customers = db.get("customers", {})
    
    if not customers:
        return "No customers found in the system."
    
    result = f"Total Customers: {len(customers)}\n\n"
    for name, data in customers.items():
        status = data.get("status", "inactive")
        payments = len(data.get("payments", []))
        last_payment = data.get("last_payment", "Never")
        result += f"{name}\n   Status: {status}\n   Payments: {payments}\n   Last Payment: {last_payment}\n\n"
    
    return result