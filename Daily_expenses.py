import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="💰 Expense Tracker",
    page_icon="📒",
    layout="wide"
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'supabase_client' not in st.session_state:
    st.session_state.supabase_client = None


def login_page():
    """Display login page"""
    st.title("🔐 Login to Expense Tracker")

    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("### Enter your Supabase credentials")

            # Login form
            with st.form("login_form"):
                url = st.text_input(
                    "Supabase URL",
                    placeholder="https://your-project.supabase.co",
                    help="Your Supabase project URL"
                )
                key = st.text_input(
                    "Supabase API Key",
                    type="password",
                    placeholder="Your anon/public API key",
                    help="Your Supabase anon key"
                )

                login_button = st.form_submit_button("🚀 Login", use_container_width=True)

                if login_button:
                    if url and key:
                        try:
                            # Test connection
                            supabase_client = create_client(url, key)
                            # Try to connect to see if credentials are valid
                            test_response = supabase_client.table("Tracker").select("*").limit(1).execute()

                            # Store in session state
                            st.session_state.supabase_client = supabase_client
                            st.session_state.logged_in = True
                            st.success("✅ Login successful!")
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Login failed: {str(e)}")
                            st.error("Please check your URL and API key")
                    else:
                        st.error("Please enter both URL and API key")


def dashboard():
    """Main dashboard after login"""
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📒 Expense Tracker Dashboard")
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.supabase_client = None
            st.rerun()

    supabase = st.session_state.supabase_client

    # Main content in tabs
    tab1, tab2 = st.tabs(["📝 Add Expense", "📊 View Data"])

    with tab1:
        add_expense_form(supabase)

    with tab2:
        view_data(supabase)


def add_expense_form(supabase):
    """Form to add new expense"""
    st.header("Add New Expense")

    col1, col2 = st.columns(2)

    with col1:
        date = st.date_input("📅 Date", value=datetime.now().date())
        item_name = st.text_input("🏷️ Item Name", placeholder="e.g., Groceries, Fuel, etc.", max_chars=50)

    with col2:
        amount = st.number_input("💰 Amount", min_value=0.0, format="%.2f")

    note = st.text_input("📝 Note (Optional)", placeholder="Add details...", max_chars=100)

    if st.button("💾 Save Expense", use_container_width=True):
        if item_name and amount > 0:
            try:
                data = {
                    "Date": date.isoformat(),
                    "Item_Name": str(item_name),
                    "Amount": float(amount),
                    "Note": str(note) if note else ""
                }

                response = supabase.table("Tracker").insert(data).execute()
                st.success("✅ Expense saved successfully!")

                # Clear form
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error saving data: {str(e)}")
        else:
            st.error("Please fill in Item Name and Amount")


def view_data(supabase):
    """Display all expenses"""
    st.header("📊 All Expenses")

    try:
        # Fetch data
        response = supabase.table("Tracker").select("*").order("Date", desc=True).execute()

        if response.data:
            df = pd.DataFrame(response.data)

            # Display summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Expenses", len(df))
            with col2:
                st.metric("Total Amount", f"₹{df['Amount'].sum():,.2f}")
            with col3:
                st.metric("Average Amount", f"₹{df['Amount'].mean():,.2f}")
            with col4:
                st.metric("This Month",
                          f"₹{df[df['Date'].str.startswith(datetime.now().strftime('%Y-%m'))]['Amount'].sum():,.2f}")

            st.markdown("---")

            # Filters
            col1, col2 = st.columns(2)
            with col1:
                # Date range filter
                if st.checkbox("Filter by Date Range"):
                    start_date = st.date_input("Start Date")
                    end_date = st.date_input("End Date")
                    df = df[(df['Date'] >= start_date.isoformat()) & (df['Date'] <= end_date.isoformat())]

            # Display data
            if not df.empty:
                # Format the dataframe for better display
                display_df = df.copy()
                display_df['Amount'] = display_df['Amount'].apply(lambda x: f"₹{x:,.2f}")

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No expenses found for the selected filters.")

        else:
            st.info("No expenses recorded yet. Add your first expense!")

    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")


def analytics_view(supabase):
    """Display analytics and charts"""
    pass


# Main app logic
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        dashboard()


if __name__ == "__main__":
    main()
