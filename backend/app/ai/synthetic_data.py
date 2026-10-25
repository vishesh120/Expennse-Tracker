import random
import hashlib
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

INDIAN_MERCHANTS_DATA = [
    # Food & Groceries
    {"title": "Swiggy Order - Dinner Bowl", "category": "Food and groceries", "min": 250, "max": 750, "method": "UPI", "upi_prefix": "swiggy@icici"},
    {"title": "Zomato - Hyderabadi Biryani", "category": "Food and groceries", "min": 320, "max": 650, "method": "UPI", "upi_prefix": "zomato@hdfcbank"},
    {"title": "Blinkit - Daily Milk & Veggies", "category": "Food and groceries", "min": 180, "max": 540, "method": "UPI", "upi_prefix": "blinkit@yesbank"},
    {"title": "Zepto - Grocery Quick Delivery", "category": "Food and groceries", "min": 140, "max": 420, "method": "UPI", "upi_prefix": "zepto@icici"},
    {"title": "Starbucks - Iced Caramel Macchiato", "category": "Food and groceries", "min": 380, "max": 520, "method": "Debit Card", "upi_prefix": None},
    {"title": "Local Chai Tapri & Snacks", "category": "Food and groceries", "min": 40, "max": 120, "method": "UPI", "upi_prefix": "ramu.chai@okaxis"},
    {"title": "DMart Supermarket Monthly Restock", "category": "Food and groceries", "min": 2200, "max": 4800, "method": "UPI", "upi_prefix": "dmart@pos"},

    # Transportation
    {"title": "Uber Auto - Tech Park Commute", "category": "Transportation", "min": 110, "max": 240, "method": "UPI", "upi_prefix": "uber.india@hdfcbank"},
    {"title": "Ola Cab - Airport Drop", "category": "Transportation", "min": 650, "max": 1150, "method": "UPI", "upi_prefix": "olacabs@axisbank"},
    {"title": "Rapido Bike - Quick Commute", "category": "Transportation", "min": 50, "max": 120, "method": "UPI", "upi_prefix": "rapido@paytm"},
    {"title": "HPCL Petrol Fuel Station Refill", "category": "Transportation", "min": 800, "max": 2000, "method": "UPI", "upi_prefix": "hpcl.bunk@sbi"},
    {"title": "Metro Smart Card Online Recharge", "category": "Transportation", "min": 200, "max": 500, "method": "UPI", "upi_prefix": "dmrc@axisbank"},
    {"title": "IRCTC Train Ticket Reservation", "category": "Transportation", "min": 620, "max": 1450, "method": "Net Banking", "upi_prefix": None},

    # Shopping
    {"title": "Amazon.in - Noise Wireless Earbuds", "category": "Shopping", "min": 1499, "max": 2999, "method": "UPI", "upi_prefix": "amazonpay@apl"},
    {"title": "Myntra - Roadster Denim Jeans", "category": "Shopping", "min": 899, "max": 1899, "method": "Credit Card", "upi_prefix": None},
    {"title": "Flipkart - Ergonomic Mouse", "category": "Shopping", "min": 499, "max": 1200, "method": "UPI", "upi_prefix": "flipkart@axisbank"},

    # Bills & Utilities
    {"title": "Airtel Prepaid 5G Plan 84 Days", "category": "Bills and utilities", "min": 719, "max": 999, "method": "UPI", "upi_prefix": "airtelprepaid@airtel"},
    {"title": "Electricity Bill Payment (BESCOM)", "category": "Bills and utilities", "min": 950, "max": 1850, "method": "UPI", "upi_prefix": "bescom@karnataka"},
    {"title": "ACT Fibernet Broadband 100 Mbps", "category": "Bills and utilities", "min": 825, "max": 1150, "method": "UPI", "upi_prefix": "actcorp@hdfcbank"},

    # Healthcare
    {"title": "Apollo Pharmacy - Prescribed Medicines", "category": "Healthcare", "min": 350, "max": 950, "method": "UPI", "upi_prefix": "apollopharmacy@icici"},
    {"title": "Practo Clinic - General Physician Fee", "category": "Healthcare", "min": 500, "max": 900, "method": "UPI", "upi_prefix": "practo@doctor"},

    # Entertainment
    {"title": "BookMyShow - PVR IMAX Movie Tickets", "category": "Entertainment", "min": 450, "max": 950, "method": "UPI", "upi_prefix": "bookmyshow@icici"},
    {"title": "Netflix Monthly Subscription", "category": "Entertainment", "min": 499, "max": 649, "method": "Credit Card", "upi_prefix": None, "recurring": True},
    {"title": "Spotify Premium Individual Plan", "category": "Entertainment", "min": 119, "max": 119, "method": "UPI", "upi_prefix": "spotify@yesbank", "recurring": True},

    # Education
    {"title": "Udemy Course - FastApi & AI Specialization", "category": "Education", "min": 499, "max": 899, "method": "UPI", "upi_prefix": "udemy@hdfcbank"},
    {"title": "Technical Books & Notebooks", "category": "Education", "min": 350, "max": 750, "method": "Cash", "upi_prefix": None},
]


