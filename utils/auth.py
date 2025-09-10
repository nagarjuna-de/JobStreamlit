from msal import PublicClientApplication, SerializableTokenCache
import streamlit as st
import base64
import os

CLIENT_ID = "7553f833-0b27-47b3-b336-e7d4a4289cef"
AUTHORITY = "https://login.microsoftonline.com/common"
SCOPES = ["User.Read", "Files.ReadWrite"]

# Change to True only when you want to regenerate base64 secret
LOCAL_MODE = True


def get_access_token():
    cache = SerializableTokenCache()

    if LOCAL_MODE:
        # Interactive login and regenerate secret.txt
        app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)

        accounts = app.get_accounts()
        if accounts:
            result = app.acquire_token_silent(SCOPES, account=accounts[0])
        else:
            result = app.acquire_token_interactive(scopes=SCOPES)

        if "access_token" in result:
            print("✅ Access token acquired.")

            # Save token_cache.bin locally (optional)
            with open("token_cache.bin", "w") as f:
                f.write(cache.serialize())

            # Write base64-encoded cache to secret.txt
            encoded = base64.b64encode(cache.serialize().encode("utf-8")).decode("utf-8")
            with open("secret.txt", "w") as f:
                f.write(f'[auth]\nencoded_token_cache = "{encoded}"\n')

            print("✅ Saved token_cache.bin and secret.txt with base64.")
            return result["access_token"]
        else:
            print("❌ Login failed.")
            print(result)
            return None

    else:
        # Load from secrets in both local and cloud
        try:
            encoded_cache = st.secrets["auth"]["encoded_token_cache"]
            decoded_cache = base64.b64decode(encoded_cache).decode("utf-8")
            cache.deserialize(decoded_cache)
        except Exception as e:
            st.warning("⚠️ Could not load token cache from secrets.")
            st.stop()

        app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)

        accounts = app.get_accounts()
        if accounts:
            result = app.acquire_token_silent(SCOPES, account=accounts[0])
            if result and "access_token" in result:
                st.session_state["token"] = result["access_token"]
                return result["access_token"]

        st.error("❌ Token expired or missing. Set `LOCAL_MODE = True` to refresh and update your secret.")
        st.stop()
