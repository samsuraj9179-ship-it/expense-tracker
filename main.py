import streamlit as st
import json
import os
from datetime import datetime

EXP_FILE = "expenses.json"
DEBT_FILE = "debts.json"
BUDGET_FILE = "budget.json"

def load_data(filename):
    if not os.path.exists(filename):
        return [] if filename != BUDGET_FILE else {"budget": 5000.0}
    with open(filename, "r") as file:
        return json.load(file)

def save_data(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

st.title("💰 Personal Finance & Debt Tracker")

# Create Tabs for clean navigation
tab1, tab2 = st.tabs(["📊 Expense Tracker", "🤝 Lent & Borrowed"])

# ==================== TAB 1: EXPENSE TRACKER ====================
with tab1:
    expenses = load_data(EXP_FILE)
    budget_data = load_data(BUDGET_FILE)
    
    # --- Sidebar for Expenses & Budget ---
    st.sidebar.header("Monthly Budget Setup")
    monthly_budget = st.sidebar.number_input("Set Monthly Budget (₹)", min_value=0.0, step=500.0, value=float(budget_data.get("budget", 5000.0)))
    
    if st.sidebar.button("Save Budget"):
        save_data(BUDGET_FILE, {"budget": monthly_budget})
        st.sidebar.success("Budget updated!")
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.header("Add New Expense")
    exp_amount = st.sidebar.number_input("Amount (₹)", min_value=0.0, step=10.0, key="exp_amt")
    exp_category = st.sidebar.selectbox("Category", ["Food", "Travel", "Utilities", "Entertainment", "Other"], key="exp_cat")
    exp_desc = st.sidebar.text_input("Description", key="exp_desc")

    if st.sidebar.button("Add Expense"):
        if exp_amount > 0:
            expenses.append({"amount": exp_amount, "category": exp_category, "description": exp_desc})
            save_data(EXP_FILE, expenses)
            st.sidebar.success("Expense added successfully!")
            st.rerun()
        else:
            st.sidebar.error("Please enter a valid amount.")

    # --- Main Page: View Expenses ---
    st.subheader("All Expenses")
    if not expenses:
        st.info("No expenses recorded yet.")
    else:
        for i, exp in enumerate(expenses, 1):
            st.write(f"**{i}. {exp['category']}** - ₹{exp['amount']} *({exp['description']})*")

        # --- Spending Summary & Budget Alert ---
        st.subheader("Spending Summary")
        total = sum(exp["amount"] for exp in expenses)
        
        # Calculate remaining budget / deficit
        remaining = monthly_budget - total
        
        col1, col2 = st.columns(2)
        col1.metric("Total Spending", f"₹{total}")
        col2.metric("Monthly Budget", f"₹{monthly_budget}")

       # Warning, Limit, or Success box based on budget
        if total > monthly_budget:
            excess = total - monthly_budget
            st.error(f"🚨 **Budget Exceeded!** You have gone over your budget by **₹{excess}**.")
        elif total == monthly_budget:
            st.warning(f"⚠️ **At the Limit!** You have exactly reached your monthly budget of **₹{monthly_budget}**.")
        else:
            st.success(f"✅ You are within your budget. Remaining: **₹{remaining}**")
        # Category Breakdown
        category_totals = {}
        for exp in expenses:
            cat = exp["category"]
            amt = exp["amount"]
            category_totals[cat] = category_totals.get(cat, 0) + amt
        
        st.write("### Breakdown by Category")
        for cat, amt in category_totals.items():
            st.write(f"- **{cat}:** ₹{amt}")

        # --- Delete Options ---
        st.divider()
        st.subheader("Manage Expenses")
        expense_options = [f"{i}. {exp['category']} - ₹{exp['amount']} ({exp['description']})" for i, exp in enumerate(expenses, 1)]
        selected_to_delete = st.selectbox("Select an expense to delete", options=["-- Select --"] + expense_options, key="del_exp")
        
        if st.button("Delete Selected Expense"):
            if selected_to_delete != "-- Select --":
                index = int(selected_to_delete.split(".")[0]) - 1
                removed = expenses.pop(index)
                save_data(EXP_FILE, expenses)
                st.success(f"Deleted: {removed['category']} - ₹{removed['amount']}")
                st.rerun()

        if st.button("Delete All Expenses", type="primary", key="clear_exp"):
            expenses.clear()
            save_data(EXP_FILE, expenses)
            st.success("All expenses deleted!")
            st.rerun()

# ==================== TAB 2: LENT & BORROWED ====================
with tab2:
    debts = load_data(DEBT_FILE)

    st.sidebar.header("Add Debt Record")
    debt_type = st.sidebar.selectbox("Type", ["Lent (They owe me)", "Borrowed (I owe them)"])
    person_name = st.sidebar.text_input("Person's Name")
    person_phone = st.sidebar.text_input("Phone Number")
    debt_amount = st.sidebar.number_input("Amount (₹)", min_value=0.0, step=10.0, key="debt_amt")
    debt_date = st.sidebar.date_input("Date", value=datetime.today())
    debt_desc = st.sidebar.text_input("Note / Reason", key="debt_desc")

    if st.sidebar.button("Save Debt Record"):
        if person_name and debt_amount > 0:
            debt_entry = {
                "type": debt_type,
                "name": person_name,
                "phone": person_phone,
                "amount": debt_amount,
                "date": debt_date.strftime("%Y-%m-%d"),
                "description": debt_desc
            }
            debts.append(debt_entry)
            save_data(DEBT_FILE, debts)
            st.sidebar.success("Debt record added successfully!")
            st.rerun()
        else:
            st.sidebar.error("Please enter a name and valid amount.")

    st.subheader("Lent & Borrowed Records")
    if not debts:
        st.info("No debt records found.")
    else:
        total_lent = sum(d["amount"] for d in debts if d["type"] == "Lent (They owe me)")
        total_borrowed = sum(d["amount"] for d in debts if d["type"] == "Borrowed (I owe them)")

        col1, col2 = st.columns(2)
        col1.metric("Total Lent to Others", f"₹{total_lent}")
        col2.metric("Total Borrowed from Others", f"₹{total_borrowed}")

        st.divider()

        for i, d in enumerate(debts, 1):
            badge = "🟢 Lent" if d["type"] == "Lent (They owe me)" else "🔴 Borrowed"
            st.write(f"**{i}. {badge}** | **{d['name']}** (📞 {d['phone']}) - **₹{d['amount']}** on *{d['date']}*")
            if d['description']:
                st.caption(f"Note: {d['description']}")
            st.markdown("---")

        debt_options = [f"{i}. [{d['type']}] {d['name']} - ₹{d['amount']}" for i, d in enumerate(debts, 1)]
        selected_debt_to_delete = st.selectbox("Select a record to settle/delete", options=["-- Select --"] + debt_options, key="del_debt")

        if st.button("Settle / Remove Record"):
            if selected_debt_to_delete != "-- Select --":
                index = int(selected_debt_to_delete.split(".")[0]) - 1
                removed_debt = debts.pop(index)
                save_data(DEBT_FILE, debts)
                st.success(f"Settled record for {removed_debt['name']}!")
                st.rerun()