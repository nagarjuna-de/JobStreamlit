import streamlit as st
from docxtpl import DocxTemplate
from io import BytesIO
from utils.auth import get_access_token
from utils.helpers import (
    get_template_target_folder_paths,
    ensure_folder_exists,
    copy_file_between_folders,
    load_json_from_onedrive,
    upload_json_to_onedrive,
)
from utils.dynamic_json_ui import render_dynamic_form
from utils.doc_helpers import (
    load_docx_from_onedrive,
    upload_docx_to_onedrive,
    download_docx_as_pdf,
    parse_bullet_to_richtext
)

# --- Page config ---
st.set_page_config(page_title="📝 Applications", layout="wide", initial_sidebar_state="collapsed")
st.title("📝 Applications")

# --- Notification Box Setup ---
notification_box = st.container()
if "latest_notification" not in st.session_state:
    st.session_state["latest_notification"] = None

# --- Files to copy ---
file_names = [
    "nagarjuna_ravella_CV.docx",
    "nagarjuna-ravella_coverletter.docx",
    "CV_template.json",
    "CL_template.json",
]

# --- Token ---
get_access_token()

# --- Main logic ---
if "selected_job" in st.session_state:
    job = st.session_state["selected_job"]

    # Set initial notification
    st.session_state["latest_notification"] = (
        "success",
        f"🧾 Viewing application for **{job['Job Type']}** at **{job['Company Name']}**",
    )

    # --- Sidebar Job Details ---
    with st.sidebar:
        st.markdown("## 📄 Job Details")
        st.markdown(f"**Status**: {job['Status']}")
        st.markdown(f"**Company**: {job['Company Name']}")
        st.markdown(f"**URL**: {job['Url']}")
        st.markdown(f"**Applied On**: {job['Date']}")

    if "token" in st.session_state:
        try:
            template_folder, target_folder, bank_folder = get_template_target_folder_paths(job)
            ensure_folder_exists(st.session_state["token"], target_folder)

            for file_name in file_names:
                copy_file_between_folders(
                    access_token=st.session_state["token"],
                    file_name=file_name,
                    source_path=template_folder,
                    target_path=target_folder,
                )

            st.session_state["latest_notification"] = ("success", f"✅ Files copied to `{target_folder}`")

            # --- Document selection and placeholders editing ---
            col1, col2 = st.columns([4, 3])

            with col1:
                st.markdown("### ✍️ Edit Placeholders")
            with col2:
                doc_type = st.radio(
                    "Choose document to edit:",
                    ("CV", "Cover Letter"),
                    horizontal=True,
                    label_visibility="collapsed"
                )

            # Determine correct file names
            if doc_type == "CV":
                template_docx_filename = "nagarjuna_ravella_CV.docx"
                template_json_filename = "CV_template.json"
                bullets_json_filename = "CV_WEBullets.json"
                output_docx_filename = "Preview_CV.docx"
                output_pdf_filename = "Nagarjuna_Ravella_CV.pdf"
            else:
                template_docx_filename = "nagarjuna_ravella_coverletter.docx"
                template_json_filename = "CL_template.json"
                bullets_json_filename = "CL_WEBullets.json"
                output_docx_filename = "FINAL_CL.docx"
                output_pdf_filename = "FINAL_CL.pdf"

            # Load placeholders JSON
            json_path = f"{target_folder}/{template_json_filename}"
            placeholders_dict = load_json_from_onedrive(st.session_state["token"], json_path)

            # Load Bullets Json
            bullets_json_path = f"{bank_folder}/{bullets_json_filename}"
            bullets_dict = load_json_from_onedrive(st.session_state["token"], bullets_json_path)

            # Render editable form
            result = render_dynamic_form(placeholders_dict, bullets_dict, bullets_json_path)

            # --- Button to Generate Final ---
            if st.button(f"📄 Create Final {doc_type} and PDF"):
                try:
                    # Update JSON values
                    for key in result:
                        if key in placeholders_dict:
                            placeholders_dict[key]["value"] = result[key]

                    upload_json_to_onedrive(
                        access_token=st.session_state["token"],
                        data=placeholders_dict,
                        filepath=json_path
                    )

                    # Load Word template
                    template_docx_path = f"{target_folder}/{template_docx_filename}"
                    docx_bytes = load_docx_from_onedrive(st.session_state["token"], template_docx_path)
                    docx_buffer = BytesIO(docx_bytes.read())
                    doc = DocxTemplate(docx_buffer)

                    # Replace placeholders
                    placeholder_mapping = {}
                    for key, field in placeholders_dict.items():
                        value = field.get("value", "")
                        if key.startswith("Bullet"):
                            placeholder_mapping[key] = parse_bullet_to_richtext(value)
                        else:
                            placeholder_mapping[key] = value
                    # placeholder_mapping = {key: field.get("value", "") for key, field in placeholders_dict.items()}
                    doc.render(placeholder_mapping)

                    # Save updated DOCX into memory
                    final_docx_buffer = BytesIO()
                    doc.save(final_docx_buffer)
                    final_docx_buffer.seek(0)

                    # Upload DOCX
                    final_docx_path = f"{target_folder}/{output_docx_filename}"
                    upload_docx_to_onedrive(st.session_state["token"], final_docx_buffer, final_docx_path)

                    # Generate and upload PDF
                    final_pdf_path = f"{target_folder}/{output_pdf_filename}"
                    download_docx_as_pdf(st.session_state["token"], final_docx_path, final_pdf_path)

                    st.session_state["latest_notification"] = (
                        "success",
                        f"✅ Final {doc_type} (.docx) and PDF created successfully!",
                    )

                except Exception as e:
                    st.session_state["latest_notification"] = (
                        "error",
                        f"❌ Error creating {doc_type} and PDF.",
                    )
                    st.code(str(e))

        except Exception as e:
            st.session_state["latest_notification"] = ("error", "❌ Failed to load templates or files.")
            st.code(str(e))
    else:
        st.session_state["latest_notification"] = (
            "warning",
            "🔒 Please log in to access your OneDrive data."
        )
else:
    st.session_state["latest_notification"] = (
        "warning",
        "⚠️ No job selected. Please go to the Tracker page and select a job."
    )

# --- Render latest notification ---
with notification_box:
    if st.session_state["latest_notification"]:
        notif_type, message = st.session_state["latest_notification"]
        if notif_type == "success":
            st.success(message)
        elif notif_type == "error":
            st.error(message)
        elif notif_type == "warning":
            st.warning(message)
