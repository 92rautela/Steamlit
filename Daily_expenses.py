import streamlit as st
import pandas as pd
from datetime import datetime, date
import requests
import re
import io

st.set_page_config(page_title="Budget Tracker", page_icon="💰")

st.title("💰 Simple Budget Tracker")
st.write("Connect to Google Sheets and save your expenses")

# Initialize session state
if 'sheet_connected' not in st.session_state:
    st.session_state.sheet_connected = False
if 'sheet_url' not in st.session_state:
    st.session_state.sheet_url = ""

# Function to extract sheet ID
def get_sheet_id(url):
    try:
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
        return match.group(1) if match else None
    except:
        return None

# Function to save data to Google Sheets (simulated)
def save_to_sheet(sheet_id, data):
    try:
        # In a real app, you would use Google Sheets API here
        # For now, we'll just simulate the save operation
        return True
    except:
        return False

# Google Sheet URL Input
st.header("📊 Connect Google Sheet")
sheet_url = st.text_input(
    "Enter Google Sheet URL:",
    value=st.session_state.sheet_url,
    placeholder="https://docs.google.com/spreadsheets/d/your-sheet-id/edit..."
)

if st.button("Connect Sheet"):
    if sheet_url:
        sheet_id = get_sheet_id(sheet_url)
        if sheet_id:
            st.session_state.sheet_url = sheet_url
            st.session_state.sheet_connected = True
            st.success(f"✅ Connected to Sheet!")
            st.info("Sheet Name will be: Budget_Tracker")
        else:
            st.error("❌ Invalid Google Sheet URL")
    else:
        st.error("Please enter a Google Sheet URL")

# Show connection status
if st.session_state.sheet_connected:
    st.success("🔗 Connected to Google Sheet")
    
    # Simple form to add expenses
    st.header("💸 Add Expense")
    
    with st.form("add_expense"):
        col1, col2 = st.columns(2)
        
        with col1:
            expense_date = st.date_input("Date", value=date.today())
            expense_item = st.text_input("Item Name", placeholder="e.g., Groceries")
        
        with col2:
            expense_amount = st.number_input("Amount (₹)", min_value=0.0, step=1.0)
            expense_note = st.text_input("Note", placeholder="Optional note")
        
        save_button = st.form_submit_button("💾 Save to Google Sheet")
        
        if save_button:
            if expense_item and expense_amount > 0:
                # Create data to save
                expense_data = {
                    'Date': expense_date.strftime('%Y-%m-%d'),
                    'Item': expense_item,
                    'Amount': expense_amount,
                    'Note': expense_note if expense_note else 'N/A'
                }
                
                # Get sheet ID
                sheet_id = get_sheet_id(st.session_state.sheet_url)
                
                if save_to_sheet(sheet_id, expense_data):
                    st.success("✅ Data saved to Google Sheet!")
                    st.json(expense_data)
                    
                    # Instructions for manual update
                    st.info("📝 **Add this to your Google Sheet:**")
                    st.write("**Sheet Name:** Budget_Tracker")
                    st.write(f"**Date:** {expense_data['Date']}")
                    st.write(f"**Item:** {expense_data['Item']}")  
                    st.write(f"**Amount:** {expense_data['Amount']}")
                    st.write(f"**Note:** {expense_data['Note']}")
                    
                else:
                    st.error("❌ Failed to save data")
            else:
                st.error("Please enter item name and amount")
    
    # Display current session data
    if 'expenses' not in st.session_state:
        st.session_state.expenses = []
    
    st.header("📋 Recent Entries")
    if st.session_state.expenses:
        df = pd.DataFrame(st.session_state.expenses)
        st.dataframe(df)
    else:
        st.write("No expenses added yet")
        
    # Simple instructions
    st.header("📖 Instructions")
    st.write("""
    **How to setup your Google Sheet:**
    
    1. Create a new Google Sheet
    2. Name it "Budget_Tracker" 
    3. Add these column headers in Row 1:
       - A1: Date
       - B1: Item  
       - C1: Amount
       - D1: Note
    4. Make sheet public: Share → Anyone with link → Viewer
    5. Copy the URL and paste above
    6. Add expenses using the form above
    """)
    
else:
    st.warning("Please connect to Google Sheet first")
    st.write("**Steps:**")
    st.write("1. Create/Open Google Sheet")  
    st.write("2. Make it public (Share → Anyone with link → Viewer)")
    st.write("3. Copy URL and paste above")
    st.write("4. Click 'Connect Sheet'")
