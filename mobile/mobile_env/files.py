import os
import frappe
from frappe import _
import paramiko

# def upload_and_transfer_file(doc, method):
#     # Check if the file attachment field has a file
#     file_doc = frappe.get_doc("File", doc.name)

#     # Check for zero content length
#     if file_doc.file_size == 0:
#         frappe.throw(_("The uploaded file is empty. Please select a valid file."))

#     # Get the file details
#     file_name = file_doc.file_name
#     local_file_path = file_doc.get_full_path()  # The current file path on the source server
#     frappe.msgprint(local_file_path)
#     try:
#         # Transfer the file to the destination server
#         transfer_file_to_destination(local_file_path, file_name)

#         # Update the file URL in the database to reflect the destination server URL using IP address
#         # destination_ip = "45.240.255.81"  # Destination server IP address
#         # file_url = f"http://{destination_ip}/files/attachments/{file_name}"  # Create the new file URL

#         # key = file_doc.content_hash  # Keeping the current content_hash
#         # frappe.db.sql("""
#         #     UPDATE `tabFile` 
#         #     SET file_url=%s, folder=%s, old_parent=%s, content_hash=%s 
#         #     WHERE name=%s
#         # """, (file_url, 'Home/Attachments', 'Home/Attachments', key, file_doc.name))
#         # frappe.db.commit()

#         frappe.msgprint(f"File URL updated to TTTTT")

#     except Exception as e:
#         frappe.throw(_("Failed to transfer file: {}").format(str(e)))


# def transfer_file_to_destination(local_file_path, file_name):
#     # Define your parameters for the destination server
#     frappe.msgprint(local_file_path)
#     destination_server_ip = "45.249.255.81"  # IP of the destination server
#     destination_user = "erpadmin"            # SSH username for the destination server
#     destination_password = "Erpd@t@123$LOCAL"  # SSH password for the destination server
#     destination_port = 2223                  # SSH port
#     destination_path = "/home/abhishek/Attachments"  # Path where the file will be uploaded on the destination server

#     if not os.path.exists(destination_path):
#       frappe.throw(_("Path not found at: {}").format(destination_path))
#     try:
#         # Create an SSH client for the destination server
#         ssh_destination = paramiko.SSHClient()
#         ssh_destination.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         frappe.msgprint("Connecting to the destination server...")

#         # # Connect to the destination server
#         ssh_destination.connect(destination_server_ip, username=destination_user, password=destination_password, port=destination_port)
#         frappe.msgprint("Connected to the destination server.")

#         # # Use SFTP to upload the file to the destination server
#         sftp_destination = ssh_destination.open_sftp()
#         destination_file_path = os.path.join(destination_path, file_name)
#         frappe.msgprint(destination_file_path)
#         sftp_destination.put(local_file_path, destination_file_path)  # Upload the file
#         sftp_destination.close()
#         ssh_destination.close()

#         frappe.msgprint(f"File successfully transferred to {destination_server_ip}.")

#     except paramiko.SSHException as e:
#         frappe.log_error(f"SSH connection error: {str(e)}")
#         frappe.msgprint(f"SSH connection error: {str(e)}", "File Transfer Error")
#     except FileNotFoundError as e:
#         frappe.log_error(f"File not found: {str(e)}")
#         frappe.msgprint(f"File not found: {str(e)}", "File Transfer Error")
#     except Exception as e:
#         frappe.log_error(f"Error transferring file: {str(e)}")
#         frappe.msgprint(f"Error transferring file: {str(e)}", "File Transfer Error")


def upload_and_transfer_file(doc, method):
    # Check if the file attachment field has a file
    file_doc = frappe.get_doc("File", doc.name)

    # Check for zero content length
    if file_doc.file_size == 0:
        frappe.throw(_("The uploaded file is empty. Please select a valid file."))

    # Get the file details
    file_name = file_doc.file_name
    local_file_path = file_doc.get_full_path()  # The current file path on the source server
    frappe.msgprint(f"Local file path: {local_file_path}")

    # Server details for transfer
    destination_ip = "192.168.1.246"  # Destination server IP address
    username = "erpadmin"  # Replace with your SSH username
    password = "Erpd@t@123$ALPHA"  # Replace with your SSH password
    destination_path = "/home/erpadmin/attachments"  # Path to check on the destination server

    # Check if the destination path exists on the remote server
    if not check_remote_path_exists(destination_ip, username, password, destination_path):
        frappe.throw(_("Path not found at: {}").format(destination_path))
    
    try:
        # Transfer the file to the destination server
        # transfer_file_to_destination(local_file_path, destination_ip, username, password, destination_path)

        # # Update the file URL in the database to reflect the destination server URL using IP address
        # file_url = f"http://{destination_ip}/attachments/{file_name}"  # Create the new file URL
        # key = file_doc.content_hash  # Keep the current content_hash
        
        # # Update file information in the database
        # frappe.db.sql("""
        #     UPDATE `tabFile` 
        #     SET file_url=%s, folder=%s, old_parent=%s, content_hash=%s 
        #     WHERE name=%
        # """, (file_url, 'Home/Attachments', 'Home/Attachments', key, file_doc.name))
        # frappe.db.commit()
       

         frappe.msgprint(f"File URL updated to: TTT")

    except Exception as e:
        frappe.throw(_("Failed to transfer file: {}").format(str(e)))

def check_remote_path_exists(destination_ip, username, password, destination_path):
    """Check if a path exists on the remote server."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the remote server
        ssh.connect(destination_ip, username=username, password=password,port="8000")

        command = f'ls -l {destination_path}'
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()

        # Execute a command to check if the directory exists
        # stdin, stdout, stderr = ssh.exec_command(f'ls {destination_path}')
        paths = output.strip().split('\n')
        frappe.msgprint(paths)
        # Read the output
        error = stderr.read().decode()

        # Check for errors in the output
        if error and "No such file or directory" in error:
            return False  # Path does not exist

        return True  # Path exists

    except Exception as e:
        frappe.throw(_("Failed to connect to the destination server: {}").format(str(e)))
    finally:
        ssh.close()

def transfer_file_to_destination(local_file_path, destination_ip, username, password, destination_path):
    """Transfer a file to the destination server using SFTP."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the destination server
        ssh.connect(destination_ip, username=username, password=password,port="8000")
        sftp = ssh.open_sftp()

        # Define the destination file path
        remote_file_path = os.path.join(destination_path, os.path.basename(local_file_path))

        # Upload the file to the destination server
        sftp.put(local_file_path, remote_file_path)
        frappe.msgprint(f"File transferred successfully to: {remote_file_path}")

    except Exception as e:
        frappe.throw(_("Failed to transfer file to the destination server: {}").format(str(e)))
    finally:
        sftp.close()
        ssh.close()
