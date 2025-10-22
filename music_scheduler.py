import schedule
import time
from agent import create_music_company_agent, load_database, save_database
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in .env file!")
    print("Create a .env file in the same directory with:")
    print("   GOOGLE_API_KEY=your_api_key_here")
    exit(1)

print("API Key loaded successfully from .env")

agent = create_music_company_agent(api_key)

def daily_music_generation():
    """Generate music daily based on user prompt"""
    print(f"\n{'='*70}")
    print(f"DAILY MUSIC GENERATION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    try:
        result = agent.invoke({
            "input": "Generate an upbeat, energetic track about winning today"
        })
        print(f"\nResult: {result['output']}")
    except Exception as e:
        print(f"Error in music generation: {e}")
    
    print(f"{'='*70}")
    print("MUSIC GENERATION COMPLETED")
    print(f"{'='*70}\n")

def daily_marketing():
    """Post the latest music to social media daily"""
    print(f"\n{'='*70}")
    print(f"DAILY MARKETING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    try:
        result = agent.invoke({
            "input": "Post our latest music to social media with an engaging caption"
        })
        print(f"\nResult: {result['output']}")
    except Exception as e:
        print(f"Error in marketing: {e}")
    
    print(f"{'='*70}")
    print("MARKETING COMPLETED")
    print(f"{'='*70}\n")

def monthly_billing():
    """Charge all active customers monthly subscription"""
    print(f"\n{'='*70}")
    print(f"MONTHLY BILLING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    try:
        # Load customer database
        db = load_database()
        customers = db.get("customers", {})
        
        if not customers:
            print("No customers found in database")
            print(f"{'='*70}\n")
            return
        
        print(f"Found {len(customers)} customers in database\n")
        
        # Charge each customer
        charged_count = 0
        failed_count = 0
        
        for customer_name, customer_data in customers.items():
            try:
                print(f"💳 Charging {customer_name}...")
                result = agent.invoke({
                    "input": f"Process a $1 monthly payment for customer {customer_name}"
                })
                print(f"{customer_name}: Success")
                charged_count += 1
            except Exception as e:
                print(f"{customer_name}: Failed - {e}")
                failed_count += 1
        
        print(f"\nBilling Summary:")
        print(f"Successfully charged: {charged_count}")
        print(f"Failed: {failed_count}")
        
    except Exception as e:
        print(f"Error in monthly billing: {e}")
    
    print(f"{'='*70}")
    print("MONTHLY BILLING COMPLETED")
    print(f"{'='*70}\n")

print("TEST MODE ENABLED")
print("   - Daily task: Every 10 seconds")
print("   - Monthly billing: Every 30 seconds")
#schedule.every(3).seconds.do(daily_music_generation)
#schedule.every(10).seconds.do(daily_marketing)  # 10 seconds after music
schedule.every(10).seconds.do(monthly_billing)

print(f"\n{'='*70}")
print("SCHEDULER STARTED")
print(f"{'='*70}")
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Press Ctrl+C to stop")
print(f"{'='*70}\n")

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\nScheduler stopped by user")
    print(f"Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")