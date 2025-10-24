"""
Database utilities for customer management
"""
import json
import os

DB_FILE = "customer_database.json"


def load_database():
    """Load customer database from file"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {"customers": {}}


def save_database(db):
    """Save customer database to file"""
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)