import requests
import frappe
import os
import json
import time
import frappe
from frappe import throw, _
import shutil

def upload_file(doc, method):
    # Check if the file attachment fibeneld has a file
  
    # Access the attached file
    file_doc = frappe.get_doc("File", doc.name)

    # Check for zero content length
    if file_doc.file_size == 0:
        frappe.throw(_("The uploaded file is empty. Please select a valid file."))

    # Get the file details
    file_name = file_doc.file_name

    # Get the external storage path from site config
    config = frappe.get_site_config()
    path = config.get("external_storage", {}).get("path")

    if not path:
        frappe.throw(_("External storage path is not configured."))

    # Create the full file path
    file_path = os.path.join(path, file_name)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Save the file to the external hard drive
    try:
        frappe.msgprint(_("File uploaded successfully to external storage."))
        shutil.move(file_doc.get_full_path() , file_path)
       
        file_url = f"https://mobilecrm.erpdata.in/files/attachments/{file_name}"
        key = file_doc.content_hash  # Assuming you want to keep the current content_hash
        
        # Update the file directly in the database
        frappe.db.sql("""UPDATE `tabFile` SET file_url=%s, folder=%s,
                          old_parent=%s, content_hash=%s WHERE name=%s""", (
                          file_url, 'Home/Attachments', 'Home/Attachments', key, file_doc.name))
        frappe.db.commit()  # 
        
        
    except Exception as e:
        frappe.throw(_("Failed to save file to external storage: {}").format(str(e)))




# def upload_file(doc, method):
#     # Get the external storage path from site_config
#     config = frappe.get_site_config()
#     path = config.get("external_storage", {}).get("path")
    
#     frappe.msgprint(path)  # Debugging message

#     if not path:
#         frappe.throw(_("External storage path is not configured."))

#     # Check if the file is present in the request
#     if 'file' not in frappe.request.files:
#         frappe.throw(_("No file was provided."))

#     # Get the uploaded file
#     file = frappe.request.files['file']
#     frappe.msgprint(file)
    

#     # Create the full file path
#     file_path = os.path.join(path, file.filename)
#     frappe.msgprint(file_path)  # Debugging message

#     # Ensure the directory exists
#     os.makedirs(os.path.dirname(file_path), exist_ok=True)

#     try:
#         # Save the file
#         with open(file_path, 'wb') as f:
#             f.write(file.read())
#         frappe.msgprint(_("File uploaded successfully."))
#          # Construct the file URL for reference in the database
#         # file_url = f"file://{file_path}"  # Use the file URI scheme for local files
#         # frappe.msgprint(f"File URL: {file_url}")

#         # Create and insert a new File document
#         # new_file_doc = frappe.get_doc({
#         #     "doctype": "File",
#         #     "file_url": f"{"https://mobilecrm.erpdata.in"}/files/{file.name}",
#         #     "file_name": file.name
#         # })
#         # new_file_doc.insert(ignore_permissions=True)
#         frappe.msgprint(_("File path stored in the database successfully."))

#     except Exception as e:
#         frappe.throw(_("Failed to save file: {}").format(str(e)))

#     return {"file_path": file_path, "message": _("File uploaded successfully.")}

def upload_to_another_frappe_server(doc, method):
    frappe.msgprint("Upload method triggered!")  # Debug: Check if method is called

    # Check if the document has an attached file
    if not hasattr(doc, 'file_list') or not doc.file_list:
        frappe.msgprint("No file attached to upload.")
        return

    # Debug: Log the file_list
    print(f"File list: {doc.file_list}")  # Show the contents of the file list

    for file_doc in doc.file_list:
        print(f"Processing file: {file_doc['name']}")  # Log the name of the file being processed

        file_doc_instance = frappe.get_doc("File", file_doc['name'])
        file_path = file_doc_instance.get_full_path()

        destination_frappe_url = "http://45.249.255.81:4414"
        api_endpoint = f"{destination_frappe_url}/api/resource/File"
        api_key = "1236c2d8ff6c832"
        api_secret = "5afa9a3f903131b"

        try:
            if not os.path.isfile(file_path):
                frappe.throw(f"File '{file_path}' does not exist.")

            with open(file_path, 'rb') as file_data:
                headers = {
                    "Authorization": f"token {api_key}:{api_secret}",
                    "Content-Type": "application/json"
                }

                # Prepare JSON metadata
                json_data = {
                    'file_name': file_doc_instance.file_name,
                    'is_private': file_doc_instance.is_private,
                    'folder': 'Home/Attachments'  # Specify the target folder
                }

                # Use a multipart form data to send both file and metadata
                response = requests.post(
                    api_endpoint,
                    headers=headers,
                    data=json_data,  # Send metadata
                    files={'file': file_data}  # Send file
                )

            if response.status_code == 200:
                frappe.msgprint(f"File '{file_doc_instance.file_name}' uploaded successfully to {destination_frappe_url}")
            else:
                frappe.throw(f"Failed to upload file. Status Code: {response.status_code}, Response: {response.text}")

        except Exception as e:
            frappe.throw(f"Error during file upload to another Frappe server: {str(e)}")


