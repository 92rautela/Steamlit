import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import tempfile
import io
import requests
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

.gsheet-section {
    background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
    border: 2px dashed #2196F3;
    padding: 15px;
    border-radius: 10px;
    margin: 15px 0;
    text-align: center;
}

.gsheet-connected {
    background: linear-gradient(135deg, #E8F5E8, #C8E6C9);
    border: 2px solid #4CAF50;
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

.gsheet-btn button {
    background: linear-gradient(135deg, #2196F3, #1976D2) !important;
}

.sync-btn button {
    background: linear-gradient(135deg, #4CAF50, #388E3C) !important;
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
# ✅ Google Sheets Functions
# ----------------------------

def extract_sheet_id(sheet_url):
    """Extract Google Sheet ID from URL"""
    try:
        # Pattern to match Google Sheets URL
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
            # Create DataFrame from CSV
            df = pd.read_csv(io.StringIO(response.text))
            return df
        else:
            st.error("❌ Cannot access sheet. Make sure it's public!")
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
                        # Look for number in same row or next column
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
            # Try to map columns
            expenses_df = df.iloc[header_row + 1:].copy()

            # Reset columns based on content
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

                # Rename columns if mapping found
                if len(col_mapping) >= 3:
                    expenses_df = expenses_df.rename(columns=col_mapping)
                else:
                    # Fallback: assume first 4 columns are Date, Item, Price, Note
                    new_cols = ['Date', 'Item', 'Price', 'Note']
                    old_cols = list(df.columns)[:4]
                    for i, new_col in enumerate(new_cols):
                        if i < len(old_cols):
                            expenses_df = expenses_df.rename(columns={old_cols[i]: new_col})

                # Clean data
                required_cols = ['Date', 'Item', 'Price']
                if all(col in expenses_df.columns for col in required_cols):
                    # Remove empty rows
                    expenses_df = expenses_df.dropna(subset=['Item', 'Price'])

                    # Convert data types
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


def create_gsheet_format_data(expenses_df, income):
    """Create formatted data ready for Google Sheets"""
    try:
        formatted_data = []

        # Add title and income
        formatted_data.append(['Budget Tracker Data', '', '', ''])
        formatted_data.append(['', '', '', ''])
        formatted_data.append(['Income', income, '', ''])
        formatted_data.append(['', '', '', ''])

        # Add expenses header
        formatted_data.append(['Date', 'Item', 'Price', 'Note'])

        # Add expenses data
        for _, row in expenses_df.iterrows():
            formatted_data.append([
                row['Date'].strftime('%Y-%m-%d') if pd.notnull(row['Date']) else '',
                str(row['Item']),
                float(row['Price']),
                str(row['Note'])
            ])

        return formatted_data

    except Exception as e:
        st.error(f"Error formatting data: {e}")
        return []


# ----------------------------
# ✅ Local File Functions
# ----------------------------
PERSISTENT_FILE = os.path.join(tempfile.gettempdir(), "budget_tracker_expenses.csv")
INCOME_FILE = os.path.join(tempfile.gettempdir(), "budget_tracker_income.csv")


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

if 'sheet_id' not in st.session_state:
    st.session_state.sheet_id = ""

if 'sheet_connected' not in st.session_state:
    st.session_state.sheet_connected = False

if 'last_sync' not in st.session_state:
    st.session_state.last_sync = None

if 'income_saved' not in st.session_state:
    st.session_state.income_saved = False

# ----------------------------
# ✅ Header
# ----------------------------
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown("""
<div class="header-box">
    💰 Personal Budget Tracker 💰<br>
    <small>With Google Sheets Integration</small>
</div>
""", unsafe_allow_html=True)

# ----------------------------
# ✅ Google Sheets Connection Section
# ----------------------------
if not st.session_state.sheet_connected:
    st.markdown("""
    <div class="gsheet-section">
        📊 Connect Your Google Sheet
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📋 Setup Instructions", expanded=True):
        st.markdown("""
        ### Quick Setup:

        **Step 1: Prepare Google Sheet**
        1. Create a new Google Sheet
        2. Make it **public** (Share > Anyone with link > Viewer)
        3. Structure (optional):
           - Row 1: Income, [your income amount]
           - Row 4: Date, Item, Price, Note
           - Row 5+: Your expense data

        **Step 2: Get Sheet Link**
        1. Copy the sheet URL from browser
        2. Paste it below

        **Step 3: Connect**
        - App will auto-detect your data structure
        - Import existing expenses and income
        """)

    # Sheet URL Input
    sheet_url = st.text_input(
        "🔗 Paste your Google Sheet URL:",
        placeholder="https://docs.google.com/spreadsheets/d/your-sheet-id/edit...",
        value=st.session_state.sheet_id if st.session_state.sheet_id else ""
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔗 Connect Sheet", key="connect_sheet", use_container_width=True):
            if sheet_url:
                sheet_id = extract_sheet_id(sheet_url)
                if sheet_id:
                    with st.spinner("Connecting to Google Sheet..."):
                        df = read_google_sheet_csv(sheet_id)

                        if df is not None:
                            expenses_df, income = parse_sheet_data(df)

                            st.session_state.expenses_df = expenses_df
                            st.session_state.income = income
                            st.session_state.sheet_id = sheet_id
                            st.session_state.sheet_connected = True
                            st.session_state.last_sync = datetime.now()

                            # Save to local files
                            save_to_csv(expenses_df)
                            save_income(income)

                            st.success("✅ Sheet connected successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to read sheet data!")
                else:
                    st.error("❌ Invalid Google Sheet URL!")
            else:
                st.error("⚠️ Please enter Google Sheet URL!")

    with col2:
        if st.button("⏭️ Skip for Now", key="skip_sheet", use_container_width=True):
            st.session_state.sheet_connected = True
            st.info("✅ Skipped Google Sheets. You can connect later!")
            st.rerun()

else:
    # Sheet Connected - Show status and sync option
    if st.session_state.sheet_id:
        st.markdown(f"""
        <div class="gsheet-connected">
            ✅ <strong>Google Sheet Connected</strong><br>
            <small>Sheet ID: ...{st.session_state.sheet_id[-8:]}</small><br>
            <small>Last sync: {st.session_state.last_sync.strftime('%H:%M:%S') if st.session_state.last_sync else 'Never'}</small>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 Sync from Sheet", key="sync_sheet", use_container_width=True):
                with st.spinner("Syncing from Google Sheet..."):
                    df = read_google_sheet_csv(st.session_state.sheet_id)
                    if df is not None:
                        expenses_df, income = parse_sheet_data(df)
                        st.session_state.expenses_df = expenses_df
                        st.session_state.income = income
                        st.session_state.last_sync = datetime.now()

                        # Save to local files
                        save_to_csv(expenses_df)
                        save_income(income)

                        st.success("✅ Data synced from Google Sheet!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to sync from sheet!")

        with col2:
            if st.button("📤 Show Export Data", key="export_data", use_container_width=True):
                formatted_data = create_gsheet_format_data(st.session_state.expenses_df, st.session_state.income)
                if formatted_data:
                    # Convert to DataFrame for display
                    export_df = pd.DataFrame(formatted_data)
                    st.markdown("**Copy this data to your Google Sheet:**")
                    st.dataframe(export_df, use_container_width=True, hide_index=True)

                    # Also provide as CSV
                    csv_data = export_df.to_csv(index=False, header=False)
                    st.download_button(
                        label="📥 Download CSV for Sheet",
                        data=csv_data,
                        file_name=f"budget_for_gsheet_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

# ----------------------------
# ✅ Income Input and Total Display
# ----------------------------
total_expenses = 0.0
if not st.session_state.expenses_df.empty and 'Price' in st.session_state.expenses_df.columns:
    price_values = pd.to_numeric(st.session_state.expenses_df['Price'], errors='coerce').fillna(0)
    total_expenses = price_values.sum()

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

            if save_to_csv(st.session_state.expenses_df):
                st.success("✅ Expense added and saved!")
                st.info("💡 Don't forget to update your Google Sheet with new data!")
                st.rerun()
            else:
                st.error("❌ Error saving expense!")
        else:
            st.error("⚠️ Please enter item name and valid price!")

# ----------------------------
# ✅ Display & Editable Expenses
# ----------------------------
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
        if not updated_df.equals(
                st.session_state.expenses_df.sort_values('Date', ascending=False).reset_index(drop=True)):
            st.session_state.expenses_df = updated_df.reset_index(drop=True)
            save_to_csv(st.session_state.expenses_df)
            st.info("🔄 Changes saved locally!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 12px;">
    💡 <strong>Tips:</strong> Keep your Google Sheet public for easy sync • 
    Export data regularly • Local data auto-saves
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

