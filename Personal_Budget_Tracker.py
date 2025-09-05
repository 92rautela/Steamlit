import streamlit as st
import pandas as pd
from datetime import datetime, date
import io

# Custom CSS
st.markdown("""
<style>
/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main container */
.main-container {
    max-width: 400px;
    margin: 20px auto;
    padding: 0;
}

/* Header styling */
.header-box {
    background: linear-gradient(135deg, #8B5CF6, #A855F7);
    color: white;
    padding: 15px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 20px;
    font-weight: bold;
}

/* Section headers */
.section-header {
    color: #4B5563;
    font-size: 16px;
    font-weight: 600;
    margin: 20px 0 10px 0;
    display: flex;
    align-items: center;
}

/* Input styling */
.stNumberInput > div > div > input,
.stTextInput > div > div > input,
.stDateInput > div > div > input {
    border: 1px solid #D1D5DB;
    border-radius: 8px;
    padding: 12px;
    font-size: 16px;
}

/* Button styling */
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'income' not in st.session_state:
    st.session_state.income = 0.0
if 'expenses_df' not in st.session_state:
    st.session_state.expenses_df = pd.DataFrame(columns=['Date', 'Item', 'Price', 'Note'])

# Main container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-box">
    💰💰💰 Personal Budget Tracker 💰💰💰 
</div>
""", unsafe_allow_html=True)

# Add Daily Expense Section
st.markdown("""
<div class="section-header">
    💸 Add Daily Expense
</div>
""", unsafe_allow_html=True)

# Expense Form
with st.form("expense_form", clear_on_submit=True):
    st.markdown("**Date:**")
    expense_date = st.date_input("", value=date.today(), label_visibility="collapsed")

    st.markdown("**Item Name:**")
    expense_item = st.text_input("", placeholder="e.g., milk", label_visibility="collapsed")
    if expense_item:
        expense_item = expense_item.title()

    st.markdown("**Price (₹):**")
    expense_price = st.number_input("", min_value=0.0, step=1.0, label_visibility="collapsed")

    st.markdown("**Note:** *(optional)*")
    expense_note = st.text_input("", placeholder="Additional details", label_visibility="collapsed", key="note_input")

    submitted = st.form_submit_button("Submit")

    if submitted:
        if expense_item and expense_price > 0:
            new_expense = pd.DataFrame({
                'Date': [expense_date],
                'Item': [expense_item],
                'Price': [expense_price],
                'Note': [expense_note if expense_note else "N/A"]
            })
            st.session_state.expenses_df = pd.concat([st.session_state.expenses_df, new_expense], ignore_index=True)
            st.success("✅ Expense added successfully!")
        else:
            st.error("Please fill in all required fields!")

st.markdown('</div>', unsafe_allow_html=True)

# Show recent expenses (optional - can be removed)
if not st.session_state.expenses_df.empty:
    st.markdown("---")
    st.markdown("### Recent Expenses")
    recent = st.session_state.expenses_df.tail(5)
    st.dataframe(recent, use_container_width=True, hide_index=True)

    # Quick download
    csv_data = st.session_state.expenses_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Data",
        data=csv_data,
        file_name=f"expenses_{datetime.now().strftime('%Y_%m')}.csv",
        mime="text/csv"
    )
