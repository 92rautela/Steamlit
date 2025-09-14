import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

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
</style>
""", unsafe_allow_html=True)

# ----------------------------
# ✅ Google Sheets API Functions
# ----------------------------

@st.cache_resource
def get_gspread_client():
    """Get authenticated gspread client"""
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        return client
    except FileNotFoundError:
        st.error("❌ credentials.json file not found! Please add it to your project folder.")
        return None
    except Exception as e:
        st.error(f"❌ Error creating client: {str(e)}")
        return None

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

def connect_to_sheet(sheet_url):
    """Connect to Google Sheet using API"""
    try:
        client = get_gspread_client()
        if not client:
            return None, "❌ Failed to create Google Sheets client"
        
        # Extract sheet ID
        sheet_id = extract_sheet_id(sheet_url)
        if not sheet_id:
            return None, "❌ Invalid Google Sheets URL"
        
        # Open sheet
        sheet = client.open_by_key(sheet_id).sheet1
        return sheet, "✅ Successfully connected to Google Sheet!"
        
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg:
            return None, "❌ Permission denied. Please share sheet with service account email."
        elif "404" in error_msg:
            return None, "❌ Sheet not found. Check URL and permissions."
        else:
            return None, f"❌ Connection error: {error_msg}"

def read_sheet_data(sheet):
    """Read data from Google Sheet"""
    try:
        # Get all data
        records = sheet.get_all_records()
        
        # Initialize
        expenses_data = []
        income = 0.0
        
        # Find income (look for Income keyword in first few rows)
        all_values = sheet.get_all_values()
        for i, row in enumerate(all_values[:5]):  # Check first 5 rows
            for j, cell in enumerate(row):
                if cell.lower().strip() in ['income', 'salary', 'earning']:
                    try:
                        # Look for number in next cell or same row
                        if j + 1 < len(row):
                            income = float(str(row[j + 1]).replace(',', '').replace('₹', '').strip())
                        break
                    except:
                        pass
        
        # Process expenses (skip first few rows that might contain income)
        if records:
            for record in records:
                # Skip rows that contain income keywords
                row_text = ' '.join(str(v).lower() for v in record.values())
                if any(word in row_text for word in ['income', 'salary', 'earning']):
                    continue
                
                # Try to extract expense data
                try:
                    # Look for date, item, price pattern
                    date_val = None
                    item_val = None
                    price_val = None
                    note_val = "N/A"
                    
                    for key, value in record.items():
                        key_lower = str(key).lower()
                        value_str = str(value).strip()
                        
                        if not value_str or value_str == '':
                            continue
                            
                        # Date detection
                        if any(word in key_lower for word in ['date', 'day', 'when']) and not date_val:
                            try:
                                date_val = pd.to_datetime(value_str).date()
                            except:
                                pass
                        
                        # Item detection
                        elif any(word in key_lower for word in ['item', 'name', 'what', 'description']) and not item_val:
                            item_val = value_str
                        
                        # Price detection
                        elif any(word in key_lower for word in ['price', 'amount', 'cost', 'money', 'expense']) and not price_val:
                            try:
                                price_val = float(str(value_str).replace(',', '').replace('₹', ''))
                            except:
                                pass
                        
                        # Note detection
                        elif any(word in key_lower for word in ['note', 'remark', 'detail', 'comment']):
                            note_val = value_str
                    
                    # If we have at least item and price, add to expenses
                    if item_val and price_val and price_val > 0:
                        if not date_val:
                            date_val = date.today()
                        
                        expenses_data.append({
                            'Date': date_val,
                            'Item': item_val,
                            'Price': price_val,
                            'Note': note_val
                        })
                
                except Exception as e:
                    continue
        
        expenses_df = pd.DataFrame(expenses_data)
        return expenses_df, income
        
    except Exception as e:
        st.error(f"Error reading sheet: {str(e)}")
        return pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note']), 0.0

def add_expense_to_sheet(sheet, expense_data):
    """Add expense to Google Sheet"""
    try:
        # Get current data to find next row
        values = sheet.get_all_values()
        next_row = len(values) + 1
        
        # Format data for sheet
        row_data = [
            str(expense_data['Date']),
            expense_data['Item'],
            expense_data['Price'],
            expense_data['Note']
        ]
        
        # Add to sheet
        sheet.append_row(row_data)
        return True, f"✅ Added to Google Sheet at row {next_row}"
        
    except Exception as e:
        return False, f"❌ Error adding to sheet: {str(e)}"

def update_income_in_sheet(sheet, income_value):
    """Update income in Google Sheet"""
    try:
        # Update income in A1 and B1
        sheet.update('A1', 'Income')
        sheet.update('B1', income_value)
        return True, "✅ Income updated in Google Sheet"
    except Exception as e:
        return False, f"❌ Error updating income: {str(e)}"

def setup_sheet_headers(sheet):
    """Setup headers in Google Sheet"""
    try:
        # Check if headers already exist
        first_row = sheet.row_values(1)
        if not first_row or first_row == ['', '', '', '']:
            # Add income in first row
            sheet.update('A1', 'Income')
            sheet.update('B1', 0)
            
            # Add expense headers in second row
            sheet.update('A2:D2', [['Date', 'Item', 'Price', 'Note']])
            return True, "✅ Headers added to Google Sheet"
        return True, "✅ Headers already exist"
    except Exception as e:
        return False, f"❌ Error setting up headers: {str(e)}"

# ----------------------------
# ✅ Session State Initialization
# ----------------------------
if 'expenses_df' not in st.session_state:
    st.session_state.expenses_df = pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note'])

if 'income' not in st.session_state:
    st.session_state.income = 0.0

if 'sheet' not in st.session_state:
    st.session_state.sheet = None

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
        <div class="live-indicator">🟢 API LIVE</div>
        💰 Personal Budget Tracker<br>
        <small>Google Sheets API Integration</small>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="header-box">
        💰 Personal Budget Tracker<br>
        <small>Connect to Google Sheets via API</small>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------
# ✅ Connection Section
# ----------------------------
st.markdown("### 🔗 Google Sheet Connection")

# URL input
sheet_url = st.text_input(
    "Google Sheet URL:",
    placeholder="https://docs.google.com/spreadsheets/d/your-sheet-id/edit...",
    value=st.session_state.sheet_url,
    help="Paste your Google Sheet URL here"
)

if not st.session_state.sheet_connected:
    # Connection instructions
    with st.expander("📋 Setup Instructions"):
        st.markdown("""
        **Before connecting:**
        1. Make sure `credentials.json` is in your project folder
        2. Share your Google Sheet with service account email from credentials.json
        3. Give Editor permission to the service account
        
        **Service Account Email:** Check your credentials.json file for `client_email`
        """)
    
    # Connect button
    if st.button("🔗 Connect to Sheet", type="primary", use_container_width=True):
        if sheet_url:
            with st.spinner("🔄 Connecting via API..."):
                sheet, message = connect_to_sheet(sheet_url)
                
                if sheet:
                    # Setup headers if needed
                    setup_success, setup_msg = setup_sheet_headers(sheet)
                    
                    # Read existing data
                    expenses_df, income = read_sheet_data(sheet)
                    
                    # Update session state
                    st.session_state.sheet = sheet
                    st.session_state.expenses_df = expenses_df
                    st.session_state.income = income
                    st.session_state.sheet_url = sheet_url
                    st.session_state.sheet_connected = True
                    st.session_state.last_sync = datetime.now()
                    
                    st.success(message)
                    if setup_success:
                        st.info(setup_msg)
                    
                    if not expenses_df.empty:
                        st.success(f"📊 Found {len(expenses_df)} expenses, Income: ₹{income:,.0f}")
                    
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.error("⚠️ Please enter your Google Sheet URL!")

else:
    # Connected status
    st.markdown(f"""
    <div class="connected-box">
        ✅ <strong>Connected via API</strong><br>
        <small>Last sync: {st.session_state.last_sync.strftime('%H:%M:%S') if st.session_state.last_sync else 'Never'}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Sync and disconnect buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Sync Data", use_container_width=True):
            with st.spinner("Syncing from sheet..."):
                expenses_df, income = read_sheet_data(st.session_state.sheet)
                st.session_state.expenses_df = expenses_df
                st.session_state.income = income
                st.session_state.last_sync = datetime.now()
                st.success("✅ Data synced!")
                st.rerun()
    
    with col2:
        if st.button("🔌 Disconnect", use_container_width=True):
            st.session_state.sheet_connected = False
            st.session_state.sheet = None
            st.session_state.sheet_url = ""
            st.success("✅ Disconnected!")
            st.rerun()

