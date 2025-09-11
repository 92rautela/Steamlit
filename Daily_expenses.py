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
# ✅ File Path - Using user's home directory for better persistence
# ----------------------------
# Create a more persistent directory in user's home folder
try:
    HOME_DIR = os.path.expanduser("~")
    DATA_DIR = os.path.join(HOME_DIR, "BudgetTracker")
    os.makedirs(DATA_DIR, exist_ok=True)
    PERSISTENT_FILE = os.path.join(DATA_DIR, "budget_tracker_expenses.csv")
    INCOME_FILE = os.path.join(DATA_DIR, "budget_tracker_income.csv")
except:
    # Fallback to temp directory if home directory is not accessible
    DATA_DIR = tempfile.gettempdir()
    PERSISTENT_FILE = os.path.join(DATA_DIR, "budget_tracker_expenses.csv")
    INCOME_FILE = os.path.join(DATA_DIR, "budget_tracker_income.csv")

# ----------------------------
# ✅ Load and Save Functions - Improved error handling
# ----------------------------

def load_expenses():
    try:
        if os.path.exists(PERSISTENT_FILE) and os.path.getsize(PERSISTENT_FILE) > 0:
            df = pd.read_csv(PERSISTENT_FILE)
            if not df.empty and 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
                df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0.0)
                df['Item'] = df['Item'].astype(str)
                df['Note'] = df['Note'].astype(str).fillna("N/A")
            return df
    except Exception as e:
        st.warning(f"⚠️ Error loading expenses: {e}. Starting with empty data.")
    
    return pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note'])

def load_income():
    try:
        if os.path.exists(INCOME_FILE) and os.path.getsize(INCOME_FILE) > 0:
            df = pd.read_csv(INCOME_FILE)
            if not df.empty and 'Income' in df.columns:
                return float(df['Income'].iloc[0])
    except Exception as e:
        st.warning(f"⚠️ Error loading income: {e}. Starting with 0.")
    
    return 0.0

def save_to_csv(df):
    try:
        if df is not None and not df.empty:
            # Ensure directory exists
            os.makedirs(os.path.dirname(PERSISTENT_FILE), exist_ok=True)
            
            # Create a backup before saving
            if os.path.exists(PERSISTENT_FILE):
                backup_file = PERSISTENT_FILE + ".backup"
                try:
                    import shutil
                    shutil.copy2(PERSISTENT_FILE, backup_file)
                except:
                    pass
            
            # Save the data
            df_to_save = df.copy()
            df_to_save['Date'] = pd.to_datetime(df_to_save['Date']).dt.strftime('%Y-%m-%d')
            df_to_save.to_csv(PERSISTENT_FILE, index=False)
            return True
    except Exception as e:
        st.error(f"❌ Error saving expenses: {e}")
        # Try to restore from backup if available
        backup_file = PERSISTENT_FILE + ".backup"
        if os.path.exists(backup_file):
            try:
                import shutil
                shutil.copy2(backup_file, PERSISTENT_FILE)
                st.info("🔄 Restored from backup")
            except:
                pass
        return False
    
    return False

def save_income(income):
    try:
        os.makedirs(os.path.dirname(INCOME_FILE), exist_ok=True)
        income_df = pd.DataFrame({'Income': [float(income)]})
        income_df.to_csv(INCOME_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"❌ Error saving income: {e}")
        return False

# ----------------------------
# ✅ Initialize Session State - Improved initialization
# ----------------------------

# Force data refresh every time app starts to prevent stale data
def initialize_data():
    st.session_state.expenses_df = load_expenses()
    st.session_state.income = load_income()
    st.session_state.data_loaded = True

# Initialize only once or when forced
if 'data_loaded' not in st.session_state or not st.session_state.get('data_loaded', False):
    initialize_data()

# Set other session state variables
if 'income_saved' not in st.session_state:
    st.session_state.income_saved = False

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
# ✅ Income Input and Total Display - Fixed calculation
# ----------------------------

# Calculate total expenses with better error handling
total_expenses = 0.0
if not st.session_state.expenses_df.empty:
    try:
        if 'Price' in st.session_state.expenses_df.columns:
            price_values = pd.to_numeric(st.session_state.expenses_df['Price'], errors='coerce').fillna(0)
            total_expenses = float(price_values.sum())
    except Exception as e:
        st.warning(f"⚠️ Error calculating expenses: {e}")
        total_expenses = 0.0

# Income input section
st.markdown("**💚 Set Your Income:**")
col1, col2 = st.columns([2, 1])
with col1:
    new_income = st.number_input(
        "Monthly Income (₹)", 
        value=float(st.session_state.income), 
        min_value=0.0, 
        step=100.0,
        key="income_input"
    )
