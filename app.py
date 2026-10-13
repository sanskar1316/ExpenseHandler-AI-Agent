import json
from pathlib import Path
from datetime import date, datetime

import pandas as pd
import streamlit as st

DATA_FILE = Path("expenses_data.json")
DEFAULT_BUDGET = 10000

st.set_page_config(page_title="ExpenseHandler AI Agent", page_icon="💸", layout="wide")

def load_data():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"transactions": [], "monthly_budget": DEFAULT_BUDGET}
    return {"transactions": [], "monthly_budget": DEFAULT_BUDGET}

def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def suggest_category(description):
    text = description.lower()
    rules = {
        "Food": ["food", "lunch", "dinner", "breakfast", "restaurant", "snack", "tea", "coffee", "grocery"],
        "Travel": ["bus", "train", "taxi", "uber", "ola", "petrol", "fuel", "travel", "metro"],
        "Education": ["college", "book", "course", "exam", "tuition", "education", "stationery"],
        "Bills": ["electricity", "water bill", "internet", "mobile recharge", "phone bill", "rent"],
        "Shopping": ["clothes", "shopping", "shoes", "bag", "amazon", "flipkart"],
        "Health": ["doctor", "medicine", "hospital", "health", "medical"],
        "Entertainment": ["movie", "game", "netflix", "concert", "entertainment"],
        "Income": ["salary", "stipend", "freelance", "income", "refund"]
    }
    for category, words in rules.items():
        if any(word in text for word in words):
            return category
    return "Other"

def month_key(value):
    return str(value)[:7]

data = load_data()
if "transactions" not in data:
    data["transactions"] = []
if "monthly_budget" not in data:
    data["monthly_budget"] = DEFAULT_BUDGET

st.title("💸 ExpenseHandler AI Agent")
st.caption("A beginner-friendly personal expense tracker with automatic category suggestions and budget alerts.")
st.info("Prototype note: this uses transparent keyword rules, not a trained AI model. Use sample data for demos and avoid storing sensitive financial information.")

with st.sidebar:
    st.header("⚙️ Settings")
    budget = st.number_input("Monthly expense budget (₹)", min_value=0.0, value=float(data.get("monthly_budget", DEFAULT_BUDGET)), step=500.0)
    if budget != data.get("monthly_budget", DEFAULT_BUDGET):
        data["monthly_budget"] = budget
        save_data(data)
    st.metric("Monthly budget", f"₹{budget:,.0f}")
    st.divider()
    st.write("**Agent actions**")
    st.write("1. Records a transaction")
    st.write("2. Suggests a category")
    st.write("3. Calculates monthly spending")
    st.write("4. Warns when spending nears the budget")
    st.write("5. Gives simple saving tips")

with st.expander("➕ Add a transaction", expanded=True):
    with st.form("transaction_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        kind = c1.selectbox("Type", ["Expense", "Income"])
        amount = c2.number_input("Amount (₹)", min_value=1.0, step=50.0)
        trans_date = c3.date_input("Date", value=date.today())
        description = st.text_input("Description", placeholder="e.g., college bus pass, lunch, salary")
        suggested = suggest_category(description) if description.strip() else "Other"
        st.caption(f"Suggested category: **{suggested}**")
        category_options = ["Food", "Travel", "Education", "Bills", "Shopping", "Health", "Entertainment", "Income", "Other"]
        default_index = category_options.index(suggested) if suggested in category_options else len(category_options)-1
        category = st.selectbox("Category", category_options, index=default_index)
        submitted = st.form_submit_button("Save transaction", type="primary")
        if submitted:
            if not description.strip():
                st.error("Please enter a description.")
            else:
                data["transactions"].append({
                    "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                    "date": trans_date.isoformat(),
                    "type": kind,
                    "amount": float(amount),
                    "description": description.strip(),
                    "category": category,
                })
                save_data(data)
                st.success("Transaction saved.")
                st.rerun()

df = pd.DataFrame(data["transactions"])
if df.empty:
    st.subheader("📊 Your dashboard")
    st.write("Add your first transaction above to see your spending summary and agent recommendations.")
    st.stop()

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
df["month"] = df["date"].dt.strftime("%Y-%m")
current_month = date.today().strftime("%Y-%m")
month_df = df[df["month"] == current_month]
expenses = month_df[month_df["type"] == "Expense"]
income = month_df[month_df["type"] == "Income"]
total_expenses = float(expenses["amount"].sum())
total_income = float(income["amount"].sum())
remaining = float(data.get("monthly_budget", DEFAULT_BUDGET)) - total_expenses
budget_value = float(data.get("monthly_budget", DEFAULT_BUDGET))
spent_pct = (total_expenses / budget_value * 100) if budget_value > 0 else 0

st.subheader(f"📊 Dashboard — {date.today().strftime('%B %Y')}")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total expenses", f"₹{total_expenses:,.2f}")
m2.metric("Total income", f"₹{total_income:,.2f}")
m3.metric("Budget remaining", f"₹{remaining:,.2f}", delta=f"{spent_pct:.0f}% of budget used")
m4.metric("Transactions this month", int(len(month_df)))
st.progress(min(max(spent_pct / 100, 0.0), 1.0))

st.subheader("🤖 Agent recommendation")
if budget_value <= 0:
    st.warning("Set a monthly budget above ₹0 to enable budget alerts.")
elif total_expenses > budget_value:
    st.error(f"Budget exceeded by ₹{total_expenses - budget_value:,.2f}. Review optional spending and set a daily limit for the rest of the month.")
elif spent_pct >= 80:
    st.warning(f"You have used {spent_pct:.0f}% of your budget. Only ₹{remaining:,.2f} remains; pause non-essential purchases.")
elif spent_pct >= 50:
    st.info(f"You have used {spent_pct:.0f}% of your budget. Check your largest category before making extra purchases.")
else:
    st.success(f"Spending is within the budget ({spent_pct:.0f}% used). Keep recording transactions to maintain an accurate picture.")

if total_income > 0:
    balance = total_income - total_expenses
    if balance < 0:
        st.warning(f"Recorded expenses exceed recorded income by ₹{-balance:,.2f} this month.")
    else:
        st.write(f"Recorded income minus expenses: **₹{balance:,.2f}**")

left, right = st.columns(2)
with left:
    st.subheader("Expenses by category")
    if expenses.empty:
        st.write("No expenses recorded this month.")
    else:
        chart = expenses.groupby("category")["amount"].sum().sort_values(ascending=False)
        st.bar_chart(chart)
        largest_category = chart.idxmax()
        st.write(f"Highest spending category: **{largest_category}** (₹{chart.max():,.2f}).")
with right:
    st.subheader("Monthly trend")
    expense_all = df[df["type"] == "Expense"].copy()
    if expense_all.empty:
        st.write("No expenses recorded yet.")
    else:
        trend = expense_all.groupby("month")["amount"].sum().sort_index()
        st.line_chart(trend)

st.subheader("🧾 Transaction history")
display_df = df.sort_values("date", ascending=False).copy()
display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
display_df = display_df[["date", "type", "description", "category", "amount"]]
st.dataframe(display_df, use_container_width=True, hide_index=True)

csv = display_df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download transactions as CSV", data=csv, file_name="expense_transactions.csv", mime="text/csv")

with st.expander("🗑️ Delete all saved transactions"):
    st.warning("This permanently clears the transactions saved in this app folder.")
    confirm = st.checkbox("I understand and want to delete all transactions")
    if st.button("Delete all transactions", disabled=not confirm):
        data["transactions"] = []
        save_data(data)
        st.rerun()