# Only show dashboard and features if connected
if st.session_state.sheet_connected:
    
    # Calculate totals
    total_expenses = 0.0
    if not st.session_state.expenses_df.empty:
        total_expenses = st.session_state.expenses_df['Price'].sum()
    
    remaining = st.session_state.income - total_expenses
    
    # Dashboard
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
    
    # Balance
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
    
    # Income Section
    st.markdown("### 💚 Set Income")
    col1, col2 = st.columns([3, 1])
    with col1:
        new_income = st.number_input("Monthly Income (₹)", value=st.session_state.income, min_value=0.0, step=100.0)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Update Income"):
            success, message = update_income_in_sheet(st.session_state.sheet, new_income)
            if success:
                st.session_state.income = new_income
                st.success(message)
            else:
                st.error(message)
    
    # Add Expense Form
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
                expense_data = {
                    'Date': expense_date,
                    'Item': expense_item.strip().title(),
                    'Price': float(expense_price),
                    'Note': expense_note.strip() if expense_note.strip() else "N/A"
                }
                
                # Add to Google Sheet
                success, message = add_expense_to_sheet(st.session_state.sheet, expense_data)
                
                if success:
                    # Add to local dataframe
                    new_row = pd.DataFrame([expense_data])
                    st.session_state.expenses_df = pd.concat([st.session_state.expenses_df, new_row], ignore_index=True)
                    
                    st.success(message)
                    st.balloons()
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("⚠️ Please enter item name and valid price!")
    
    # Show expenses
    if not st.session_state.expenses_df.empty:
        with st.expander(f"📋 View All Expenses ({len(st.session_state.expenses_df)} total)", expanded=True):
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
    # Setup guide for new users
    st.markdown("""
    <div class="info-box">
        🎯 <strong>Getting Started:</strong><br>
        1. Add your credentials.json file to project folder<br>
        2. Share your Google Sheet with service account email<br>
        3. Connect using the URL above<br>
        4. Start tracking your expenses automatically!<br>
        <br>
        <strong>✨ Features:</strong><br>
        • Real-time sync with Google Sheets<br>
        • Automatic data backup<br>
        • Beautiful dashboard<br>
        • Works on any device
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 12px; margin: 20px 0;">
    🔗 Powered by Google Sheets API • Real-time sync • Secure authentication
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
