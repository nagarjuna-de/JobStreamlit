import requests
from io import BytesIO

import re
from docxtpl import RichText

def load_docx_from_onedrive(access_token, filepath: str) -> BytesIO:
    """
    Downloads a .docx file from OneDrive and returns it as BytesIO.
    
    Parameters:
    - access_token: Microsoft Graph API token
    - filepath: path of the file in OneDrive (e.g., Jobs/applications/April/15_Accenture/nagarjuna_ravella_CV.docx)

    Returns:
    - BytesIO: in-memory bytes object for loading into python-docx
    """
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{filepath}:/content"
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        raise Exception(f"❌ Failed to download docx from OneDrive: {response.status_code} - {response.text}")




def upload_docx_to_onedrive(access_token: str, file_stream: BytesIO, filepath: str):
    """
    Uploads a DOCX BytesIO object to OneDrive at the given filepath.

    Parameters:
    - access_token: Microsoft Graph token
    - file_stream: BytesIO object containing the docx file
    - filepath: OneDrive relative path (e.g., Jobs/applications/April/15_Accenture/FINAL_CV.docx)
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }

    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{filepath}:/content"
    response = requests.put(url, headers=headers, data=file_stream.getvalue())

    if response.status_code not in [200, 201]:
        raise Exception(f"❌ Failed to upload DOCX: {response.status_code} - {response.text}")



def download_docx_as_pdf(access_token: str, source_docx_path: str, target_pdf_path: str):
    """
    Downloads a .docx from OneDrive, converts it to PDF, and uploads the PDF to OneDrive.

    Parameters:
    - access_token: Microsoft Graph access token
    - source_docx_path: path of the DOCX in OneDrive
    - target_pdf_path: path to upload the new PDF in OneDrive
    """
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Download as PDF using format=pdf
    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{source_docx_path}:/content?format=pdf"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"❌ Failed to download DOCX as PDF: {response.status_code} - {response.text}")

    pdf_content = response.content

    # Upload PDF back to OneDrive
    headers_upload = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/pdf"
    }

    upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{target_pdf_path}:/content"
    upload_response = requests.put(upload_url, headers=headers_upload, data=pdf_content)

    if upload_response.status_code not in [200, 201]:
        raise Exception(f"❌ Failed to upload PDF: {upload_response.status_code} - {upload_response.text}")


def parse_bullet_to_richtext(text: str):
    rt = RichText()
    parts = re.split(r"(\*\*.*?\*\*)", text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            rt.add(part[2:-2], bold=True)
        else:
            rt.add(part)
    return rt