# def upload_file_to_frappe(doc, method):
#     # Get the full file path
#     file_path = doc.get_full_path()

#     # Check if the file exists
#     if not os.path.exists(file_path):
#         frappe.log_error(f"File does not exist: {file_path}", "File Upload Error")
#         return

#     # Frappe server details
#     frappe_url = 'http://45.249.255.81:4414'
#     api_key = "1236c2d8ff6c832"
#     api_secret = "5afa9a3f903131b"

#     # Prepare the URL for uploading the file using Frappe's file resource API
#     upload_url = f"{frappe_url}/api/resource/File"

#     # Prepare the headers for authentication and content type
#     headers = {
#         "Authorization": f"token {api_key}:{api_secret}",
#         "Content-Type": "application/json"  # Ensure it's sent as JSON
#     }

#     # Open the file for reading and upload it
#     try:
#         with open(file_path, 'rb') as f:
#             files = {
#                 'file': (doc.file_name, f)  # Use doc.file_name for the correct file name
#             }

#             # Prepare the data, and ensure it's properly formatted
#             data = {
#                 'is_private': 0,  # 1 for private, 0 for public
#                 'doctype': 'File',  # Required doctype for file uploads
#                 'docname': doc.name,  # Name of the file document in Frappe
#                 'folder': 'Home',  # Specify the folder path if needed
#                 'file_name': doc.file_name
#             }

#             # Convert data to JSON format
#             data_json = json.dumps(data)

#             # Make the POST request to upload the file
#             response = requests.post(upload_url, headers=headers, files=files, data={'data': data_json})

#             # Check the response status and log results accordingly
#             if response.status_code == 200:
#                 try:
#                     response_data = response.json()
#                     frappe.log(f"File uploaded successfully: {response_data}")
#                 except ValueError:
#                     frappe.log_error(f"Invalid JSON response from server: {response.text}", "File Upload Error")
#             else:
#                 frappe.log_error(f"Failed to upload file: Status {response.status_code}, Response {response.text}", "File Upload Error")

#     except Exception as e:
#         frappe.log_error(f"Error while uploading file: {str(e)}", "File Upload Exception")


# def upload_file_to_frappe(doc, method):
#     # Get the full file path
#     file_path = doc.get_full_path()  # Assuming this method returns the full file path
#     frappe.msgprint(f"File path: {file_path}")

#     # Check if the file exists
#     if not os.path.exists(file_path):
#         frappe.msgprint(f"File does not exist: {file_path}", "File Upload Error")
#         return

#     # Frappe server details
#     frappe_url = 'http://45.249.255.81:4414'
#     api_key = "1236c2d8ff6c832"
#     api_secret = "5afa9a3f903131b"

#     # Prepare the URL for the upload
#     upload_url = f"{frappe_url}/api/method/upload_file"
#     time.sleep(1)  # Add a delay if needed for rate-limiting

#     # Prepare the headers for authentication
#     headers = {
#         "Authorization": f"token {api_key}:{api_secret}"
#     }
#     print("Headers:", headers)

#     try:
#         with open(file_path, 'rb') as f:
#             # Prepare the files to upload
#             files = {
#                 'file': (doc.file_name, f)  # Use doc.file_name for the correct file name
#             }

#             # Prepare additional data
#             data = {
#                 'file_name': doc.file_name,
#                 'is_private': 0,  # 1 for private, 0 for public
#                 'folder': 'Home'
#             }

#             # Make the POST request to upload the file
#             response = requests.post(upload_url, headers=headers, files=files, data=data)

#             # Check the response
#             print("Response Status Code:", response.status_code)
#             if response.status_code == 200:
#                 response_data = json.loads(response.text)  # Load the response data
#                 print("Response Data:", response_data)  # Debugging line

