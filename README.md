[main.py](https://github.com/user-attachments/files/22145433/main.py)
import streamlit as st
from datetime import date

st.title("🧮 Age Calculator")

min_dob = date(1900, 1, 1)
max_dob = date.today()

# Take DOB input
dob = st.date_input("Enter your Date of Birth",min_value=min_dob)

# Get today's date
today = date.today()

# Calculate age
age_years = today.year - dob.year

# Show result
st.write(f"🎂 Your age is: **{age_years}** years")
