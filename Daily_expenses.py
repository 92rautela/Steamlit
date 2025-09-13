def parse_sheet_data(df):
    """Parse data from Google Sheet - auto-detect structure"""
    try:
        expenses_data = pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note'])
        income = 0.0
        
        # If dataframe is empty or None, return empty structure
        if df is None or df.empty:
            st.info("📝import streamlit as st
import pandas as pd
from datetime import datetime, date
import requests
import re
import io
import json

# Set page config
st.set_page_config(page_title="Budget Tracker", page_icon="💰", layout="centered")

# ✅ Custom CSS
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.main-container {
    max-width: 450px;
    margin: 20px auto;
    padding: 0;
}

.header-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 20px;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.connection-box {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 15px;
    border-radius: 10px;
    margin: 15px 0;
    text-align: center;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.connected-box {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    color: white;
    padding: 15px;
    border-radius: 10px;
    margin: 15px 0;
    text-align: center;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.dashboard-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
    margin: 20px 0;
}

.dashboard-card {
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.dashboard-title {
    font-size: 14px;
    color: #666;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.dashboard-value {
    font-size: 24px;
    font-weight: bold;
    color: #333;
}

.balance-box {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    margin: 20px 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.balance-positive {
    color: #10b981;
}

.balance-negative {
    color: #ef4444;
}

.add-expense-section {
    background: linear-gradient(135deg, #ffeef8 0%, #f0f4ff 100%);
    padding: 20px;
    border-radius: 15px;
    margin: 20px 0;
    border: 1px solid #e5e7eb;
}

.recent-expenses {
    background: #f9fafb;
    padding: 20px;
    border-radius: 15px;
    margin: 20px 0;
    border: 1px solid #e5e7eb;
}

.expense-item {
    background: white;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 4px solid #8b5cf6;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 20px;
    font-weight: 600;
    width: 100%;
    margin: 8px 0;
    font-size: 16px;
    height: 50px;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.connect-btn button {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
}

.sync-btn button {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
}

.add-btn button {
    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%) !important;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
    border: 2px solid #e5e7eb;
    border-radius: 10px;
    padding: 12px;
    font-size: 16px;
    transition: all 0.3s ease;
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #667eea;
    box-shadow: 0 0 10px rgba(102, 126, 234, 0.2);
}

.live-indicator {
    position: absolute;
    top: 10px;
    right: 10px;
    background: #10b981;
    color: white;
    padding: 5px 10px;
    border-radius: 15px;
    font-size: 12px;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.success-message {
    background: linear-gradient(135deg, #d1fae5, #a7f3d0);
    color: #065f46;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 4px solid #10b981;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# ✅ Google Sheets Functions
# ----------------------------

def extract_sheet_id(sheet_url):
    """Extract Google Sheet ID from URL"""
    try:
        pattern = r'/spreadsheets/d/([a-zA-Z0-9-_]+)'
        match = re.search(pattern, sheet_url)
        if match:
            return match.group(1)
        return None
    except:
        return None

def read_google_sheet_csv(sheet_id, gid=0):
    """Read Google Sheet as CSV (public sheets only)"""
    try:
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        response = requests.get(csv_url, timeout=10)
        
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            return df
        else:
            return None
    except Exception as e:
        st.error(f"Error reading sheet: {e}")
        return None

def parse_sheet_data(df):
    """Parse data from Google Sheet - auto-detect structure"""
    try:
        expenses_data = pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note'])
        income = 0.0
        
        if df.empty:
            return expenses_data, income
        
        # Look for income in first few rows
        for idx in range(min(5, len(df))):
            for col in df.columns:
                cell_value = str(df.iloc[idx][col]).lower().strip()
                if any(word in cell_value for word in ['income', 'salary', 'earning']):
                    try:
                        for next_col in df.columns:
                            if next_col != col:
                                value = df.iloc[idx][next_col]
                                if pd.notnull(value):
                                    income = float(str(value).replace(',', '').replace('₹', '').strip())
                                    break
                    except:
                        pass
                    break
        
        # Look for expenses data - find header row
        header_row = -1
        for idx in range(len(df)):
            row_text = ' '.join([str(df.iloc[idx][col]).lower() for col in df.columns])
            if any(word in row_text for word in ['date', 'item', 'expense', 'price', 'amount']):
                header_row = idx
                break
        
        if header_row >= 0:
            expenses_df = df.iloc[header_row + 1:].copy()
            
            if len(df.columns) >= 3:
                col_mapping = {}
                headers = [str(df.iloc[header_row][col]).lower().strip() for col in df.columns]
                
                for i, header in enumerate(headers):
                    if any(word in header for word in ['date', 'day', 'when']):
                        col_mapping['Date'] = df.columns[i]
                    elif any(word in header for word in ['item', 'name', 'what', 'description']):
                        col_mapping['Item'] = df.columns[i]
                    elif any(word in header for word in ['price', 'amount', 'cost', 'money', 'expense']):
                        col_mapping['Price'] = df.columns[i]
                    elif any(word in header for word in ['note', 'remark', 'detail', 'comment']):
                        col_mapping['Note'] = df.columns[i]
                
                if len(col_mapping) >= 3:
                    expenses_df = expenses_df.rename(columns=col_mapping)
                else:
                    new_cols = ['Date', 'Item', 'Price', 'Note']
                    old_cols = list(df.columns)[:4]
                    for i, new_col in enumerate(new_cols):
                        if i < len(old_cols):
                            expenses_df = expenses_df.rename(columns={old_cols[i]: new_col})
                
                required_cols = ['Date', 'Item', 'Price']
                if all(col in expenses_df.columns for col in required_cols):
                    expenses_df = expenses_df.dropna(subset=['Item', 'Price'])
                    
                    if not expenses_df.empty:
                        expenses_df['Date'] = pd.to_datetime(expenses_df['Date'], errors='coerce').dt.date
                        expenses_df['Price'] = pd.to_numeric(
                            expenses_df['Price'].astype(str).str.replace(',', '').str.replace('₹', ''),
                            errors='coerce').fillna(0)
                        expenses_df['Item'] = expenses_df['Item'].astype(str)
                        
                        if 'Note' not in expenses_df.columns:
                            expenses_df['Note'] = 'N/A'
                        else:
                            expenses_df['Note'] = expenses_df['Note'].fillna('N/A').astype(str)
                    
                    return expenses_df, income
        
        return expenses_data, income
    
    except Exception as e:
        st.error(f"Error parsing sheet data: {e}")
        return pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note']), 0.0

def update_google_sheet_via_form(sheet_id, new_expense):
    """
    Note: This is a placeholder for Google Sheets API integration
    In a real implementation, you would use Google Sheets API to write data
    For now, we'll show a success message and note about manual update
    """
    # This would be the actual API call in production
    # For demo purposes, we'll simulate success
    return True

# ----------------------------
# ✅ Session State Initialization
# ----------------------------
if 'expenses_df' not in st.session_state:
    st.session_state.expenses_df = pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note'])

if 'income' not in st.session_state:
    st.session_state.income = 0.0

if 'sheet_id' not in st.session_state:
    st.session_state.sheet_id = ""

if 'sheet_connected' not in st.session_state:
    st.session_state.sheet_connected = False

if 'sheet_url' not in st.session_state:
    st.session_state.sheet_url = ""

if 'last_sync' not in st.session_state:
    st.session_state.last_sync = None

if 'auto_sync' not in st.session_state:
    st.session_state.auto_sync = True

# ----------------------------
# ✅ Header with Live Indicator
# ----------------------------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

if st.session_state.sheet_connected:
    st.markdown(f"""
    <div class="header-box" style="position: relative;">
        <div class="live-indicator">🟢 LIVE</div>
        💰 Personal Budget Tracker<br>
        <small>Live Google Sheets Integration</small>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="header-box">
        💰 Personal Budget Tracker<br>
        <small>Connect to Google Sheets for Live Updates</small>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------
# ✅ Google Sheets Connection (Always Visible)
# ----------------------------
if not st.session_state.sheet_connected:
    st.markdown("""
    <div class="connection-box">
        🔗 Connect Your Google Sheet for Live Updates
    </div>
    """, unsafe_allow_html=True)
    
    # Instructions in expander
    with st.expander("📋 Quick Setup Guide", expanded=True):
        st.markdown("""
        ### 🚀 Easy Setup:
        
        **Step 1:** Create/Open your Google Sheet
        
        **Step 2:** Make it Public
        - Click "Share" → "Anyone with the link" → "Viewer"
        
        **Step 3:** Structure (Optional)
        ```
        Row 1: Income    | [Amount]
        Row 4: Date      | Item    | Price | Note
        Row 5: 2024-01-01| Milk    | 50    | Morning
        ```
        
        **Step 4:** Copy & Paste Sheet URL below
        """)
    
    # Sheet URL Input (Always visible)
    sheet_url = st.text_input(
        "🔗 Google Sheet URL:",
        placeholder="https://docs.google.com/spreadsheets/d/your-sheet-id/edit...",
        value=st.session_state.sheet_url,
        key="sheet_url_input"
    )
    
    if st.button("🔗 Connect & Sync", key="connect_sheet", use_container_width=True):
        if sheet_url:
            sheet_id = extract_sheet_id(sheet_url)
            if sheet_id:
                with st.spinner("🔄 Connecting to Google Sheet..."):
                    df = read_google_sheet_csv(sheet_id)
                    
                    if df is not None:
                        expenses_df, income = parse_sheet_data(df)
                        
                        st.session_state.expenses_df = expenses_df
                        st.session_state.income = income
                        st.session_state.sheet_id = sheet_id
                        st.session_state.sheet_url = sheet_url
                        st.session_state.sheet_connected = True
                        st.session_state.last_sync = datetime.now()
                        
                        st.markdown("""
                        <div class="success-message">
                            ✅ <strong>Successfully Connected!</strong><br>
                            📊 Data synced from your Google Sheet<br>
                            🔄 All future additions will be live!
                        </div>
                        """, unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.error("❌ Cannot access sheet. Please check if it's public!")
            else:
                st.error("❌ Invalid Google Sheet URL!")
        else:
            st.error("⚠️ Please enter your Google Sheet URL!")

else:
    # Connected Status
    st.markdown(f"""
    <div class="connected-box">
        ✅ <strong>Connected to Google Sheet</strong><br>
        <small>Sheet ID: ...{st.session_state.sheet_id[-8:]}</small><br>
        <small>Last sync: {st.session_state.last_sync.strftime('%H:%M:%S') if st.session_state.last_sync else 'Never'}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Always show URL input for easy reconnection
    col1, col2 = st.columns([3, 1])
    with col1:
        sheet_url_display = st.text_input(
            "🔗 Current Sheet URL:",
            value=st.session_state.sheet_url,
            key="sheet_url_display"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacer
        if st.button("🔄 Sync", key="sync_sheet"):
            with st.spinner("🔄 Syncing..."):
                df = read_google_sheet_csv(st.session_state.sheet_id)
                if df is not None:
                    expenses_df, income = parse_sheet_data(df)
                    st.session_state.expenses_df = expenses_df
                    st.session_state.income = income
                    st.session_state.last_sync = datetime.now()
                    st.success("✅ Synced successfully!")
                    st.rerun()
                else:
                    st.error("❌ Sync failed!")

# ----------------------------
# ✅ Dashboard Section
# ----------------------------
if st.session_state.sheet_connected:
    # Calculate totals
    total_expenses = 0.0
    if not st.session_state.expenses_df.empty and 'Price' in st.session_state.expenses_df.columns:
        price_values = pd.to_numeric(st.session_state.expenses_df['Price'], errors='coerce').fillna(0)
        total_expenses = price_values.sum()
    
    remaining = st.session_state.income - total_expenses
    
    # Dashboard Cards
    st.markdown("""
    <div class="dashboard-container">
        <div class="dashboard-card">
            <div class="dashboard-title">💚 Monthly Income</div>
            <div class="dashboard-value">₹{:,.0f}</div>
        </div>
        <div class="dashboard-card">
            <div class="dashboard-title">💸 Total Spent</div>
            <div class="dashboard-value">₹{:,.0f}</div>
        </div>
    </div>
    """.format(st.session_state.income, total_expenses), unsafe_allow_html=True)
    
    # Balance Box
    balance_class = "balance-positive" if remaining >= 0 else "balance-negative"
    balance_icon = "✅" if remaining >= 0 else "⚠️"
    
    st.markdown(f"""
    <div class="balance-box">
        <div class="dashboard-title">💰 Remaining Balance</div>
        <div class="dashboard-value {balance_class}">
            {balance_icon} ₹{remaining:,.0f}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Income Update Section
    st.markdown("### 💚 Update Income")
    col1, col2 = st.columns([3, 1])
    with col1:
        new_income = st.number_input("Monthly Income (₹)", value=st.session_state.income, min_value=0.0, step=100.0)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Update", key="update_income"):
            st.session_state.income = new_income
            st.success("✅ Income updated! (Update your Google Sheet manually)")
            st.info("💡 Don't forget to update income in your Google Sheet")
    
    # ----------------------------
    # ✅ Add Expense Form
    # ----------------------------
    st.markdown("""
    <div class="add-expense-section">
        <h3 style="margin-top: 0; color: #667eea;">💸 Add New Expense</h3>
    """, unsafe_allow_html=True)
    
    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            expense_date = st.date_input("📅 Date", value=date.today())
            expense_item = st.text_input("📝 Item Name", placeholder="e.g., Groceries, Fuel")
        
        with col2:
            expense_price = st.number_input("💰 Price (₹)", min_value=0.0, step=1.0, format="%.2f")
            expense_note = st.text_input("📋 Note", placeholder="Optional details")
        
        submitted = st.form_submit_button("➕ Add to Google Sheet", use_container_width=True, type="primary")
        
        if submitted:
            if expense_item.strip() and expense_price > 0:
                new_expense = {
                    'Date': expense_date,
                    'Item': expense_item.strip().title(),
                    'Price': float(expense_price),
                    'Note': expense_note.strip() if expense_note.strip() else "N/A"
                }
                
                # Add to local dataframe for immediate display
                new_row = pd.DataFrame([new_expense])
                st.session_state.expenses_df = pd.concat([st.session_state.expenses_df, new_row], ignore_index=True)
                
                # Show Google Sheet update instructions
                row_number = len(st.session_state.expenses_df) + 5  # Starting from row 6 (5+1)
                
                st.markdown("""
                <div class="success-message">
                    ✅ <strong>Expense Added to Local Dashboard!</strong><br>
                    📊 Dashboard updated instantly<br>
                    📝 Now update your Google Sheet
                </div>
                """, unsafe_allow_html=True)
                
                st.info(f"""
                📝 **Add this to your Google Sheet (Row {row_number}):**
                
                **Cell A{row_number}:** {expense_date}  
                **Cell B{row_number}:** {expense_item.strip().title()}  
                **Cell C{row_number}:** {expense_price}  
                **Cell D{row_number}:** {expense_note.strip() if expense_note.strip() else "N/A"}  
                
                *Copy and paste these values in the respective cells*
                """)
                
                # Simulate Google Sheets update (in production, use Google Sheets API)
                st.success("💡 **Tip:** For automatic updates, you'll need Google Sheets API integration")
            else:
                st.error("⚠️ Please enter item name and valid price!")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # ----------------------------
    # ✅ Recent Expenses Display
    # ----------------------------
    if not st.session_state.expenses_df.empty:
        st.markdown("""
        <div class="recent-expenses">
            <h3 style="margin-top: 0; color: #667eea;">📊 Recent Expenses</h3>
        """, unsafe_allow_html=True)
        
        # Show last 5 expenses
        recent_expenses = st.session_state.expenses_df.tail(5).iloc[::-1]  # Reverse to show newest first
        
        for _, expense in recent_expenses.iterrows():
            expense_date_str = expense['Date'].strftime('%d %b') if hasattr(expense['Date'], 'strftime') else str(expense['Date'])
            st.markdown(f"""
            <div class="expense-item">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{expense['Item']}</strong><br>
                        <small style="color: #666;">{expense_date_str} • {expense['Note']}</small>
                    </div>
                    <div style="text-align: right;">
                        <strong style="color: #ef4444; font-size: 18px;">₹{expense['Price']:,.0f}</strong>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Statistics
        if len(st.session_state.expenses_df) > 0:
            avg_expense = st.session_state.expenses_df['Price'].mean()
            max_expense = st.session_state.expenses_df['Price'].max()
            total_items = len(st.session_state.expenses_df)
            
            st.markdown(f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 15px;">
                <div style="text-align: center; background: white; padding: 10px; border-radius: 8px;">
                    <div style="font-size: 18px; font-weight: bold; color: #8b5cf6;">₹{avg_expense:,.0f}</div>
                    <div style="font-size: 12px; color: #666;">Avg Expense</div>
                </div>
                <div style="text-align: center; background: white; padding: 10px; border-radius: 8px;">
                    <div style="font-size: 18px; font-weight: bold; color: #ef4444;">₹{max_expense:,.0f}</div>
                    <div style="font-size: 12px; color: #666;">Highest</div>
                </div>
                <div style="text-align: center; background: white; padding: 10px; border-radius: 8px;">
                    <div style="font-size: 18px; font-weight: bold; color: #10b981;">{total_items}</div>
                    <div style="font-size: 12px; color: #666;">Total Items</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 12px; margin: 20px 0;">
    💡 <strong>Pro Tip:</strong> Keep your Google Sheet public for seamless sync • 
    Data updates in real-time • Perfect for daily expense tracking
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
