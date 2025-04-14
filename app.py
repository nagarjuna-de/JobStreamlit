import streamlit as st

# Custom navigation menu
st.set_page_config(page_title="Job Application Project", layout="wide")

st.markdown("## Job Application Project")

# Define navigation options
menu = st.selectbox("Navigate to", ["Home", "Tracker", "Applications"])

# Load selected page content
if menu == "Home":
    st.markdown("### Welcome to the Job Application Tracker")
    st.markdown("""
    Use this tool to track your job applications and analyze your progress.

    Select a page from the dropdown above.
    """)

elif menu == "Tracker":
    from pages import tracker
    tracker.show()

elif menu == "Applications":
    from pages import applications
    applications.show()


