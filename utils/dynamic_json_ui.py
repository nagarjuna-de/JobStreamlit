import streamlit as st
import datetime
from utils.helpers import upload_json_to_onedrive

def render_dynamic_form(schema_with_values: dict, bullets_dict: dict, bullet_upload_path):
    result = {}
    col1, col2 = st.columns(2)
    col_toggle = True

    # Pass 1: Text, Select, Date fields
    for key, field in schema_with_values.items():
        field_type = field["type"]
        label = field.get("label", key.capitalize())
        default = field.get("value", "")

        if field_type in ["text", "select", "date"]:
            with (col1 if col_toggle else col2):
                result[key] = render_field(field_type, label, default, key)
            col_toggle = not col_toggle

    # Pass 2: Bullet fields
    st.markdown("### 🧑‍💻 Bullet Points")

    for key, field in schema_with_values.items():
        field_type = field["type"]
        label = field.get("label", key.capitalize())
        default = field.get("value", "")

        if field_type in ["textarea", "bullets"]:
            with st.container(border=True):
                st.markdown(f"**{label}**")

                # Category + buttons row
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.selectbox(
                        "Category",
                        ["Select category", "Frontend", "Backend", "DevOps", "Cloud", "Metrics", "Database"],
                        key=f"{key}_cat",
                        label_visibility="collapsed"
                    )
                with col2:
                    if st.button("💾 Save", key=f"{key}_save"):
                        save_bullet_to_bank(
                            key=key,
                            bullets_dict=bullets_dict,
                            upload_path=bullet_upload_path,
                            access_token=st.session_state["token"]
                        )

                with col3:
                    bullet_browse_popover(key, bullets_dict)

                # Text area
                result[key] = st.text_area(
                    label="test", value=default, height=70,
                    key=f"{key}_area", label_visibility="collapsed"
                )

    return result


def render_field(field_type, label, default, key):
    if field_type == "text":
        return st.text_input(label, value=default)

    elif field_type == "select":
        return st.selectbox(
            label,
            options=default.get("options", []) if isinstance(default, dict) else [],
            index=default.get("options", []).index(default)
            if isinstance(default, dict) and default in default.get("options", []) else 0
        )

    elif field_type == "date":
        try:
            default_date = datetime.datetime.strptime(default, "%Y-%m-%d").date()
        except:
            default_date = datetime.date.today()

        selected_date = st.date_input(label, value=default_date, key=f"{key}_date")
        return selected_date.strftime("%d.%B.%Y")


def bullet_browse_popover(key: str, bullets_dict: dict):
    """
    Show bullet bank popover based on selected category.
    On select, updates corresponding text area and reruns.
    """
    category = st.session_state.get(f"{key}_cat", None)

    if not category or category == "Select category":
        st.button("📚 Browse", key=f"{key}_browse_disabled")
        return

    with st.popover(f"📚 {category} Bullets"):
        st.markdown("**Click a bullet to use it**")
        for idx, bullet in enumerate(bullets_dict.get(category, [])):
            col1, col2 = st.columns([10, 1])
            with col1:
                st.markdown(f"• {bullet}")
            with col2:
                if st.button("➕", key=f"{key}_use_{idx}"):
                    st.session_state[f"{key}_area"] = bullet
                    st.rerun()


def save_bullet_to_bank(key: str, bullets_dict: dict, upload_path: str, access_token: str):
    """
    Saves a bullet point from the UI into the correct category of bullets_dict and uploads to OneDrive.

    Parameters:
    - key: Unique key for the bullet field
    - bullets_dict: Dictionary holding bullets grouped by category
    - upload_path: Path to bullet bank file in OneDrive
    - access_token: MS Graph access token
    """
    category = st.session_state.get(f"{key}_cat")
    bullet_text = st.session_state.get(f"{key}_area", "").strip()

    if category and category != "Select category" and bullet_text:
        bullets_dict.setdefault(category, [])
        if bullet_text not in bullets_dict[category]:
            bullets_dict[category].append(bullet_text)
            st.success(f"✅ Bullet saved to '{category}'")

            try:
                upload_json_to_onedrive(
                    access_token=access_token,
                    data=bullets_dict,
                    filepath=upload_path
                )
            except Exception as e:
                st.error("❌ Failed to upload bullet bank.")
                st.code(str(e))
        else:
            st.info("ℹ️ Bullet already exists in that category.")
    else:
        st.warning("⚠️ Please enter text and select a valid category.")