#                 file_name = ""
#                 # Check if 'message' is in the response data
#                 if 'message' in response_data:
#                     file_info = response_data['message']
#                     print("File Info:", file_info)  # Debugging line

#                     # If file_info is a dict, check for file details
#                     if isinstance(file_info, dict) and 'message' in file_info:
#                         file_details = file_info['message']
#                         file_url = file_details.get('file_url', None) 
#                         file_name = file_details.get('file_name', None)  # Get the file name
#                         print("File URL:", file_url)

#                 if file_name:
#                     # Update the document with the new file URL
#                     uploaded_file_url = f"{frappe_url}/private/files/{file_name}"
#                     doc.db_set("file_url", uploaded_file_url)
#                     frappe.msgprint(f"File URL updated in the document: {uploaded_file_url}")
#                 else:
#                     frappe.msgprint("No file name returned from the server.")
#             else:
#                 frappe.msgprint(f"Failed to upload file: Status Code: {response.status_code}, Response: {response.text}", "File Upload Error")

#     except Exception as e:
#         print("Exception:", e)
#         frappe.msgprint(f"Error while uploading file: {str(e)}", "File Upload Exception")


def upload_file_to_frappe(doc, method):
    # Get the full file path
    file_path = doc.get_full_path()  # Assuming this method returns the full file path
    
    # Check if the file exists
    if not os.path.exists(file_path):
        frappe.msgprint(f"File does not exist: {file_path}", "File Upload Error")
        return

    # Frappe server details
    frappe_url = 'http://45.249.255.81:4414'
    api_key = "1236c2d8ff6c832"
    api_secret = "5afa9a3f903131b"

    # Prepare the URL for the upload
    upload_url = f"{frappe_url}/api/method/upload_file"
    time.sleep(1)  # Add a delay if needed for rate-limiting

    # Prepare the headers for authentication
    headers = {
        "Authorization": f"token {api_key}:{api_secret}"
    }
    print("Headers:", headers)

    try:
        with open(file_path, 'rb') as f:
            # Prepare the files to upload
            files = {
                'file': (doc.file_name, f)  # Use doc.file_name for the correct file name
            }

            # Prepare additional data
            data = {
                'file_name': doc.file_name,
                'is_private': 0,  # 1 for private, 0 for public
                'folder': 'Home'
            }

            # Make the POST request to upload the file
            response = requests.post(upload_url, headers=headers, files=files, data=data)

            # Check the response
            print("Response Status Code:", response.status_code)
            if response.status_code == 200:
                if isinstance(response.text, str):
                    # Parse the JSON string into a Python dictionary if it's a string
                    data = json.loads(response.text)
                else:
                    # If it's already a dictionary, no need to parse
                    data = response.text

                # Access the 'file_name' safely
                file_name = doc.file_name
                frappe.msgprint(file_name)

                if file_name:
                    # Update the document with the new file URL
                    uploaded_file_url = f"{frappe_url}/private/files/{file_name}"
                    doc.db_set("file_url", uploaded_file_url)
                    frappe.msgprint(f"File URL updated in the document: {uploaded_file_url}")

                    # Delete the file from the old server after successful upload
                    try:
                        os.remove(file_path)
                        frappe.msgprint(f"Local file deleted: {file_path}")
                        doc.db_set("file_size", 0)
                    except Exception as e:
                        frappe.msgprint(f"Failed to delete local file: {str(e)}", "File Deletion Error")
                else:
                    frappe.msgprint("No file name returned from the server.")

    except Exception as e:
        print("Exception:", e)
        frappe.msgprint(f"Error while uploading file: {str(e)}", "File Upload Exception")




