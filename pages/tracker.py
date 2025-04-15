import streamlit as st
from utils.onedrive import read_excel_from_onedrive, append_row_to_excel_table, overwrite_excel_file
from utils.auth import get_access_token
import pandas as pd
import datetime
import uuid



st.set_page_config(page_title="📊 Tracker", layout="wide")
get_access_token()

st.title("📊 Tracker Page")


st.markdown("View analytics for your job")

if "token" in st.session_state:
    try:
        df = read_excel_from_onedrive(
            access_token=st.session_state["token"],
            filepath="Jobs/JobTracker.xlsx"
        )

        display_df = df.drop(columns=["ID"])
        # Show the main table
        st.subheader("📄 Job Applications Table")
        edited_df = st.data_editor(
            display_df,
            num_rows="fixed",
            use_container_width=True,
            column_config={
                "Company Name": st.column_config.TextColumn(),
                "Url": st.column_config.TextColumn("Application URL"),
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Preparation", "Applied", "In process", "Rejected"]
                ),
                # Lock all other columns (optional)
                "Job Type": st.column_config.TextColumn(disabled=True),
                "Date": st.column_config.DateColumn("Date", format="DD-MMM-YYYY"),
                "Created Application folder": st.column_config.TextColumn(disabled=True),
            },
            key="editor"
        )

        if st.button("💾 Save Updates to Excel"):
            try:
                editable_cols = ["Company Name", "Url", "Status"]
                df[editable_cols] = edited_df[editable_cols]

                overwrite_excel_file(
                    access_token=st.session_state["token"],
                    updated_df=df,
                    filepath="Jobs/JobTracker.xlsx",
                )
                st.success("✅ Updates saved to Excel!")
            except Exception as e:
                st.error("❌ Failed to update Excel.")
                st.code(str(e))

        # Sidebar form toggle
        show_form = st.sidebar.checkbox("➕ Add New Job Entry", value=True)

        if show_form:
            with st.sidebar.form("add_form", clear_on_submit=True):
                job_type = st.selectbox("Job Type", [
                    "Full Stack Developer", "Cloud Engineer", "DevOps Engineer",
                    "Python Engineer", "Backend Engineer", "AI Engineer"
                ])
                date_applied = datetime.date.today().strftime("%d-%b-%Y")
                company = st.text_input("Company Name")
                url = st.text_input("Application URL")
                folder_created = st.selectbox("Created Application Folder", ["Yes", "No"])
                status = st.selectbox("Status", ["Preparation", "Applied", "In process", "Rejected"])

                submitted = st.form_submit_button("Add Entry")

                if submitted:
                    # Validate all fields
                    if not (job_type and company.strip() and url.strip() and folder_created and status):
                        st.sidebar.warning("⚠️ Please fill out all fields.")
                    else:
                        new_id = str(uuid.uuid4())[:8]

                        new_row = {
                            "ID": new_id,
                            "Job Type": job_type,
                            "Date": str(date_applied),
                            "Company Name": company,
                            "Url": url,
                            "Created Application folder": folder_created,
                            "Status": status
                        }
                        try:
                            append_row_to_excel_table(
                                access_token=st.session_state["token"],
                                new_row=new_row,
                                filepath="Jobs/JobTracker.xlsx"
                            )
                            st.sidebar.success("✅ Entry added and saved to OneDrive!")
                            st.rerun()
                            
                        except Exception as e:
                            st.sidebar.error("❌ Failed to save to OneDrive.")
                            st.sidebar.code(str(e))

        

    except Exception as e:
        st.error("❌ Failed to load Excel.")
        st.code(str(e))
else:
    st.warning("🔒 Please log in to access your OneDrive data.")
