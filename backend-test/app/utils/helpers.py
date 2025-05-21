from flask import jsonify

def success_response(message="Success", data=None, status_code=200):
    response = {"code": 0, "message": message}
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code

def error_response(message="Error", code=-1, status_code=400, error_details=None):
    response = {"code": code, "message": message}
    if error_details:
        response["error_details"] = str(error_details)
    return jsonify(response), status_code
