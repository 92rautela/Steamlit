import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import tempfile

# Set page config
st.set_page_config(page_title="Budget Tracker", page_icon="💰", layout="centered")
# ✅ Custom CSS
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.main-container {
    max-width: 400px;
    margin: 20px auto;
    padding: 0;
}

.header-box {
    background: linear-gradient(135deg, #8B5CF6, #A855F7);
    color: white;
    padding: 15px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 20px;
    font-weight: bold;
}

.income-expense-container {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.income-box {
    background: linear-gradient(135deg, #10B981, #059669);
    color: white;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    flex: 1;
    font-weight: bold;
}

.total-amount-box {
    background: linear-gradient(135deg, #EF4444, #DC2626);
    color: white;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    flex: 1;
    font-weight: bold;
}

.box-title {
    font-size: 12px;
    opacity: 0.9;
    margin-bottom: 5px;
}

.box-value {
    font-size: 18px;
    font-weight: bold;
}

/* Income input box green */
div[data-baseweb="input"] input {
    background-color: #ECFDF5 !important;
    color: #065F46 !important;
    font-weight: bold;
    border-radius: 8px;
    border: 1px solid #10B981 !important;
}
.stNumberInput > div > div > input,
.stTextInput > div > div > input,
.stDateInput > div > div > input {
    border: 1px solid #D1D5DB;
    border-radius: 8px;
    padding: 12px;
    font-size: 16px;

/* Submit button gray */
.stForm button {
    background-color: #9CA3AF !important;
    color: white !important;
    font-weight: bold;
    border-radius: 8px;
}
.stForm button:hover {
    background-color: #6B7280 !important;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# ✅ File Path
# ----------------------------
PERSISTENT_FILE = os.path.join(tempfile.gettempdir(), "budget_tracker_expenses.csv")
INCOME_FILE = os.path.join(tempfile.gettempdir(), "budget_tracker_income.csv")

# ----------------------------
# ✅ Load and Save Functions
# ----------------------------
def load_expenses():
    if os.path.exists(PERSISTENT_FILE):
        try:
            df = pd.read_csv(PERSISTENT_FILE)
            if not df.empty and 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date']).dt.date
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
    return pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note'])

def load_income():
    if os.path.exists(INCOME_FILE):
        try:
            df = pd.read_csv(INCOME_FILE)
            return df['Income'].iloc[0] if not df.empty else 0.0
        except Exception as e:
            st.error(f"Error loading income: {e}")
    return 0.0

def save_to_csv(df):
    try:
        os.makedirs(os.path.dirname(PERSISTENT_FILE), exist_ok=True)
        df.to_csv(PERSISTENT_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving: {e}")
        return False

def save_income(income):
    try:
        os.makedirs(os.path.dirname(INCOME_FILE), exist_ok=True)
        income_df = pd.DataFrame({'Income': [income]})
        income_df.to_csv(INCOME_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving income: {e}")
        return False

# ----------------------------
# ✅ Session State Initialization
# ----------------------------
if 'expenses_df' not in st.session_state:
    st.session_state.expenses_df = load_expenses()

if 'income' not in st.session_state:
    st.session_state.income = load_income()

if 'last_refresh' not in st.session_state or st.session_state.get('force_refresh', False):
    st.session_state.expenses_df = load_expenses()
    st.session_state.income = load_income()
    st.session_state.last_refresh = datetime.now()
    st.session_state.force_refresh = False

# ----------------------------
# ✅ Header
# ----------------------------
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown("""
<div class="header-box">
    💰 Personal Budget Tracker 💰 
</div>
""", unsafe_allow_html=True)

# ----------------------------
# ✅ Income + Expenses Display
# ----------------------------
# Calculate total expenses
total_expenses = 0.0
if not st.session_state.expenses_df.empty and 'Price' in st.session_state.expenses_df.columns:
    price_values = pd.to_numeric(st.session_state.expenses_df['Price'], errors='coerce').fillna(0)
    total_expenses = price_values.sum()

# Editable Income Box (Green Box)
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="income-box">
        <div class="box-title">💚 INCOME</div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.income = st.number_input(
        "Edit Income",
        value=float(st.session_state.income),
        min_value=0.0,
        step=100.0,
        label_visibility="collapsed"
    )
    save_income(st.session_state.income)

with col2:
    st.markdown(f"""
    <div class="total-amount-box">
        <div class="box-title">❤️ TOTAL EXPENSES</div>
        <div class="box-value">₹{total_expenses:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

# Remaining balance
remaining = st.session_state.income - total_expenses
balance_color = "green" if remaining >= 0 else "red"
balance_icon = "✅" if remaining >= 0 else "⚠️"

st.markdown(f"""
<div style="text-align: center; padding: 10px; background-color: #F3F4F6; border-radius: 8px; margin: 10px 0;">
    <span style="color: {balance_color}; font-weight: bold; font-size: 16px;">
        {balance_icon} Remaining Balance: ₹{remaining:,.2f}
    </span>
</div>
""", unsafe_allow_html=True)

# ----------------------------
# ✅ Add Expense Form
# ----------------------------
st.markdown("### 💸 Add New Expense")

with st.form("expense_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        expense_date = st.date_input("", value=date.today(), label_visibility="collapsed")
        expense_item = st.text_input("", placeholder="e.g., Milk, Groceries", label_visibility="collapsed")
        if expense_item:
            expense_item = expense_item.title()

    with col2:
        expense_price = st.number_input("", min_value=0.0, step=1.0, format="%.2f", label_visibility="collapsed")
        expense_note = st.text_input("", placeholder="Additional details", label_visibility="collapsed")

    submitted = st.form_submit_button("Submit", use_container_width=True)

    if submitted:
        if expense_item.strip() and expense_price > 0:
            new_expense = pd.DataFrame({
                'Date': [expense_date],
                'Item': [expense_item.strip().title()],
                'Price': [float(expense_price)],
                'Note': [expense_note.strip() if expense_note.strip() else "N/A"]
            })
            st.session_state.expenses_df = pd.concat([st.session_state.expenses_df, new_expense], ignore_index=True)
            if save_to_csv(st.session_state.expenses_df):
                st.success("✅ Expense added and saved!")
                st.session_state.force_refresh = True
                st.rerun()

# ----------------------------
# ✅ Editable Expenses
# ----------------------------
if not st.session_state.expenses_df.empty:
    st.markdown("### ✏️ Edit Expenses")

    editable_df = st.session_state.expenses_df.copy()
    editable_df["Date"] = pd.to_datetime(editable_df["Date"], errors="coerce").dt.date
    editable_df["Price"] = pd.to_numeric(editable_df["Price"], errors="coerce").fillna(0.0)
    editable_df["Item"] = editable_df["Item"].astype(str)
    editable_df["Note"] = editable_df["Note"].astype(str)

    updated_df = st.data_editor(
        editable_df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "Date": st.column_config.DateColumn("📅 Date"),
            "Item": st.column_config.TextColumn("📝 Item"),
            "Price": st.column_config.NumberColumn("💰 Price", format="₹%.2f"),
            "Note": st.column_config.TextColumn("📋 Note")
        }
    )

    st.session_state.expenses_df = updated_df
    save_to_csv(st.session_state.expenses_df)

    # Clear all data button
    if st.button("🗑️ Clear All Data", use_container_width=True):
        st.session_state.expenses_df = pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note'])
        st.session_state.income = 0.0
        try:
            if os.path.exists(PERSISTENT_FILE):
                os.remove(PERSISTENT_FILE)
            if os.path.exists(INCOME_FILE):
                os.remove(INCOME_FILE)
            st.success("✅ All data cleared!")
            st.rerun()
        except Exception as e:
            st.error(f"Error clearing data: {e}")
else:
    st.info("📝 No expenses found. Add your first expense above!")

