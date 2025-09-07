import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import tempfile
import io

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

.info-box {
    background: #FEF3C7;
    border: 1px solid #F59E0B;
    color: #92400E;
    padding: 10px;
    border-radius: 8px;
    margin: 10px 0;
    font-size: 14px;
}

.section-header {
    color: #4B5563;
    font-size: 16px;
    font-weight: 600;
    margin: 20px 0 10px 0;
    display: flex;
    align-items: center;
}

.stNumberInput > div > div > input,
.stTextInput > div > div > input,
.stDateInput > div > div > input {
    border: 1px solid #D1D5DB;
    border-radius: 8px;
    padding: 12px;
    font-size: 16px;
}

.stButton > button {
    background: linear-gradient(135deg, #8B5CF6, #A855F7);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    width: 100%;
    margin: 8px 0;
    font-size: 14px;
    height: 40px;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #7C3AED, #9333EA);
    transform: translateY(-1px);
}

.stats-container {
    background: #F9FAFB;
    padding: 15px;
    border-radius: 10px;
    margin: 15px 0;
}

.stat-box {
    text-align: center;
    margin: 5px 0;
}

.stat-value {
    font-size: 24px;
    font-weight: bold;
    color: #8B5CF6;
}

.stat-label {
    font-size: 14px;
    color: #6B7280;
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

if 'income_saved' not in st.session_state:
    st.session_state.income_saved = False

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
# ✅ Income Input and Total Display
# ----------------------------
# Calculate total expenses
total_expenses = st.session_state.expenses_df['Price'].sum() if not st.session_state.expenses_df.empty else 0.0

# Income input section
st.markdown("**💚 Set Your Income:**")
col1, col2 = st.columns([2, 1])
with col1:
    new_income = st.number_input("Monthly Income (₹)", value=st.session_state.income, min_value=0.0, step=100.0)
with col2:
    if st.button("💾 Save", key="save_income"):
        st.session_state.income = new_income
        if save_income(new_income):
            st.session_state.income_saved = True
            st.success("✅ Income saved!")

# Income change warning
if not st.session_state.income_saved and new_income != st.session_state.income:
    st.markdown("""
    <div class="info-box">
        💡 <strong>Note:</strong> You have entered a new income amount. Click "Save" to confirm, 
        or use "Clear All Data" to reset everything including your saved income.
    </div>
    """, unsafe_allow_html=True)

# Display boxes
st.markdown(f"""
<div class="income-expense-container">
    <div class="income-box">
        <div class="box-title">💚 INCOME</div>
        <div class="box-value">₹{st.session_state.income:,.2f}</div>
    </div>
    <div class="total-amount-box">
        <div class="box-title">❤️ TOTAL EXPENSES</div>
        <div class="box-value">₹{total_expenses:,.2f}</div>
    </div>
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
st.markdown("""
<div class="section-header">
    💸 Add New Expense
</div>
""", unsafe_allow_html=True)

with st.form("expense_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📅 Date:**")
        expense_date = st.date_input("", value=date.today(), label_visibility="collapsed")

        st.markdown("**📝 Item Name:**")
        expense_item = st.text_input("", placeholder="e.g., Milk, Groceries", label_visibility="collapsed")
        if expense_item:
            expense_item = expense_item.title()  # Convert to Title Case
            st.write("Formatted:", expense_item)

    with col2:
        st.markdown("**💰 Price (₹):**")
        expense_price = st.number_input("", min_value=0.0, step=1.0, format="%.2f", label_visibility="collapsed")

        st.markdown("**📋 Note:** *(optional)*")
        expense_note = st.text_input("", placeholder="Additional details", label_visibility="collapsed")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submitted = st.form_submit_button("Submit", use_container_width=True)

    if submitted:
        if expense_item.strip() and expense_price > 0:
            new_expense = pd.DataFrame({
                'Date': [expense_date],
                'Item': [expense_item.strip().title()],
                'Price': [expense_price],
                'Note': [expense_note.strip() if expense_note.strip() else "N/A"]
            })
            st.session_state.expenses_df = pd.concat([st.session_state.expenses_df, new_expense], ignore_index=True)
            if save_to_csv(st.session_state.expenses_df):
                st.success("✅ Expense added and saved!")
                st.session_state.force_refresh = True
                st.rerun()
            else:
                st.error("❌ Error saving expense!")
        else:
            st.error("⚠️ Please enter item name and valid price!")

# ----------------------------
# ✅ Display & Editable Expenses
# ----------------------------
if not st.session_state.expenses_df.empty:
    st.markdown("---")
    st.markdown("### 📋 Recent Expenses")

    # 🔍 Stats + Download Button
    total_items = len(st.session_state.expenses_df)
    total_price = st.session_state.expenses_df['Price'].sum()
    average_price = st.session_state.expenses_df['Price'].mean()
    highest_price = st.session_state.expenses_df['Price'].max()

    left_col, right_col = st.columns([3, 1])
    with right_col:
        # Simple download format selection
        download_format = st.selectbox(
            "📥 Download Format:",
            ["Select Format", "CSV", "Excel", "TXT"],
            key="download_format"
        )

        if download_format == "CSV":
            csv_data = st.session_state.expenses_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"expenses_{datetime.now().strftime('%Y_%m_%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        elif download_format == "Excel":
            try:
                # Create Excel file in memory
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    st.session_state.expenses_df.to_excel(writer, index=False, sheet_name='Expenses')
                excel_data = output.getvalue()

                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name=f"expenses_{datetime.now().strftime('%Y_%m_%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except ImportError:
                st.error("Excel export requires additional libraries. Use CSV instead.")
                csv_data = st.session_state.expenses_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV (Alternative)",
                    data=csv_data,
                    file_name=f"expenses_{datetime.now().strftime('%Y_%m_%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        elif download_format == "TXT":
            # Create text format - FIXED VERSION
            txt_data = "Personal Budget Tracker - Expenses Report\n"
            txt_data += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            txt_data += "=" * 50 + "\n\n"
            
            # Safe iteration through DataFrame
            if not st.session_state.expenses_df.empty:
                df_copy = st.session_state.expenses_df.copy()
                for i in range(len(df_copy)):
                    row_data = df_copy.iloc[i]
                    txt_data += f"Date: {row_data['Date']}\n"
                    txt_data += f"Item: {row_data['Item']}\n"
                    txt_data += f"Price: ₹{row_data['Price']:.2f}\n"
                    txt_data += f"Note: {row_data['Note']}\n"
                    txt_data += "-" * 30 + "\n"

            txt_data += f"\nSummary:\n"
            txt_data += f"Total Items: {len(st.session_state.expenses_df)}\n"
            txt_data += f"Total Amount: ₹{st.session_state.expenses_df['Price'].sum():.2f}\n"

            st.download_button(
                label="📥 Download TXT",
                data=txt_data,
                file_name=f"expenses_{datetime.now().strftime('%Y_%m_%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