def generate_sample_transactions(user_id: str, days: int = 45) -> List[Dict[str, Any]]:
    """
    Generate synthetic transactions spanning the past N days.
    """
    transactions = []
    base_date = datetime.now(timezone.utc).date()

    # Recurring Salary credit on 1st of each month
    # We'll insert salary for 2 months
    salary_dates = [
        (base_date - timedelta(days=base_date.day - 1)),  # 1st of current month
        ((base_date - timedelta(days=base_date.day + 1)).replace(day=1))  # 1st of prev month
    ]
    for sal_date in salary_dates:
        h = hashlib.md5(f"{sal_date}-65000-Monthly Salary Credit-Net Banking".encode()).hexdigest()
        transactions.append({
            "title": "Monthly Salary Credit - Tech Corp India",
            "amount": 65000.0,
            "type": "income",
            "date": sal_date.strftime("%Y-%m-%d"),
            "category": "Salary and income",
            "payment_method": "Net Banking",
            "upi_reference": f"NEFT-SAL-{random.randint(10000000, 99999999)}",
            "description": "Direct bank deposit of monthly salary",
            "is_recurring": True,
            "recurring_frequency": "monthly",
            "ai_suggested_category": "Salary and income",
            "ai_confidence": 0.98,
            "is_user_confirmed": True,
            "import_hash": h
        })

    # Recurring Rent payment on 3rd of each month
    for sal_date in salary_dates:
        rent_date = sal_date + timedelta(days=2)
        h = hashlib.md5(f"{rent_date}-16500-Flat Rent Transfer-UPI".encode()).hexdigest()
        transactions.append({
            "title": "House Rent to Landlord (2BHK Share)",
            "amount": 16500.0,
            "type": "expense",
            "date": rent_date.strftime("%Y-%m-%d"),
            "category": "Rent and housing",
            "payment_method": "UPI",
            "upi_reference": f"{random.randint(400000000000, 499999999999)}",
            "description": "Monthly rent payment via UPI",
            "is_recurring": True,
            "recurring_frequency": "monthly",
            "ai_suggested_category": "Rent and housing",
            "ai_confidence": 0.96,
            "is_user_confirmed": True,
            "import_hash": h
        })

    # Monthly SIP investments on 5th of each month
    for sal_date in salary_dates:
        sip_date = sal_date + timedelta(days=4)
        h = hashlib.md5(f"{sip_date}-5000-Nifty 50 Index Fund SIP-UPI".encode()).hexdigest()
        transactions.append({
            "title": "Groww - Nifty 50 Index Mutual Fund SIP",
            "amount": 5000.0,
            "type": "expense",
            "date": sip_date.strftime("%Y-%m-%d"),
            "category": "Investments and savings",
            "payment_method": "UPI",
            "upi_reference": f"{random.randint(400000000000, 499999999999)}",
            "description": "Automated monthly index fund investment",
            "is_recurring": True,
            "recurring_frequency": "monthly",
            "ai_suggested_category": "Investments and savings",
            "ai_confidence": 0.97,
            "is_user_confirmed": True,
            "import_hash": h
        })

    # Generate daily expenses
    for day_offset in range(days, 0, -1):
        txn_date = base_date - timedelta(days=day_offset)
        # 1 to 4 transactions per day
        num_txns = random.randint(1, 3) if txn_date.weekday() < 5 else random.randint(2, 4)

        for _ in range(num_txns):
            template = random.choice(INDIAN_MERCHANTS_DATA)
            amt = round(random.uniform(template["min"], template["max"]), 2)
            method = template["method"]
            ref = None
            if method == "UPI":
                ref = f"{random.randint(400000000000, 499999999999)}"

            title = template["title"]
            h = hashlib.md5(f"{txn_date}-{amt}-{title}-{method}".encode()).hexdigest()

            transactions.append({
                "title": title,
                "amount": amt,
                "type": "expense",
                "date": txn_date.strftime("%Y-%m-%d"),
                "category": template["category"],
                "payment_method": method,
                "upi_reference": ref,
                "description": f"Paid via {method}" + (f" ({ref})" if ref else ""),
                "is_recurring": template.get("recurring", False),
                "recurring_frequency": "monthly" if template.get("recurring") else None,
                "ai_suggested_category": template["category"],
                "ai_confidence": round(random.uniform(0.88, 0.99), 2),
                "is_user_confirmed": True,
                "import_hash": h
            })

    # Sort transactions by date descending
    transactions.sort(key=lambda x: x["date"], reverse=True)
    return transactions
