import json
from pathlib import Path
from datetime import date, datetime

import pandas as pd
import streamlit as st

DATA_FILE = Path("expenses_data.json")
DEFAULT_BUDGET = 10000
CATEGORIES = ["Food", "Travel", "Education", "Bills", "Shopping", "Health", "Entertainment", "Income", "Other"]

st.set_page_config(
    page_title="ExpenseFlow | Personal Finance",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --ink:#172033; --muted:#748096; --brand:#6558f5; --mint:#dff8ee; }
html, body, [class*="css"] { font-family:'DM Sans', sans-serif; }
.stApp { background: linear-gradient(135deg,#f7f8ff 0%,#f6fbff 55%,#f7fffb 100%); color:var(--ink); }
.block-container { padding-top:1.6rem; padding-bottom:3rem; max-width:1450px; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#171b35 0%,#25264c 100%); }
[data-testid="stSidebar"] * { color:#f4f5ff !important; }
[data-testid="stSidebar"] [data-testid="stNumberInput"] input { color:#172033 !important; background:#fff !important; }
[data-testid="stSidebar"] hr { border-color:#45466b; }
.hero { padding:1.55rem 1.8rem; border-radius:24px; color:white;
        background:linear-gradient(120deg,#6157ed 0%,#8475ff 55%,#58c9b2 130%);
        box-shadow:0 14px 36px rgba(88,83,220,.18); margin-bottom:1.25rem; }
.hero h1 { font-family:'Manrope',sans-serif; font-size:2.15rem; font-weight:800; margin:0; letter-spacing:-1px; color:white; }
.hero p { margin:.45rem 0 0; color:#eeedff; font-size:1rem; }
.eyebrow { text-transform:uppercase; letter-spacing:1.7px; font-size:.72rem; font-weight:700; opacity:.82; margin-bottom:.45rem; }
.section-title { font-family:'Manrope',sans-serif; font-size:1.18rem; font-weight:800; color:#1b2340; margin:.6rem 0 .8rem; }
.metric-card { background:rgba(255,255,255,.92); border:1px solid #e8eaf5; border-radius:18px;
               padding:1.1rem 1.15rem; box-shadow:0 5px 18px rgba(35,43,87,.045); min-height:126px; }
.metric-label { color:#778199; font-size:.82rem; font-weight:600; }
.metric-value { font-family:'Manrope',sans-serif; color:#202744; font-size:1.7rem; font-weight:800; margin:.35rem 0 .2rem; }
.metric-note { color:#8a93a8; font-size:.78rem; }
.panel { background:rgba(255,255,255,.88); border:1px solid #e8eaf5; border-radius:20px; padding:1.15rem 1.25rem; box-shadow:0 5px 18px rgba(35,43,87,.04); }
div[data-testid="stForm"], div[data-testid="stExpander"] { background:rgba(255,255,255,.9); border:1px solid #e8eaf5; border-radius:18px; }
div[data-testid="stForm"] { padding:1.1rem 1.2rem; }
.stButton button, .stDownloadButton button, button[kind="primary"], [data-testid="stFormSubmitButton"] button {
 border-radius:12px !important; font-weight:700 !important; min-height:2.7rem; }
.stButton button[kind="primary"], [data-testid="stFormSubmitButton"] button { background:linear-gradient(90deg,#6558f5,#8175ff) !important; border:0 !important; }
div[data-testid="stMetric"] { background:white; border:1px solid #e8eaf5; padding:1rem; border-radius:16px; }
.stProgress > div > div > div > div { background:linear-gradient(90deg,#6558f5,#58c9b2); }
[data-testid="stDataFrame"] { border:1px solid #e8eaf5; border-radius:14px; overflow:hidden; }
div[data-testid="stAlert"] { border-radius:14px; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

def load_data():
    if DATA_FILE.exists():
        try:
            value = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            if isinstance(value, dict):
                return value
        except (json.JSONDecodeError, OSError):
            pass
    return {"transactions": [], "monthly_budget": DEFAULT_BUDGET}

def save_data(value):
    DATA_FILE.write_text(json.dumps(value, indent=2), encoding="utf-8")

def suggest_category(description):
    text = description.lower()
    rules = {
        "Food": ["food", "lunch", "dinner", "breakfast", "restaurant", "snack", "tea", "coffee", "grocery"],
        "Travel": ["bus", "train", "taxi", "uber", "ola", "petrol", "fuel", "travel", "metro", "rickshaw"],
        "Education": ["college", "book", "course", "exam", "tuition", "education", "stationery", "fees"],
        "Bills": ["electricity", "water bill", "internet", "mobile recharge", "phone bill", "rent"],
        "Shopping": ["clothes", "shopping", "shoes", "bag", "amazon", "flipkart"],
        "Health": ["doctor", "medicine", "hospital", "health", "medical"],
        "Entertainment": ["movie", "game", "netflix", "concert", "entertainment"],
        "Income": ["salary", "stipend", "freelance", "income", "refund"],
    }
    for category, words in rules.items():
        if any(word in text for word in words):
            return category
    return "Other"

def money(value):
    return f"₹{value:,.0f}"

def metric_card(label, value, note, emoji):
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{emoji} &nbsp;{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
        unsafe_allow_html=True,
    )

data = load_data()
data.setdefault("transactions", [])
data.setdefault("monthly_budget", DEFAULT_BUDGET)

with st.sidebar:
    st.markdown("## 💸 ExpenseFlow")
    st.caption("PERSONAL FINANCE SPACE")
    st.divider()
    st.markdown("### ⚙️ Budget settings")
    budget = st.number_input(
        "Monthly expense budget (₹)", min_value=0.0,
        value=float(data.get("monthly_budget", DEFAULT_BUDGET)), step=500.0,
        help="Your monthly spending target."
    )
    if budget != data.get("monthly_budget", DEFAULT_BUDGET):
        data["monthly_budget"] = budget
        save_data(data)
    st.markdown("---")
    st.markdown("### ✨ Your finance assistant")
    st.markdown("- Tracks income and expenses\n- Suggests spending categories\n- Monitors your monthly budget\n- Highlights spending patterns")
    st.markdown("---")
    st.caption("ExpenseFlow · Simple money habits, clearer decisions")

st.markdown("""
<div class="hero">
  <div class="eyebrow">YOUR MONEY, MADE CLEAR</div>
  <h1>Welcome to ExpenseFlow ✨</h1>
  <p>A calmer way to track spending, understand your habits, and stay on budget.</p>
</div>
""", unsafe_allow_html=True)

# Add transaction area
st.markdown('<div class="section-title">＋ Add a transaction</div>', unsafe_allow_html=True)
with st.form("transaction_form", clear_on_submit=True):
    c1, c2, c3 = st.columns([1, 1, 1])
    kind = c1.selectbox("Transaction type", ["Expense", "Income"])
    amount = c2.number_input("Amount (₹)", min_value=1.0, value=100.0, step=50.0)
    trans_date = c3.date_input("Date", value=date.today())
    description = st.text_input("Description", placeholder="e.g. lunch, college bus pass, monthly salary")
    suggested = suggest_category(description) if description.strip() else "Other"
    c4, c5 = st.columns([1, 2])
    category = c4.selectbox("Category", CATEGORIES, index=CATEGORIES.index(suggested))
    c5.markdown(
        f'<div style="padding:.65rem .9rem;margin-top:1.8rem;border-radius:12px;'
        f'background:#f1f0ff;color:#5146c9;font-size:.9rem;">✨ Suggested category: <b>{suggested}</b></div>',
        unsafe_allow_html=True
    )
    submitted = st.form_submit_button("Save transaction  →", type="primary", use_container_width=True)
    if submitted:
        if not description.strip():
            st.error("Please enter a short description.")
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
            st.success("Transaction saved successfully.")
            st.rerun()

df = pd.DataFrame(data["transactions"])
if not df.empty:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df["month"] = df["date"].dt.strftime("%Y-%m")
else:
    df = pd.DataFrame(columns=["date", "type", "amount", "description", "category", "month"])

today = date.today()
current_month = today.strftime("%Y-%m")
month_df = df[df["month"] == current_month] if not df.empty else df
expenses = month_df[month_df["type"] == "Expense"] if not month_df.empty else month_df
income = month_df[month_df["type"] == "Income"] if not month_df.empty else month_df
total_expenses = float(expenses["amount"].sum()) if not expenses.empty else 0.0
total_income = float(income["amount"].sum()) if not income.empty else 0.0
budget_value = float(data.get("monthly_budget", DEFAULT_BUDGET))
remaining = budget_value - total_expenses
spent_pct = (total_expenses / budget_value * 100) if budget_value > 0 else 0.0

st.markdown(f'<div class="section-title">📊 Your overview <span style="color:#8992a8;font-size:.85rem;font-weight:500;">· {today.strftime("%B %Y")}</span></div>', unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4, gap="medium")
with k1: metric_card("Total expenses", money(total_expenses), "Spent this month", "↗️")
with k2: metric_card("Total income", money(total_income), "Received this month", "💰")
with k3: metric_card("Budget remaining", money(remaining), "Available this month", "🎯")
with k4: metric_card("Transactions", f"{len(month_df):,}", "This month", "🧾")

st.markdown("")
st.markdown('<div class="section-title">🎯 Budget health</div>', unsafe_allow_html=True)
if budget_value <= 0:
    st.warning("Set your monthly budget above ₹0 in the sidebar to enable budget tracking.")
else:
    st.progress(min(max(spent_pct / 100, 0.0), 1.0), text=f"{spent_pct:.0f}% of monthly budget used")
    if total_expenses > budget_value:
        st.error(f"Budget exceeded by {money(total_expenses - budget_value)}. Review optional spending for the rest of the month.")
    elif spent_pct >= 80:
        st.warning(f"You have used {spent_pct:.0f}% of your budget. {money(remaining)} remains, so consider pausing non-essential purchases.")
    elif spent_pct >= 50:
        st.info(f"You have used {spent_pct:.0f}% of your budget. Check your largest spending category before making extra purchases.")
    else:
        st.success(f"You're within budget — {money(max(remaining, 0))} remains. Keep recording transactions to see your habits clearly.")

if total_income > 0:
    balance = total_income - total_expenses
    st.caption(f"💡 This month's recorded balance: **{money(balance)}** (income minus expenses).")

st.markdown('<div class="section-title">📈 Spending insights</div>', unsafe_allow_html=True)
left, right = st.columns(2, gap="large")
with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("**Expenses by category**")
    if expenses.empty:
        st.caption("Your category chart will appear here after you add an expense.")
    else:
        chart = expenses.groupby("category")["amount"].sum().sort_values(ascending=False)
        st.bar_chart(chart, color="#7568f5")
        st.caption(f"Top category: **{chart.idxmax()}** · {money(float(chart.max()))}")
    st.markdown('</div>', unsafe_allow_html=True)
with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("**Monthly spending trend**")
    expense_all = df[df["type"] == "Expense"].copy() if not df.empty else df
    if expense_all.empty:
        st.caption("Your spending trend will appear here as you record expenses.")
    else:
        trend = expense_all.groupby("month")["amount"].sum().sort_index()
        st.line_chart(trend, color="#36b99a")
        st.caption("Compare your total expenses across recorded months.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">🧾 Transaction history</div>', unsafe_allow_html=True)
if df.empty:
    st.markdown("""
    <div class="panel" style="text-align:center;padding:2rem;">
      <div style="font-size:2rem;">🌱</div>
      <h3 style="margin:.4rem 0;color:#202744;">Your money story starts here</h3>
      <p style="color:#7a849b;">Add your first transaction above to see your dashboard and spending insights.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    search = st.text_input("🔎 Search transactions", placeholder="Search description or category…")
    display_df = df.copy()
    if search.strip():
        mask = (
            display_df["description"].astype(str).str.contains(search, case=False, na=False)
            | display_df["category"].astype(str).str.contains(search, case=False, na=False)
            | display_df["type"].astype(str).str.contains(search, case=False, na=False)
        )
        display_df = display_df[mask]
    display_df = display_df.sort_values("date", ascending=False).copy()
    display_df["date"] = display_df["date"].dt.strftime("%d %b %Y")
    display_df["amount"] = display_df["amount"].map(lambda x: f"₹{x:,.2f}")
    display_df = display_df[["date", "type", "description", "category", "amount"]]
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=320)
    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export transactions as CSV", data=csv, file_name="expense_transactions.csv", mime="text/csv")

with st.expander("🗑️ Manage saved transactions"):
    st.caption("Use this only if you want to clear the transaction history stored by this app.")
    confirm = st.checkbox("I understand that deleting transactions cannot be undone")
    if st.button("Delete all transactions", disabled=not confirm):
        data["transactions"] = []
        save_data(data)
        st.rerun()

st.markdown("""
<div style="text-align:center;color:#9aa2b5;font-size:.78rem;padding:2rem 0 .4rem;">
  ExpenseFlow · Build better money habits, one entry at a time
</div>
""", unsafe_allow_html=True)
