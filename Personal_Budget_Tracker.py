
import pandas as pd
from datetime import datetime, date
import os
import tempfile

# Set page config
st.set_page_config(page_title="Budget Tracker", page_icon="💰", layout="centered")

# ----------------------------
# ✅ Custom CSS
# ----------------------------
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

def save_to_csv(df):
    try:
        os.makedirs(os.path.dirname(PERSISTENT_FILE), exist_ok=True)
        df.to_csv(PERSISTENT_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving: {e}")
        return False

# ----------------------------
# ✅ Session State Initialization
# ----------------------------
if 'expenses_df' not in st.session_state:
    st.session_state.expenses_df = load_expenses()

if 'last_refresh' not in st.session_state or st.session_state.get('force_refresh', False):
    st.session_state.expenses_df = load_expenses()
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

        st.markdown("**💰 Price (₹):**")
        expense_price = st.number_input("", min_value=0.0, step=1.0, format="%.2f", label_visibility="collapsed")

    with col2:
        st.markdown("**📝 Item Name:**")
        expense_item = st.text_input("", placeholder="e.g., Milk, Groceries", label_visibility="collapsed")

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
# ✅ Display Expenses
# ----------------------------
if not st.session_state.expenses_df.empty:
    st.markdown("---")
    st.markdown("### 📋 Recent Expenses")

    # 🔍 Static Report + Download Button
    total_items = len(st.session_state.expenses_df)
    total_price = st.session_state.expenses_df['Price'].sum()
    average_price = st.session_state.expenses_df['Price'].mean()
    highest_price = st.session_state.expenses_df['Price'].max()

    left_col, right_col = st.columns([3, 1])
    with right_col:
        csv_data = st.session_state.expenses_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"expenses_{datetime.now().strftime('%Y_%m_%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Show last 10 entries
    recent_df = st.session_state.expenses_df.copy()
    recent_df['Date'] = pd.to_datetime(recent_df['Date'])
    recent_df = recent_df.sort_values('Date', ascending=False).head(10)
    recent_df['Date'] = recent_df['Date'].dt.date
    display_df = recent_df.copy()
    display_df['Price'] = display_df['Price'].apply(lambda x: f"₹{x:,.2f}")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("📅 Date"),
            "Item": st.column_config.TextColumn("📝 Item"),
            "Price": st.column_config.TextColumn("💰 Price"),
            "Note": st.column_config.TextColumn("📋 Note")
        }
    )

    # Clear all data option
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🗑️ Clear All Data", use_container_width=True):
            st.session_state.expenses_df = pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note'])
            try:
                if os.path.exists(PERSISTENT_FILE):
                    os.remove(PERSISTENT_FILE)
                st.success("✅ All data cleared!")
                st.rerun()
            except Exception as e:
                st.error(f"Error clearing data: {e}")

else:
    st.info("📝 No expenses found. Add your first expense above!")
    st.caption(f"💾 Data will be stored")

