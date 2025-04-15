import streamlit as st
from utils.auth import get_access_token

st.set_page_config(page_title="🏠 Home", layout="wide", initial_sidebar_state="collapsed")
st.title("💼 Job Application Project")

get_access_token()

if "token" in st.session_state:
    st.success("🔑 Access token is available. Ready to access OneDrive.")
    st.header("🏠 Home")
    st.markdown("""
    Welcome to your **Job Application Tracker**!  
    Use **Tracker** to view insights and charts.  
    Use **Applications** to manage job entries.
    """)
else:
    st.warning("Please log in to continue.")
    st.stop()
