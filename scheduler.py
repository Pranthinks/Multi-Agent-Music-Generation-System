import schedule
import time
from datetime import datetime
import os
from dotenv import load_dotenv
from agents.multi_agent_system import LangChainMultiAgentSystem

# Load environment variables
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in .env file!")
    print("Create a .env file with: GOOGLE_API_KEY=your_api_key_here")
    exit(1)

print("API Key loaded successfully\n")

# Initialize the multi-agent system using factory function
agent_system = LangChainMultiAgentSystem(api_key)

def daily_music_generation():
    """Generate music daily"""
    print(f"\n{'='*70}")
    print(f"DAILY MUSIC GENERATION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    try:
        result = agent_system.invoke({
            "input": "Generate an upbeat, energetic track about winning today"
        })
        print(f"\nResult: {result['output']}")

        daily_marketing()
    except Exception as e:
        print(f"Error: {e}")
    
    print(f"{'='*70}\n")

def daily_marketing():
    """Post latest music to social media daily"""
    print(f"\n{'='*70}")
    print(f"DAILY MARKETING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    try:
        result = agent_system.invoke({
            "input": "Post our latest music to social media with an engaging caption"
        })
        print(f"\nResult: {result['output']}")
    except Exception as e:
        print(f"Error: {e}")
    
    print(f"{'='*70}\n")

def monthly_billing():
    """Charge all active customers monthly"""
    print(f"\n{'='*70}")
    print(f"MONTHLY BILLING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    try:
        # First get all customers
        result = agent_system.invoke({
            "input": "List all customers"
        })
        print(f"\nCustomers: {result['output']}\n")
        
        # Then process billing for all customers
        result = agent_system.invoke({
            "input": "Process monthly subscription payment of $1 for all customers"
        })
        print(f"\nBilling Result: {result['output']}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print(f"{'='*70}\n")
def monthly_billing_runner():
    if datetime.now().day == 1:   # run only on 1st of month
        monthly_billing()

# Schedule tasks
schedule.every().day.at("09:00").do(daily_music_generation)  
schedule.every().day.at("00:10").do(monthly_billing_runner)

print("\nSCHEDULER STARTED")
print("="*70)
print("Schedule:")
print("Schedule:")
print("   - Music Generation: Every day at 09:00 AM (Marketing runs after Music)")
print("   - Billing: Runs monthly on the 1st at 00:10 AM")

# Run scheduler
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\n\nScheduler stopped by user")
    print(f"Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)