import datetime
import requests
from io import BytesIO
import json

def get_template_target_folder_paths(job):
    date_obj = job["Date"]
    month = date_obj.strftime("%B")       # April
    day = date_obj.strftime("%d")         # 15
    company = job["Company Name"]

    # Construct folder path
    target_folder = f"Jobs/applications/{month}/{day}_{company}"
    template_folder = f"Jobs/templates/{job['Job Type']}"
    bank_folder = f"Jobs/templates/Bullet Bank"
    return template_folder, target_folder, bank_folder




def ensure_folder_exists(access_token, folder_path):
    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder_path}"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        # Create folder
        parent_path = "/".join(folder_path.split("/")[:-1])
        folder_name = folder_path.split("/")[-1]

        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{parent_path}:/children"
        payload = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }
        create_resp = requests.post(url, headers={**headers, "Content-Type": "application/json"}, json=payload)
        create_resp.raise_for_status()
    elif response.status_code != 200:
        raise Exception(f"Failed to check folder: {response.status_code} - {response.text}")
    


def copy_file_between_folders(access_token, file_name, source_path, target_path):
    headers = {"Authorization": f"Bearer {access_token}"}

    # 🔍 Check if file already exists in target folder
    check_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{target_path}/{file_name}"
    check_resp = requests.get(check_url, headers=headers)

    if check_resp.status_code == 200:
        print(f"🔁 Skipping '{file_name}' — already exists in {target_path}")
        return  # ✅ File exists, skip copying
    elif check_resp.status_code != 404:
        raise Exception(f"❌ Failed to check file existence: {check_resp.status_code} - {check_resp.text}")

    # ⬇ Step 1: Download file from source
    download_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{source_path}/{file_name}:/content"
    download_resp = requests.get(download_url, headers=headers)
    if download_resp.status_code != 200:
        raise Exception(f"❌ Failed to download {file_name}: {download_resp.status_code} - {download_resp.text}")

    file_bytes = BytesIO(download_resp.content)

    # ⬆ Step 2: Upload to target folder
    upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{target_path}/{file_name}:/content"
    upload_resp = requests.put(upload_url, headers=headers, data=file_bytes.getvalue())
    if upload_resp.status_code not in [200, 201]:
        raise Exception(f"❌ Failed to upload {file_name}: {upload_resp.status_code} - {upload_resp.text}")



def load_json_from_onedrive(access_token, filepath: str):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{filepath}:/content"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return json.loads(response.content.decode("utf-8"))
    else:
        raise Exception(f"❌ Failed to load JSON: {response.status_code} - {response.text}")
    
def upload_json_to_onedrive(access_token, data: dict, filepath: str):
    # Convert dict to JSON bytes
    json_bytes = BytesIO(json.dumps(data, indent=2).encode("utf-8"))

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{filepath}:/content"

    response = requests.put(url, headers=headers, data=json_bytes.getvalue())

    if response.status_code not in [200, 201]:
        raise Exception(f"❌ Failed to upload JSON to OneDrive: {response.status_code} - {response.text}")

