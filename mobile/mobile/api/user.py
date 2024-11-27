
import frappe



# @frappe.whitelist()
# def get_customer(user_id: str):
#    try:
#       swagger.validate_http_method("GET")
#       customer = frappe.get_doc("User", user_id)
#       return {"status": "success", "data": customer.as_dict()}
#    except frappe.DoesNotExistError:
#       return {"status": "error", "message": "User does not exist"}
#    except Exception as e:
#       swagger.log_api_error()
#       return {"status": "error", "message": str(e)}

# @frappe.whitelist(allow_guest=True)
# def delete_user(user_id: str):
#    try:
#       swagger.validate_http_method("DELETE")
#       frappe.delete_doc("User", user_id, ignore_permissions=True)
#       return {"status": "success", "message": f"User with ID {user_id} deleted successfully"}
#    except frappe.DoesNotExistError:
#       return {"status": "error", "message": "User does not exist"}
#    except Exception as e:
#       swagger.log_api_error()
#       return {"status": "error", "message": str(e)}