with col2:
    if st.button("💾 Save", key="save_income"):
        if save_income(new_income):
            st.session_state.income = new_income
            st.session_state.income_saved = True
            st.success("✅ Income saved!")
        else:
            st.error("❌ Failed to save income!")

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
remaining = float(st.session_state.income) - total_expenses
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
# ✅ Add Expense Form - Improved handling
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

    with col2:
        st.markdown("**💰 Price (₹):**")
        expense_price = st.number_input("", min_value=0.0, step=1.0, format="%.2f", label_visibility="collapsed")

        st.markdown("**📋 Note:** *(optional)*")
        expense_note = st.text_input("", placeholder="Additional details", label_visibility="collapsed")

    # Show formatted item name if entered
    if expense_item:
        formatted_item = expense_item.strip().title()
        st.write(f"Formatted: **{formatted_item}**")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submitted = st.form_submit_button("✅ Add Expense", use_container_width=True)

    if submitted:
        if expense_item and expense_item.strip() and expense_price > 0:
            try:
                new_expense = pd.DataFrame({
                    'Date': [expense_date],
                    'Item': [expense_item.strip().title()],
                    'Price': [float(expense_price)],
                    'Note': [expense_note.strip() if expense_note and expense_note.strip() else "N/A"]
                })
                
                # Add to session state
                st.session_state.expenses_df = pd.concat([st.session_state.expenses_df, new_expense], ignore_index=True)
                
                # Save immediately
                if save_to_csv(st.session_state.expenses_df):
                    st.success("✅ Expense added and saved successfully!")
                    # Force refresh to show updated data
                    st.rerun()
                else:
                    st.error("❌ Failed to save expense to file!")
            except Exception as e:
                st.error(f"❌ Error adding expense: {e}")
        else:
            st.error("⚠️ Please enter a valid item name and price!")

# ----------------------------
# ✅ Display & Editable Expenses - Improved data handling
# ----------------------------
if not st.session_state.expenses_df.empty:
    st.markdown("---")
    st.markdown("### 📋 Your Expenses")

    try:
        # Create editable copy with proper data types
        editable_df = st.session_state.expenses_df.copy()
        
        # Ensure proper data types
        editable_df["Date"] = pd.to_datetime(editable_df["Date"], errors="coerce").dt.date
        editable_df["Price"] = pd.to_numeric(editable_df["Price"], errors="coerce").fillna(0.0)
        editable_df["Item"] = editable_df["Item"].astype(str)
        editable_df["Note"] = editable_df["Note"].astype(str).fillna("N/A")
        
        # Sort by date (newest first)
        editable_df = editable_df.sort_values('Date', ascending=False)

        st.markdown("### ✏️ Edit/Delete Expenses")
        
        # Editable Table
        updated_df = st.data_editor(
            editable_df,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "Date": st.column_config.DateColumn("📅 Date"),
                "Item": st.column_config.TextColumn("📝 Item", help="Click to edit", width="medium"),
                "Price": st.column_config.NumberColumn("💰 Price", format="₹%.2f", min_value=0.0),
                "Note": st.column_config.TextColumn("📋 Note", help="Optional note")
            },
            key="expense_editor"
        )

        # Save changes button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("💾 Save Changes", use_container_width=True, key="save_changes"):
                try:
                    # Update session state
                    st.session_state.expenses_df = updated_df.copy()
                    
                    # Save to file
                    if save_to_csv(st.session_state.expenses_df):
                        st.success("✅ Changes saved successfully!")
                    else:
                        st.error("❌ Failed to save changes!")
                except Exception as e:
                    st.error(f"❌ Error saving changes: {e}")

    except Exception as e:
        st.error(f"❌ Error displaying expenses: {e}")
        st.info("🔄 Refreshing data...")
        initialize_data()
        st.rerun()

    # Statistics
    if len(st.session_state.expenses_df) > 0:
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_expense = total_expenses / len(st.session_state.expenses_df) if len(st.session_state.expenses_df) > 0 else 0
            st.metric("Average Expense", f"₹{avg_expense:.2f}")
        
        with col2:
            max_expense = st.session_state.expenses_df['Price'].max() if not st.session_state.expenses_df.empty else 0
            st.metric("Highest Expense", f"₹{max_expense:.2f}")
        
        with col3:
            expense_count = len(st.session_state.expenses_df)
            st.metric("Total Entries", expense_count)

else:
    st.info("📝 No expenses found. Add your first expense above!")

# ----------------------------
# ✅ Data Management Section
# ----------------------------
st.markdown("---")
st.markdown("### 🛠️ Data Management")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Refresh Data", use_container_width=True):
        initialize_data()
        st.success("✅ Data refreshed!")
        st.rerun()

with col2:
    if st.button("📤 Export Data", use_container_width=True):
        if not st.session_state.expenses_df.empty:
            csv_data = st.session_state.expenses_df.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
                data=csv_data,
                file_name=f"budget_expenses_{date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("⚠️ No data to export!")

# Clear all data option (with confirmation)
if st.checkbox("🗑️ Enable Clear All Data (dangerous)"):
    if st.button("🗑️ Clear All Data", use_container_width=True, type="secondary"):
        try:
            # Clear session state
            st.session_state.expenses_df = pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note'])
            st.session_state.income = 0.0
            st.session_state.income_saved = False
            
            # Remove files
            if os.path.exists(PERSISTENT_FILE):
                os.remove(PERSISTENT_FILE)
            if os.path.exists(INCOME_FILE):
                os.remove(INCOME_FILE)
            
            st.success("✅ All data cleared!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error clearing data: {e}")

st.markdown('</div>', unsafe_allow_html=True)
