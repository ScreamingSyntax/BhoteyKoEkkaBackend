def error_message(message):
    return {
        "success":0,
        "message":message
    }

def success_with_no_data(message):
    return {
        "success":1,
        "message":message
    }

def success_with_data(data):
    return {
        "success":1,
        "data":data
    }

def success_session_expiry():
    return {
        "success":-1,
        "message":"Session Expired"
    }
