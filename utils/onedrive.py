import requests
import pandas as pd
from io import BytesIO
import requests

def read_excel_from_onedrive(access_token, filepath="Jobs/JobTracker.xlsx", sheet_name=0):
    """
    Reads an Excel file from OneDrive via Microsoft Graph API and returns a Pandas DataFrame.

    Parameters:
    - access_token (str): Microsoft Graph access token.
    - filepath (str): Path to the Excel file in OneDrive.
    - sheet_name (int or str): Sheet to read (default: first sheet).

    Returns:
    - pd.DataFrame: Contents of the Excel sheet.
    """
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{filepath}:/content"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        raise Exception(f"🔌 Network error while fetching Excel file: {e}")

    if response.status_code == 200:
        try:
            excel_data = BytesIO(response.content)
            df = pd.read_excel(excel_data, sheet_name=sheet_name)
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
            return df
        except Exception as e:
            raise Exception(f"📄 Failed to parse Excel file: {e}")




def append_row_to_excel_table(access_token, new_row: dict, filepath="Jobs/JobTracker.xlsx", table_name="JobTable"):
    """
    Appends a single new row to a named table in an Excel file stored on OneDrive using Microsoft Graph API.
    Assumes the table has the following columns (in order): ID, Job Type, Date, Company Name, Url, Created Application folder, Status
    """

    # 1. Create a workbook session
    session_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{filepath}:/workbook/createSession"
    try:
        session_resp = requests.post(
            session_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json={"persistChanges": True},
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        raise Exception(f"🔌 Network error while creating session: {e}")

    if session_resp.status_code != 201:
        raise Exception(f"❌ Failed to create Excel session: {session_resp.status_code} - {session_resp.text}")

    session_id = session_resp.json()["id"]

    # 2. Format row (ensure order matches table column structure)
    values = [[
        new_row.get("ID", ""),
        new_row.get("Job Type", ""),
        new_row.get("Date", ""),
        new_row.get("Company Name", ""),
        new_row.get("Url", ""),
        new_row.get("Folder Created", ""),
        new_row.get("Status", "")
    ]]

    # 3. Append the row to the table
    append_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{filepath}:/workbook/tables/{table_name}/rows/add"
    try:
        append_resp = requests.post(
            append_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "workbook-session-id": session_id
            },
            json={"values": values},
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        raise Exception(f"🔌 Network error while appending row: {e}")

    if append_resp.status_code not in [200, 201]:
        raise Exception(f"❌ Failed to append row: {append_resp.status_code} - {append_resp.text}")

    # 4. Close session (optional but good practice)
    close_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{filepath}:/workbook/closeSession"
    try:
        requests.post(
            close_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "workbook-session-id": session_id
            },
            timeout=5
        )
    except requests.exceptions.RequestException:
        pass  # Fail silently if session close fails — Excel will auto-close it eventually




def overwrite_excel_file(access_token, updated_df, filepath="Jobs/JobTracker.xlsx"):
    """
    Overwrites the entire Excel file with the updated DataFrame.
    """
    # Convert to Excel in memory
    buffer = BytesIO()
    updated_df.to_excel(buffer, index=False)
    buffer.seek(0)

    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{filepath}:/content"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }

    response = requests.put(url, headers=headers, data=buffer)

    if response.status_code not in [200, 201]:
        raise Exception(f"❌ Failed to overwrite Excel file: {response.status_code} - {response.text}")


