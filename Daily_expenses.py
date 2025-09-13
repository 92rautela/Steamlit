import streamlit as st
import pandas as pd
from datetime import datetime, date
import requests
import re
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

.info-box {
    background: #fef3c7;
    color: #92400e;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 4px solid #f59e0b;
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
            csv_content = response.text.strip()
            
            # Check if sheet is empty
            if not csv_content or len(csv_content.split('\n')) <= 1:
                return pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note'])
            
            try:
                df = pd.read_csv(io.StringIO(csv_content))
                if df.empty:
                    return pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note'])
                return df
            except pd.errors.EmptyDataError:
                return pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note'])
                
        elif response.status_code == 403:
            st.error("🔒 Sheet is not public! Please make it public: Share → Anyone with link → Viewer")
            return None
        elif response.status_code == 404:
            st.error("❌ Sheet not found! Please check the URL.")
            return None
        else:
            st.error(f"❌ Cannot access sheet. Status code: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def parse_sheet_data(df):
    """Parse data from Google Sheet - auto-detect structure"""
    try:
        expenses_data = pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note'])
        income = 0.0
        
        # If dataframe is empty or None
        if df is None or df.empty:
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
        
        # Look for expenses data
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
# ✅ Connection Section
# ----------------------------
st.markdown("### 🔗 Google Sheet Connection")

# Always show URL input
sheet_url = st.text_input(
    "Google Sheet URL:",
    placeholder="https://docs.google.com/spreadsheets/d/your-sheet-id/edit...",
    value=st.session_state.sheet_url,
    help="Paste your Google Sheet URL here (Sheet must be public)"
)

if not st.session_state.sheet_connected:
    # Show setup instructions
    with st.expander("📋 Setup Instructions", expanded=False):
        st.markdown("""
        ### 🚀 Quick Setup:
        
        **Option 1: Empty Sheet (I'll guide you)**
        1. Create new Google Sheet (can be completely empty)
        2. Make it public: Share → Anyone with link → Viewer  
        3. Paste URL above and click Connect
        4. I'll show you exactly what to add!
        
        **Option 2: Existing Sheet**  
        Structure your sheet like this:
        ```
        Row 1: Income    | 25000
        Row 3: Date      | Item     | Price | Note  
        Row 4: 2024-01-01| Groceries| 500   | Weekly
        ```
        """)
    
    # Connection button
    if st.button("🔗 Connect Sheet", type="primary", use_container_width=True):
        if sheet_url:
            # Show what we're trying to extract
            sheet_id = extract_sheet_id(sheet_url)
            
            if sheet_id:
                st.info(f"🔍 Connecting to sheet ID: ...{sheet_id[-8:]}")
                
                with st.spinner("🔄 Connecting..."):
                    df = read_google_sheet_csv(sheet_id)
                    
                    if df is not None:
                        expenses_df, income = parse_sheet_data(df)
                        
                        st.session_state.expenses_df = expenses_df
                        st.session_state.income = income
                        st.session_state.sheet_id = sheet_id
                        st.session_state.sheet_url = sheet_url
                        st.session_state.sheet_connected = True
                        st.session_state.last_sync = datetime.now()
                        
                        if expenses_df.empty and income == 0.0:
                            st.success("✅ Connected! Empty sheet detected - Ready for setup")
                        else:
                            st.success(f"✅ Connected! Found {len(expenses_df)} expenses, Income: ₹{income:,.0f}")
                        
                        st.rerun()
            else:
                st.error("❌ Cannot extract Sheet ID from URL!")
                st.markdown("""
                **Please make sure your URL looks like one of these:**
                - `https://docs.google.com/spreadsheets/d/1ABC...XYZ/edit#gid=0`
                - `https://docs.google.com/spreadsheets/d/1ABC...XYZ/edit`
                
                **How to get correct URL:**
                1. Open your Google Sheet in browser
                2. Copy the entire URL from address bar
                3. Paste it above
                """)
        else:
            st.error("⚠️ Please enter your Google Sheet URL!")

else:
    # Connected status
    st.markdown(f"""
    <div class="connected-box">
        ✅ <strong>Sheet Connected</strong><br>
        <small>ID: ...{st.session_state.sheet_id[-8:]}</small><br>
        <small>Last sync: {st.session_state.last_sync.strftime('%H:%M:%S') if st.session_state.last_sync else 'Never'}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Sync button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Sync", use_container_width=True):
            with st.spinner("Syncing..."):
                df = read_google_sheet_csv(st.session_state.sheet_id)
                if df is not None:
                    expenses_df, income = parse_sheet_data(df)
                    st.session_state.expenses_df = expenses_df
                    st.session_state.income = income
                    st.session_state.last_sync = datetime.now()
                    st.success("✅ Synced!")
                    st.rerun()
                else:
                    st.error("❌ Sync failed!")

# Only show dashboard and features if connected
if st.session_state.sheet_connected:
    
    # ----------------------------
    # ✅ Dashboard Section
    # ----------------------------
    
    # Calculate totals
    total_expenses = 0.0
    if not st.session_state.expenses_df.empty and 'Price' in st.session_state.expenses_df.columns:
        price_values = pd.to_numeric(st.session_state.expenses_df['Price'], errors='coerce').fillna(0)
        total_expenses = price_values.sum()
    
    remaining = st.session_state.income - total_expenses
    
    # Dashboard Cards
    st.markdown("### 📊 Dashboard")
    st.markdown(f"""
    <div class="dashboard-container">
        <div class="dashboard-card">
            <div class="dashboard-title">💚 Monthly Income</div>
            <div class="dashboard-value">₹{st.session_state.income:,.0f}</div>
        </div>
        <div class="dashboard-card">
            <div class="dashboard-title">💸 Total Spent</div>
            <div class="dashboard-value">₹{total_expenses:,.0f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    # ----------------------------
    # ✅ Income Section
    # ----------------------------
    st.markdown("### 💚 Set Income")
    col1, col2 = st.columns([3, 1])
    with col1:
        new_income = st.number_input("Monthly Income (₹)", value=st.session_state.income, min_value=0.0, step=100.0)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Save Income"):
            st.session_state.income = new_income
            st.success("✅ Income updated locally!")
            
            # Show Google Sheet update instructions
            st.markdown(f"""
            <div class="info-box">
                📝 <strong>Update your Google Sheet:</strong><br>
                Put <strong>Income</strong> in cell <strong>A1</strong><br>
                Put <strong>{int(new_income)}</strong> in cell <strong>B1</strong>
            </div>
            """, unsafe_allow_html=True)
    
    # ----------------------------
    # ✅ Add Expense Form
    # ----------------------------
    st.markdown("### 💸 Add New Expense")
    
    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            expense_date = st.date_input("📅 Date", value=date.today())
            expense_item = st.text_input("📝 Item", placeholder="e.g., Groceries")
        
        with col2:
            expense_price = st.number_input("💰 Price (₹)", min_value=0.0, step=1.0, format="%.2f")
            expense_note = st.text_input("📋 Note", placeholder="Optional")
        
        submitted = st.form_submit_button("➕ Add Expense", type="primary", use_container_width=True)
        
        if submitted:
            if expense_item.strip() and expense_price > 0:
                new_expense = {
                    'Date': expense_date,
                    'Item': expense_item.strip().title(),
                    'Price': float(expense_price),
                    'Note': expense_note.strip() if expense_note.strip() else "N/A"
                }
                
                # Add to local dataframe
                new_row = pd.DataFrame([new_expense])
                st.session_state.expenses_df = pd.concat([st.session_state.expenses_df, new_row], ignore_index=True)
                
                # Calculate row number for Google Sheet
                row_number = len(st.session_state.expenses_df) + 2  # Starting from row 3
                
                st.success("✅ Expense added to dashboard!")
                
                # Show Google Sheet update instructions
                st.markdown(f"""
                <div class="info-box">
                    📝 <strong>Add this to Google Sheet (Row {row_number}):</strong><br>
                    <strong>A{row_number}:</strong> {expense_date}<br>
                    <strong>B{row_number}:</strong> {expense_item.strip().title()}<br>
                    <strong>C{row_number}:</strong> {expense_price}<br>
                    <strong>D{row_number}:</strong> {expense_note.strip() if expense_note.strip() else "N/A"}
                </div>
                """, unsafe_allow_html=True)
                
                st.rerun()
            else:
                st.error("⚠️ Please enter item name and valid price!")
    
    # ----------------------------
    # ✅ Recent Expenses Display  
    # ----------------------------
    if not st.session_state.expenses_df.empty:
        st.markdown("### 📊 Recent Expenses")
        
        # Show last 5 expenses
        recent_expenses = st.session_state.expenses_df.tail(5).iloc[::-1]  # Newest first
        
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
        
        # Show all expenses in expandable section
        with st.expander(f"📋 View All Expenses ({len(st.session_state.expenses_df)} total)"):
            st.dataframe(
                st.session_state.expenses_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Date": st.column_config.DateColumn("📅 Date"),
                    "Item": st.column_config.TextColumn("📝 Item"),
                    "Price": st.column_config.NumberColumn("💰 Price", format="₹%.2f"),
                    "Note": st.column_config.TextColumn("📋 Note")
                }
            )
    else:
        # Show setup guide for empty sheet
        st.markdown("""
        <div class="info-box">
            🎯 <strong>Getting Started:</strong><br>
            1. Set your monthly income above<br>
            2. Add your first expense<br>  
            3. I'll show you exactly where to update your Google Sheet<br>
            4. Your data will be perfectly organized!
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 12px; margin: 20px 0;">
    💡 Keep your Google Sheet public for seamless sync • Data syncs in real-time
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
