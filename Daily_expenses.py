import streamlit as st
import pandas as pd
from datetime import datetime, date
import requests
import json
import io
from urllib.parse import urlparse, parse_qs

# Set page config for mobile
st.set_page_config(
    page_title="Mobile Budget Tracker", 
    page_icon="💰", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ✅ Mobile-First CSS
st.markdown("""
<style>
/* Hide Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {visibility: hidden;}

/* Mobile container */
.main-container {
    max-width: 100%;
    padding: 10px;
    margin: 0;
}

/* Header */
.header-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px 15px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 15px;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.header-title {
    font-size: 24px;
    margin-bottom: 5px;
}

.header-subtitle {
    font-size: 14px;
    opacity: 0.9;
}

/* Google Sheets Setup */
.gsheet-setup {
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    border: 2px dashed #4CAF50;
    padding: 20px;
    border-radius: 15px;
    margin: 15px 0;
    text-align: center;
}

.connected-sheet {
    background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
    border: 2px solid #4CAF50;
    padding: 15px;
    border-radius: 15px;
    margin: 15px 0;
    text-align: center;
}

/* Income/Expense cards */
.money-cards {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin: 15px 0;
}

.income-card {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    color: white;
    padding: 20px 15px;
    border-radius: 15px;
    text-align: center;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
}

.expense-card {
    background: linear-gradient(135deg, #fc466b 0%, #3f5efb 100%);
    color: white;
    padding: 20px 15px;
    border-radius: 15px;
    text-align: center;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(252, 70, 107, 0.3);
}

.card-title {
    font-size: 12px;
    opacity: 0.9;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.card-value {
    font-size: 20px;
    font-weight: bold;
}

/* Balance display */
.balance-display {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    margin: 15px 0;
    font-weight: bold;
    font-size: 18px;
    box-shadow: 0 4px 15px rgba(252, 182, 159, 0.3);
}

/* Form styling */
.expense-form {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    padding: 20px;
    border-radius: 20px;
    margin: 20px 0;
    box-shadow: 0 4px 15px rgba(255, 236, 210, 0.4);
}

.form-title {
    color: #333;
    font-size: 20px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 15px;
}

/* Mobile input styling */
.stNumberInput > div > div > input,
.stTextInput > div > div > input,
.stDateInput > div > div > input,
.stTextArea > div > div > textarea {
    border: 2px solid #ddd;
    border-radius: 12px;
    padding: 15px !important;
    font-size: 16px !important;
    background: white;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
}

.stNumberInput > div > div > input:focus,
.stTextInput > div > div > input:focus,
.stDateInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

/* Mobile buttons */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 15px;
    padding: 15px 25px;
    font-weight: 600;
    width: 100%;
    margin: 10px 0;
    font-size: 16px;
    height: 55px;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* Action buttons different colors */
.download-btn button {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
}

.danger-btn button {
    background: linear-gradient(135deg, #fc466b 0%, #3f5efb 100%) !important;
}

/* Statistics cards */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin: 15px 0;
}

.stat-card {
    background: white;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    border: 2px solid #f0f0f0;
}

.stat-value {
    font-size: 18px;
    font-weight: bold;
    color: #667eea;
    margin-bottom: 5px;
}

.stat-label {
    font-size: 12px;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Recent expenses */
.expense-item {
    background: white;
    border-radius: 12px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    border-left: 4px solid #667eea;
}

.expense-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.expense-item-name {
    font-weight: bold;
    color: #333;
    font-size: 16px;
}

.expense-price {
    font-weight: bold;
    color: #fc466b;
    font-size: 16px;
}

.expense-meta {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #666;
}

/* Mobile responsive */
@media (max-width: 768px) {
    .main-container {
        padding: 5px;
    }
    
    .money-cards {
        grid-template-columns: 1fr;
        gap: 8px;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
        gap: 8px;
    }
    
    .card-value {
        font-size: 18px;
    }
    
    .header-title {
        font-size: 20px;
    }
}

/* Success/Error messages */
.success-msg {
    background: linear-gradient(135deg, #d4e5d4 0%, #a8d5a8 100%);
    color: #2d5a2d;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 4px solid #4CAF50;
}

.error-msg {
    background: linear-gradient(135deg, #f8d7da 0%, #f1aeb5 100%);
    color: #721c24;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 4px solid #dc3545;
}

/* Loading spinner */
.loading {
    text-align: center;
    padding: 20px;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------
# ✅ Google Sheets Functions (Simplified for Mobile)
# ----------------------------

def extract_sheet_id(sheet_url):
    """Extract sheet ID from Google Sheets URL"""
    try:
        if '/d/' in sheet_url:
            return sheet_url.split('/d/')[1].split('/')[0]
        return sheet_url
    except:
        return None

def read_google_sheet(sheet_id, range_name='Sheet1!A:Z'):
    """Read data from Google Sheets using public access"""
    try:
        # For public sheets, we can use the CSV export URL
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        response = requests.get(csv_url, timeout=10)
        
        if response.status_code == 200:
            # Read CSV data
            df = pd.read_csv(io.StringIO(response.text))
            return df
        else:
            st.error("Unable to read sheet. Make sure it's publicly accessible!")
            return None
    except Exception as e:
        st.error(f"Error reading sheet: {e}")
        return None

def parse_budget_data(df):
    """Parse budget data from Google Sheet"""
    try:
        expenses_data = []
        income = 0.0
        
        # If sheet has our format
        if not df.empty:
            # Look for income in first few rows
            for idx, row in df.head(5).iterrows():
                if str(row.iloc[0]).lower().strip() in ['income', 'monthly income', 'salary']:
                    try:
                        income = float(row.iloc[1])
                    except:
                        income = 0.0
                    break
            
            # Look for expenses starting after income row
            expense_start_row = 0
            for idx, row in df.iterrows():
                if str(row.iloc[0]).lower().strip() in ['date', 'expense date', 'expenses']:
                    expense_start_row = idx + 1
                    break
            
            # Parse expenses
            if expense_start_row > 0:
                expenses_df = df.iloc[expense_start_row:].copy()
                expenses_df.columns = ['Date', 'Item', 'Price', 'Note']
                
                # Clean and convert data
                expenses_df = expenses_df.dropna(subset=['Date', 'Item', 'Price'])
                expenses_df['Date'] = pd.to_datetime(expenses_df['Date'], errors='coerce').dt.date
                expenses_df['Price'] = pd.to_numeric(expenses_df['Price'], errors='coerce').fillna(0)
                expenses_df['Note'] = expenses_df['Note'].fillna('N/A')
                
                return expenses_df, income
        
        # If no structured data found, return empty
        return pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note']), income
        
    except Exception as e:
        st.error(f"Error parsing data: {e}")
        return pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note']), 0.0

# ----------------------------
# ✅ Local Save Functions
# ----------------------------

def save_to_excel(expenses_df, income):
    """Save data to Excel for local download"""
    try:
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Save expenses
            expenses_df.to_excel(writer, sheet_name='Expenses', index=False)
            
            # Save metadata
            metadata_df = pd.DataFrame({
                'Parameter': ['Income', 'Total_Expenses', 'Balance', 'Last_Updated'],
                'Value': [
                    income,
                    expenses_df['Price'].sum() if not expenses_df.empty else 0,
                    income - (expenses_df['Price'].sum() if not expenses_df.empty else 0),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ]
            })
            metadata_df.to_excel(writer, sheet_name='Summary', index=False)
        
        return buffer.getvalue()
    except Exception as e:
        st.error(f"Error creating Excel file: {e}")
        return None

def create_csv_for_gsheet(expenses_df, income):
    """Create CSV format for easy copy to Google Sheets"""
    try:
        # Create a formatted sheet structure
        output = []
        output.append(['Mobile Budget Tracker Data'])
        output.append([''])
        output.append(['Income', income])
        output.append([''])
        output.append(['Date', 'Item', 'Price', 'Note'])
        
        # Add expenses
        for _, row in expenses_df.iterrows():
            output.append([
                row['Date'].strftime('%Y-%m-%d') if pd.notnull(row['Date']) else '',
                row['Item'],
                row['Price'],
                row['Note']
            ])
        
        # Convert to CSV
        csv_buffer = io.StringIO()
        pd.DataFrame(output).to_csv(csv_buffer, index=False, header=False)
        return csv_buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error creating CSV: {e}")
        return None

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

if 'last_sync' not in st.session_state:
    st.session_state.last_sync = None

# ----------------------------
# ✅ Main App
# ----------------------------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-box">
    <div class="header-title">💰 Mobile Budget Tracker</div>
    <div class="header-subtitle">Google Sheets + Local Download</div>
</div>
""", unsafe_allow_html=True)

# ----------------------------
# ✅ Google Sheets Connection
# ----------------------------
if not st.session_state.sheet_connected:
    st.markdown("""
    <div class="gsheet-setup">
        📊 Connect Your Google Sheet
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📋 Quick Setup Guide", expanded=True):
        st.markdown("""
        ### 📱 Mobile Setup (Easy Way):
        
        **Step 1: Create Google Sheet**
        1. Open Google Sheets app on your phone
        2. Create new sheet named "My Budget"
        3. In cell A1 type: "Income"
        4. In cell B1 type your monthly income (e.g., 50000)
        5. In cell A3 type: "Date"
        6. In cell B3 type: "Item" 
        7. In cell C3 type: "Price"
        8. In cell D3 type: "Note"
        
        **Step 2: Make Sheet Public**
        1. Tap Share button (top right)
        2. Tap "Change to anyone with the link"
        3. Set to "Viewer" 
        4. Copy the link
        
        **Step 3: Paste Link Below**
        """)
    
    # Sheet URL input
    sheet_url = st.text_input(
        "🔗 Paste your Google Sheet link here:",
        placeholder="https://docs.google.com/spreadsheets/d/your-sheet-id/edit...",
        help="Make sure your sheet is public (anyone with link can view)"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Connect Sheet", use_container_width=True):
            if sheet_url:
                sheet_id = extract_sheet_id(sheet_url)
                if sheet_id:
                    with st.spinner("Connecting to your sheet..."):
                        df = read_google_sheet(sheet_id)
                        
                        if df is not None:
                            expenses_df, income = parse_budget_data(df)
                            st.session_state.expenses_df = expenses_df
                            st.session_state.income = income
                            st.session_state.sheet_id = sheet_id
                            st.session_state.sheet_connected = True
                            st.session_state.last_sync = datetime.now()
                            
                            st.success("✅ Sheet connected successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Could not connect to sheet!")
                else:
                    st.error("❌ Invalid sheet URL!")
            else:
                st.error("❌ Please enter sheet URL!")
    
    with col2:
        if st.button("📱 Skip & Start Fresh", use_container_width=True):
            st.session_state.sheet_connected = True
            st.info("✅ Started without Google Sheet connection!")
            st.rerun()

else:
    # Connected - show main app
    if st.session_state.sheet_id:
        st.markdown(f"""
        <div class="connected-sheet">
            ✅ Connected to Google Sheet<br>
            <small>Last sync: {st.session_state.last_sync.strftime('%H:%M') if st.session_state.last_sync else 'Never'}</small>
        </div>
        """, unsafe_allow_html=True)
    
    # ----------------------------
    # ✅ Income & Balance Display
    # ----------------------------
    
    # Income input (compact for mobile)
    st.markdown("**💚 Monthly Income:**")
    col1, col2 = st.columns([3, 1])
    with col1:
        new_income = st.number_input("", value=st.session_state.income, min_value=0.0, step=500.0, label_visibility="collapsed")
    with col2:
        if st.button("💾", help="Save Income"):
            st.session_state.income = new_income
            st.success("Saved!")
    
    # Calculate totals
    total_expenses = 0.0
    if not st.session_state.expenses_df.empty and 'Price' in st.session_state.expenses_df.columns:
        total_expenses = pd.to_numeric(st.session_state.expenses_df['Price'], errors='coerce').fillna(0).sum()
    
    remaining = st.session_state.income - total_expenses
    
    # Money cards
    st.markdown(f"""
    <div class="money-cards">
        <div class="income-card">
            <div class="card-title">💚 Income</div>
            <div class="card-value">₹{st.session_state.income:,.0f}</div>
        </div>
        <div class="expense-card">
            <div class="card-title">💸 Expenses</div>
            <div class="card-value">₹{total_expenses:,.0f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Balance
    balance_color = "#11998e" if remaining >= 0 else "#fc466b"
    balance_icon = "✅" if remaining >= 0 else "⚠️"
    
    st.markdown(f"""
    <div class="balance-display" style="border-left: 5px solid {balance_color};">
        {balance_icon} Balance: <span style="color: {balance_color};">₹{remaining:,.0f}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # ----------------------------
    # ✅ Add Expense Form (Mobile Optimized)
    # ----------------------------
    st.markdown("""
    <div class="expense-form">
        <div class="form-title">💸 Add New Expense</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("mobile_expense_form", clear_on_submit=True):
        # Single column layout for mobile
        expense_date = st.date_input("📅 Date", value=date.today())
        
        expense_item = st.text_input("🛍️ What did you buy?", placeholder="e.g., Groceries, Petrol, Coffee")
        
        expense_price = st.number_input("💰 How much? (₹)", min_value=0.0, step=10.0, format="%.0f")
        
        expense_note = st.text_input("📝 Quick Note (optional)", placeholder="Any extra details...")
        
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
                
                st.markdown("""
                <div class="success-msg">
                    ✅ Expense added successfully!
                </div>
                """, unsafe_allow_html=True)
                
                st.rerun()
            else:
                st.markdown("""
                <div class="error-msg">
                    ❌ Please enter item name and price!
                </div>
                """, unsafe_allow_html=True)
    
    # ----------------------------
    # ✅ Statistics & Recent Expenses
    # ----------------------------
    if not st.session_state.expenses_df.empty:
        # Statistics
        total_items = len(st.session_state.expenses_df)
        avg_expense = st.session_state.expenses_df['Price'].mean()
        max_expense = st.session_state.expenses_df['Price'].max()
        
        st.markdown(f"""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{total_items}</div>
                <div class="stat-label">Total Items</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">₹{avg_expense:.0f}</div>
                <div class="stat-label">Average</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">₹{max_expense:.0f}</div>
                <div class="stat-label">Highest</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Recent expenses
        st.markdown("### 📋 Recent Expenses")
        
        # Show last 5 expenses
        recent_expenses = st.session_state.expenses_df.tail(5).sort_values('Date', ascending=False)
        
        for idx, expense in recent_expenses.iterrows():
            date_str = expense['Date'].strftime('%b %d') if pd.notnull(expense['Date']) else 'No Date'
            
            st.markdown(f"""
            <div class="expense-item">
                <div class="expense-header">
                    <div class="expense-item-name">{expense['Item']}</div>
                    <div class="expense-price">₹{expense['Price']:,.0f}</div>
                </div>
                <div class="expense-meta">
                    <div>📅 {date_str}</div>
                    <div>📝 {expense['Note']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if len(st.session_state.expenses_df) > 5:
            st.info(f"Showing recent 5 expenses. Total: {len(st.session_state.expenses_df)} expenses")
    
    # ----------------------------
    # ✅ Action Buttons
    # ----------------------------
    st.markdown("---")
    
    # Sync button (if connected)
    if st.session_state.sheet_id:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Sync from Sheet", use_container_width=True):
                with st.spinner("Syncing..."):
                    df = read_google_sheet(st.session_state.sheet_id)
                    if df is not None:
                        expenses_df, income = parse_budget_data(df)
                        st.session_state.expenses_df = expenses_df
                        st.session_state.income = income
                        st.session_state.last_sync = datetime.now()
                        st.success("✅ Data synced!")
                        st.rerun()
        
        with col2:
            if st.button("📤 Copy to Sheet", use_container_width=True):
                csv_data = create_csv_for_gsheet(st.session_state.expenses_df, st.session_state.income)
                if csv_data:
                    st.text_area("📋 Copy this data to your Google Sheet:", csv_data, height=100)
    
    # Download buttons
    st.markdown("### 📱 Download Your Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not st.session_state.expenses_df.empty or st.session_state.income > 0:
            excel_data = save_to_excel(st.session_state.expenses_df, st.session_state.income)
            if excel_data:
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name=f"budget_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
    
    with col2:
        if not st.session_state.expenses_df.empty or st.session_state.income > 0:
            csv_data = create_csv_for_gsheet(st.session_state.expenses_df, st.session_state.income)
            if csv_data:
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"budget_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    # Clear data button
    if st.button("🗑️ Clear All Data", use_container_width=True):
        st.session_state.expenses_df = pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note'])
        st.session_state.income = 0.0
        st.success("✅ All data cleared!")
        st.rerun()
    
    # Disconnect sheet
    if st.session_state.sheet_id:
        if st.button("🔌 Disconnect Sheet", use_container_width=True):
            st.session_state.sheet_id = ""
            st.session_state.sheet_connected = False
            st.success("✅ Disconnected from Google Sheet!")
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px; padding: 10px;">
    📱 <strong>Mobile Budget Tracker</strong><br>
    Google Sheets sync • Local downloads • Always accessible
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
