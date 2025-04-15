import streamlit as st

def render_nav():
    nav = st.radio(
        "Navigation",
        ["🏠 Home", "📊 Tracker", "📝 Applications"],
        index=["🏠 Home", "📊 Tracker", "📝 Applications"].index(get_current_page_name()),
        horizontal=True,
        label_visibility="collapsed"
    )

    page_map = {
        "🏠 Home": "/",
        "📊 Tracker": "/tracker",
        "📝 Applications": "/applications",
    }

    if st.session_state.get("current_page") != nav:
        st.session_state["current_page"] = nav
        st.rerun()
    
    st.markdown("---")
    st.markdown(f"### {nav}")
    st.write("")  # spacing

def get_current_page_name():
    query_params = st.query_params
    if "tracker" in query_params:
        return "📊 Tracker"
    if "applications" in query_params:
        return "📝 Applications"
    return "🏠 Home"

