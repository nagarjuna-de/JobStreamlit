from msal import PublicClientApplication
import streamlit as st

CLIENT_ID = "7553f833-0b27-47b3-b336-e7d4a4289cef"
AUTHORITY = "https://login.microsoftonline.com/common"
SCOPES = ["User.Read", "Files.ReadWrite"]

def get_access_token():
    if "token" in st.session_state:
        return st.session_state["token"]

    st.info("🔐 You need to sign in to continue.")
    if st.button("🔑 Login with Microsoft"):
        app = PublicClientApplication(client_id=CLIENT_ID, authority=AUTHORITY)
        result = app.acquire_token_interactive(scopes=SCOPES)

        if "access_token" in result:
            st.session_state["token"] = result["access_token"]
            st.success("✅ Login successful!")
        else:
            st.error("❌ Login failed.")
            st.code(result)
            st.stop()


