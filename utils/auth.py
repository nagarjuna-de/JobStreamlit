from msal import PublicClientApplication, SerializableTokenCache
from datetime import datetime, timedelta, timezone
import streamlit as st
import base64
import os
import json

CLIENT_ID = "7553f833-0b27-47b3-b336-e7d4a4289cef"
AUTHORITY = "https://login.microsoftonline.com/7736da25-863a-4767-a50f-4de1c3cd454f"
SCOPES = ["User.Read", "Files.ReadWrite"]

# ===== cred.json =====
CRED_FILE = "Cred.json"          # {"encoded_token_cache":"", "generated_at":""}
EXPIRY_DAYS = 90                 # display-only estimate for refresh window

# ---------- helpers ----------
def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _approx_expires(generated_at: str | None) -> str:
    if not generated_at:
        return "Unknown"
    try:
        gen = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        return (gen + timedelta(days=EXPIRY_DAYS)).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return "Unknown"

def _cred_read():
    if not os.path.exists(CRED_FILE):
        return None, None
    try:
        with open(CRED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("encoded_token_cache"), data.get("generated_at")
    except Exception:
        return None, None

def _cred_write(encoded_cache: str, generated_at: str):
    tmp = CRED_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(
            {"encoded_token_cache": encoded_cache, "generated_at": generated_at},
            f,
        )
    os.replace(tmp, CRED_FILE)

# ---------- main entry ----------
def get_access_token(force_refresh: bool = False) -> bool:
    """
    - Silent load from cred.json into MSAL cache, try acquire_token_silent.
    - If force_refresh=True: run device code flow (Cloud-safe), then persist to cred.json.
    - On success, sets st.session_state["token"], ["generated_at"], ["approx_expires_at"].
    - Returns True if token available, else False.
    """
    cache = SerializableTokenCache()
    encoded, generated_at = _cred_read()

    # Load cache if present
    if encoded:
        try:
            cache.deserialize(base64.b64decode(encoded).decode("utf-8"))
        except Exception:
            pass

    app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)

    # 1) Silent path
    if not force_refresh:
        try:
            accounts = app.get_accounts()
            if accounts:
                result = app.acquire_token_silent(SCOPES, account=accounts[0])
                if result and "access_token" in result:
                    st.session_state["token"] = result["access_token"]
                    st.session_state["generated_at"] = generated_at
                    st.session_state["approx_expires_at"] = _approx_expires(generated_at)
                    return True
        except Exception:
            pass
        return False

    # 2) Refresh path: Device Code Flow (works on Streamlit Cloud)
    try:
        flow = app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in flow:
            st.error("Device flow init failed.")
            return False

        # Show instructions to the user
        st.info(
            f"Open {flow['verification_uri']} and enter code: **{flow['user_code']}**. "
            "Keep this page open; it will complete after approval."
        )

        result = app.acquire_token_by_device_flow(flow)  # blocks until user finishes
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return False

    if "access_token" in result:
        # Persist updated cache to cred.json
        generated_at = _now_iso()
        try:
            encoded_cache = base64.b64encode(cache.serialize().encode("utf-8")).decode("utf-8")
            _cred_write(encoded_cache, generated_at)
        except Exception as e:
            st.warning(f"Signed in, but couldn't write cred.json: {e}")

        st.session_state["token"] = result["access_token"]
        st.session_state["generated_at"] = generated_at
        st.session_state["approx_expires_at"] = _approx_expires(generated_at)
        return True

    st.error("Login failed.")
    return False
