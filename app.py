import streamlit as st
from utils.auth import get_access_token
from pages import tracker, applications

st.set_page_config(page_title="Job Application Project", layout="wide")
st.title("💼 Job Application Project")

get_access_token()

if "token" in st.session_state:
    st.success("🔑 Access token is available. Ready to access OneDrive.")

    # Navigation
    page = st.selectbox("Navigate to", ["Home", "Tracker", "Applications"])

    if page == "Home":
        st.header("🏠 Home")
        st.markdown("""
        Welcome to your Job Application Tracker.

        Use **Tracker** to see charts and insights.

        Use **Applications** to manage your job entries.
        """)
    elif page == "Tracker":
        tracker.show()
    elif page == "Applications":
        applications.show()
else:
    st.warning("Please log in to continue.")
    st.stop()  # Stops app execution after showing login button
