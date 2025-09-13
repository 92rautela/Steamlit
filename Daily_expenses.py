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

.file-section {
    background: #F0F9FF;
    border: 2px dashed #0EA5E9;
    padding: 15px;
    border-radius: 10px;
    margin: 15px 0;
    text-align: center;
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

.download-btn {
    background: linear-gradient(135deg, #059669, #10B981) !important;
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
# ✅ File Management Functions
# ----------------------------

def create_default_budget_file():
    """Create a default budget file structure"""
    default_data = {
        'expenses': pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note']),
        'income': 0.0,
        'created_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return default_data

def save_budget_to_file(expenses_df, income, filename=None):
    """Save budget data to Excel file with multiple sheets"""
    try:
        if filename is None:
            filename = f"budget_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Create a BytesIO buffer
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Save expenses
            expenses_df.to_excel(writer, sheet_name='Expenses', index=False)
            
            # Save income and metadata
            metadata_df = pd.DataFrame({
                'Parameter': ['Income', 'Total_Expenses', 'Remaining_Balance', 'Last_Updated'],
                'Value': [
                    income,
                    expenses_df['Price'].sum() if not expenses_df.empty else 0,
                    income - (expenses_df['Price'].sum() if not expenses_df.empty else 0),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ]
            })
            metadata_df.to_excel(writer, sheet_name='Settings', index=False)
        
        return buffer.getvalue(), filename
        
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None, None

def load_budget_from_file(uploaded_file):
    """Load budget data from uploaded Excel file"""
    try:
        # Read expenses sheet
        expenses_df = pd.read_excel(uploaded_file, sheet_name='Expenses')
        
        # Convert Date column to proper format
        if not expenses_df.empty and 'Date' in expenses_df.columns:
            expenses_df['Date'] = pd.to_datetime(expenses_df['Date'], errors='coerce').dt.date
        
        # Read settings sheet
        try:
            settings_df = pd.read_excel(uploaded_file, sheet_name='Settings')
            income = settings_df[settings_df['Parameter'] == 'Income']['Value'].iloc[0]
        except:
            income = 0.0
            
        return expenses_df, float(income)
        
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note']), 0.0

def auto_save_data(expenses_df, income):
    """Auto save data to temporary file for crash recovery"""
    try:
        temp_file = os.path.join(tempfile.gettempdir(), "budget_tracker_autosave.xlsx")
        
        with pd.ExcelWriter(temp_file, engine='openpyxl') as writer:
            expenses_df.to_excel(writer, sheet_name='Expenses', index=False)
            
            metadata_df = pd.DataFrame({
                'Parameter': ['Income', 'Last_Updated'],
                'Value': [income, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            })
            metadata_df.to_excel(writer, sheet_name='Settings', index=False)
            
        return True
    except:
        return False

def load_autosaved_data():
    """Load autosaved data for crash recovery"""
    try:
        temp_file = os.path.join(tempfile.gettempdir(), "budget_tracker_autosave.xlsx")
        if os.path.exists(temp_file):
            expenses_df = pd.read_excel(temp_file, sheet_name='Expenses')
            
            if not expenses_df.empty and 'Date' in expenses_df.columns:
                expenses_df['Date'] = pd.to_datetime(expenses_df['Date'], errors='coerce').dt.date
                
            settings_df = pd.read_excel(temp_file, sheet_name='Settings')
            income = settings_df[settings_df['Parameter'] == 'Income']['Value'].iloc[0]
            
            return expenses_df, float(income)
    except:
        pass
    
    return pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note']), 0.0

# ----------------------------
# ✅ Session State Initialization
# ----------------------------
if 'expenses_df' not in st.session_state:
    # Try to load autosaved data first
    st.session_state.expenses_df, st.session_state.income = load_autosaved_data()

if 'income' not in st.session_state:
    st.session_state.income = 0.0

if 'file_loaded' not in st.session_state:
    st.session_state.file_loaded = False

if 'current_filename' not in st.session_state:
    st.session_state.current_filename = None

# ----------------------------
# ✅ Header
# ----------------------------
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown("""
<div class="header-box">
    💰 Personal Budget Tracker 💰<br>
    <small>Import your file or start fresh!</small>
</div>
""", unsafe_allow_html=True)

# ----------------------------
# ✅ File Import/Export Section
# ----------------------------
st.markdown("""
<div class="file-section">
    📁 File Management
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**📤 Import Budget File:**")
    uploaded_file = st.file_uploader(
        "Choose your budget file", 
        type=['xlsx'], 
        help="Upload your existing budget Excel file",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None and not st.session_state.file_loaded:
        expenses_df, income = load_budget_from_file(uploaded_file)
        st.session_state.expenses_df = expenses_df
        st.session_state.income = income
        st.session_state.file_loaded = True
        st.session_state.current_filename = uploaded_file.name
        st.success(f"✅ File '{uploaded_file.name}' loaded successfully!")
        st.rerun()

with col2:
    st.markdown("**📥 Download Budget File:**")
    
    # Auto-generate filename
    download_filename = f"my_budget_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    if not st.session_state.expenses_df.empty or st.session_state.income > 0:
        file_data, filename = save_budget_to_file(
            st.session_state.expenses_df, 
            st.session_state.income, 
            download_filename
        )
        
        if file_data:
            st.download_button(
                label="💾 Download Budget",
                data=file_data,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    else:
        st.info("Add some data first!")

# File status
if st.session_state.current_filename:
    st.info(f"📁 Current file: **{st.session_state.current_filename}**")

# Reset file loaded flag when upload is cleared
if uploaded_file is None and st.session_state.file_loaded:
    st.session_state.file_loaded = False

# ----------------------------
# ✅ Calculate totals
# ----------------------------
total_expenses = 0.0
if not st.session_state.expenses_df.empty and 'Price' in st.session_state.expenses_df.columns:
    price_values = pd.to_numeric(st.session_state.expenses_df['Price'], errors='coerce').fillna(0)
    total_expenses = price_values.sum()

# ----------------------------
# ✅ Income Input and Display
# ----------------------------
st.markdown("**💚 Set Your Income:**")
col1, col2 = st.columns([2, 1])
with col1:
    new_income = st.number_input("Monthly Income (₹)", value=st.session_state.income, min_value=0.0, step=100.0)
with col2:
    if st.button("💾 Save", key="save_income"):
        st.session_state.income = new_income
        auto_save_data(st.session_state.expenses_df, st.session_state.income)
        st.success("✅ Income saved!")

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

    with col2:
        st.markdown("**💰 Price (₹):**")
        expense_price = st.number_input("", min_value=0.0, step=1.0, format="%.2f", label_visibility="collapsed")

        st.markdown("**📋 Note:** *(optional)*")
        expense_note = st.text_input("", placeholder="Additional details", label_visibility="collapsed")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submitted = st.form_submit_button("➕ Add Expense", use_container_width=True)

    if submitted:
        if expense_item.strip() and expense_price > 0:
            new_expense = pd.DataFrame({
                'Date': [expense_date],
                'Item': [expense_item.strip().title()],
                'Price': [float(expense_price)],
                'Note': [expense_note.strip() if expense_note.strip() else "N/A"]
            })
            st.session_state.expenses_df = pd.concat([st.session_state.expenses_df, new_expense], ignore_index=True)
            
            # Auto-save after adding expense
            if auto_save_data(st.session_state.expenses_df, st.session_state.income):
                st.success("✅ Expense added and auto-saved!")
            else:
                st.warning("⚠️ Expense added but auto-save failed!")
                
            st.rerun()
        else:
            st.error("⚠️ Please enter item name and valid price!")

# ----------------------------
# ✅ Display & Edit Expenses
# ----------------------------
if not st.session_state.expenses_df.empty:
    st.markdown("---")
    st.markdown("### 📋 Your Expenses")

    # Statistics
    if len(st.session_state.expenses_df) > 0:
        avg_expense = st.session_state.expenses_df['Price'].mean()
        max_expense = st.session_state.expenses_df['Price'].max()
        total_items = len(st.session_state.expenses_df)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Items", total_items)
        with col2:
            st.metric("💰 Average", f"₹{avg_expense:.2f}")
        with col3:
            st.metric("🔝 Highest", f"₹{max_expense:.2f}")

    st.markdown("### ✏️ Edit Expenses")

    # Editable data
    editable_df = st.session_state.expenses_df.copy()

    if not editable_df.empty:
        # Ensure proper data types
        editable_df["Date"] = pd.to_datetime(editable_df["Date"], errors="coerce").dt.date
        editable_df["Price"] = pd.to_numeric(editable_df["Price"], errors="coerce").fillna(0.0)
        editable_df["Item"] = editable_df["Item"].astype(str)
        editable_df["Note"] = editable_df["Note"].astype(str)

        # Sort by date (newest first)
        editable_df = editable_df.sort_values('Date', ascending=False)

        # Editable Table
        updated_df = st.data_editor(
            editable_df,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "Date": st.column_config.DateColumn("📅 Date"),
                "Item": st.column_config.TextColumn("📝 Item", help="Click to edit"),
                "Price": st.column_config.NumberColumn("💰 Price", format="₹%.2f"),
                "Note": st.column_config.TextColumn("📋 Note")
            }
        )

        # Check if data was modified
        if not updated_df.equals(st.session_state.expenses_df.sort_values('Date', ascending=False).reset_index(drop=True)):
            st.session_state.expenses_df = updated_df.reset_index(drop=True)
            auto_save_data(st.session_state.expenses_df, st.session_state.income)
            st.info("🔄 Changes auto-saved!")

    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            # Try to reload autosaved data
            expenses_df, income = load_autosaved_data()
            st.session_state.expenses_df = expenses_df
            st.session_state.income = income
            st.success("✅ Data refreshed!")
            st.rerun()
    
    with col2:
        if st.button("💾 Manual Save", use_container_width=True):
            if auto_save_data(st.session_state.expenses_df, st.session_state.income):
                st.success("✅ Data saved manually!")
            else:
                st.error("❌ Save failed!")
    
    with col3:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.expenses_df = pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note'])
            st.session_state.income = 0.0
            st.session_state.current_filename = None
            
            # Remove autosave file
            try:
                temp_file = os.path.join(tempfile.gettempdir(), "budget_tracker_autosave.xlsx")
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
                
            st.success("✅ All data cleared!")
            st.rerun()

else:
    st.markdown("---")
    st.info("📝 No expenses found. Add your first expense above or import a budget file!")
    
    # Show example of creating new budget
    st.markdown("""
    ### 🚀 Getting Started:
    1. **📤 Import existing file**: Upload your Excel budget file
    2. **➕ Add expenses**: Use the form above to add new expenses  
    3. **💾 Download**: Save your budget as Excel file anytime
    4. **🔄 Auto-recovery**: Data is auto-saved to prevent loss
    """)

# Footer info
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 12px;">
    💡 <strong>Tips:</strong> Your data auto-saves after every change • Download your file regularly as backup • 
    Upload the same file to continue where you left off
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
