# app.py
import json
import os
from datetime import datetime, timedelta, timezone

import streamlit as st
from utils.auth import get_access_token

CRED_FILE = "cred.json"
STALE_DAYS = 80  # your threshold

st.set_page_config(page_title="🏠 Home", layout="wide", initial_sidebar_state="collapsed")
st.title("💼 Job Application Project")

def _read_cred():
    if not os.path.exists(CRED_FILE):
        return None, None
    try:
        with open(CRED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("encoded_token_cache"), data.get("generated_at")
    except Exception:
        return None, None

def _parse_iso(dt_str: str | None) -> datetime | None:
    if not dt_str:
        return None
    try:
        # handle both "...Z" and "+00:00" endings
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None

def _human(dt: datetime | None) -> str:
    return dt.strftime("%Y-%m-%d %H:%M UTC") if dt else "Unknown"

encoded_cache, generated_at_str = _read_cred()
generated_dt = _parse_iso(generated_at_str)
valid_until_dt = generated_dt + timedelta(days=STALE_DAYS) if generated_dt else None
now = datetime.now(timezone.utc)

def _show_signin_ui(message: str):
    st.warning(message)
    if st.button("🔐 Sign in with Microsoft"):
        with st.spinner("Waiting for Microsoft sign-in..."):
            ok = get_access_token(force_refresh=True)  # Device Code Flow
        if ok:
            st.success("Signed in successfully.")
            st.rerun()
        else:
            st.error("Sign-in failed. Please try again.")

# 1) No cache or empty cache
if not encoded_cache:
    _show_signin_ui("No cached credentials found. Please sign in to continue.")
    st.stop()

# 2) No generated_at or can’t parse → treat as stale
if not generated_dt:
    _show_signin_ui("Credential timestamp missing/invalid. Please sign in to continue.")
    st.stop()

# 3) Older than 80 days → force re-auth
if now >= valid_until_dt:
    _show_signin_ui(
        f"Cached credential is older than {STALE_DAYS} days "
        f"(generated at: {_human(generated_dt)}). Please sign in again."
    )
    st.stop()

# 4) Fresh enough → show validity + try silent token
st.info(f"Token cache is fresh. **Valid until**: {_human(valid_until_dt)}")
ok = get_access_token(force_refresh=False)  # silent
if ok and "token" in st.session_state:
    st.success("🔑 Access token is available. Ready to access OneDrive.")
    st.caption(f"Generated at: {_human(generated_dt)}  •  Approx. valid until: {_human(valid_until_dt)}")
    st.button("🔁 Refresh token", on_click=lambda: (get_access_token(force_refresh=True), st.rerun()))
else:
    # Could not silently load → ask user to sign in
    _show_signin_ui("Couldn’t acquire token silently. Please sign in.")