def download_file_from_source_to_destination(doc, method):
    # Define your parameters for the source server (Frappe server)
    source_path = doc.get_full_path()  # Get the source file path
    frappe.msgprint(f"Source Path: {source_path}")

    # Define your parameters for the destination server (local server)
    # destination_server_ip = "45.240.255.81"  # IP of the local server (without port)
    # destination_user = "erpadmin"           # SSH username for the destination server
    # destination_password = "Erpd@t@123$LOCAL"  # SSH password for the destination server
    # destination_port = 2223                  # SSH port (should be allowed through the firewall)
    # local_file_path = source_path    
    # # Path where the file will be saved locally on the destination server
    destination_server_ip = "45.240.255.81"  # IP of the local server (without port)
    destination_user = "erpadmin"           # SSH username for the destination server
    destination_password = "Erpd@t@123$ALPHA"  # SSH password for the destination server
    destination_port = 2223                  # SSH port (should be allowed through the firewall)
    local_file_path = source_path  
    try:
        # Create an SSH client for the destination server
        ssh_destination = paramiko.SSHClient()
        ssh_destination.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        frappe.msgprint("Connecting to the destination server...")

        # Connect to the destination server
        ssh_destination.connect(destination_server_ip, username=destination_user, password=destination_password, port=destination_port)
        frappe.msgprint("Connected to the destination server.")

        # Use SFTP to upload the file to the destination server
        sftp_destination = ssh_destination.open_sftp()
        sftp_destination.put(local_file_path, "/home/erpadmin/attachments")  # Upload the file to the destination server
        sftp_destination.close()
        ssh_destination.close()

        frappe.msgprint(f"File downloaded successfully from the source server and uploaded to {destination_server_ip}.")

    except paramiko.SSHException as e:
        frappe.log_error(f"SSH connection error: {str(e)}")
        frappe.msgprint(f"SSH connection error: {str(e)}", "File Transfer Error")
    except FileNotFoundError as e:
        frappe.log_error(f"File not found: {str(e)}")
        frappe.msgprint(f"File not found: {str(e)}", "File Transfer Error")
    except Exception as e:
        frappe.log_error(f"Error transferring file: {str(e)}")
        frappe.msgprint(f"Error transferring file: {str(e)}", "File Transfer Error")


@frappe.whitelist()
def upload_file1(doc, method):
    # Get the external storage path from site_config
    config = frappe.get_site_config()
    path = config.get("external_storage", {}).get("path")
    
    frappe.msgprint(path)  # Debugging message

    if not path:
        frappe.throw(_("External storage path is not configured."))

    # Check if the file is present in the request
    if 'file' not in frappe.request.files:
        frappe.throw(_("No file was provided."))

    # Get the uploaded file
    file = frappe.request.files['file']

    # Create the full file path
    file_path = os.path.join(path, file.filename)
    frappe.msgprint(file_path)  # Debugging message

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    if file.content_length == 0:
        frappe.throw(_("Uploaded file is empty."))

    try:
        # Save the file
        with open(file_path, 'wb') as f:
            f.write(file.read())
        frappe.msgprint(_("File uploaded successfully."))
       
         # Construct the file URL for reference in the database
        # file_url = f"file://{file_path}"  # Use the file URI scheme for local files
        # frappe.msgprint(f"File URL: {file_url}")

        # Create and insert a new File document
        # new_file_doc = frappe.get_doc({
        #     "doctype": "File",
        #     "file_url": f"{"https://mobilecrm.erpdata.in"}/files/{file.name}",
        #     "file_name": file.name
        # })
        # new_file_doc.insert(ignore_permissions=True)
        frappe.msgprint(_("File path stored in the database successfully."))

    except Exception as e:
        frappe.throw(_("Failed to save file: {}").format(str(e)))

    return {"file_path": file_path, "message": _("File uploaded successfully.")}




def upload_file1(doc, method):
    # Get the external storage path from site_config
    config = frappe.get_site_config()
    path = config.get("external_storage", {}).get("path")

    # Debugging: Check if path is correct
    frappe.msgprint(f"External storage path: {path}")

    if not path:
        frappe.throw(_("External storage path is not configured."))

    # Check if the file is present in the request
    if 'file' not in frappe.request.files:
        frappe.throw(_("No file was provided."))

    # Get the uploaded file
    file = frappe.request.files['file']

    # Create the full file path
    file_path = os.path.join(path, file.filename)

    # Debugging: Log the full file path
    frappe.msgprint(f"Full file path: {file_path}")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    frappe.msgprint("Directory check completed.")  # Debugging

    try:
        # Save the file to the local folder
        frappe.msgprint("Attempting to save file...")  # Debugging
        with open(file_path, 'wb') as f:
            f.write(file.read())
        frappe.msgprint(_("File uploaded successfully."))

        # Construct the file URL for reference in the database
        file_url = "/files/" + file.filename

        
        new_file_doc = frappe.get_doc({
            "doctype": "File",
            "file_url": file_url,
            "file_name": file.filename
        })
        new_file_doc.insert(ignore_permissions=True)
        frappe.msgprint(_("File path stored in the database successfully."))

    except Exception as e:
        # Catch any errors and display
        frappe.throw(_("Failed to save file: {}").format(str(e)))

    return {"file_path": file_path, "message": _("File uploaded and reference saved successfully.")}

