# Protocol.py defines how clients and servers communicate.

#-------------------------------------------------
# CENRS - Communication Protocol
#-------------------------------------------------

import json

# Valid user roles
ROLES=[
    "SUBSCRIBER",
    "PUBLISHER",
    "BOTH"
]

# Valid campus locations
LOCATIONS =[
    "HALL",
    "EV",
    "JMSB",
    "LOYOLA",
    "SGW",
    "ALL"
]

# Valid emergency Categories
CATEGORIES = [
    "FIRE",
    "SECURITY",
    "WEATHER",
    "POWER",
    "BUILDING",
    "GENERAL",
    "ALL"
]

# Valid incident severities
SEVERITIES = [
    "INFO",
    "WARNING",
    "CRITICAL"
]

# Valid incident statuses
STATUSES = [
    "ACTIVE",
    "CLOSED"
]

# Valid user response statuses
USER_STATUSES = [
    "SAFE",
    "NEED_HELP",
    "LEFT_AREA"
]

#-------------------------------------------------
# define valid message commands
#-------------------------------------------------

COMMANDS = [

    # Registration
    "REGISTER",
    "REGISTERED",
    "REGISTER-DENIED",
    "DE-REGISTER",

    #Suscriptions
    "SUBSCRIBE",
    "SUBSCRIBED",
    "SUBSCRIPTION-DENIED",
    "UNSUBSCRIBE",
    "UNSUBSCRIBED"

    #Publishing Incidents
    "PUBLISH_ALERT",
    "ALERT_ACCEPTED",
    "ALERT_DENIED",

    #Alerts
    "ALERT",
    "ALERT_ACK",

    #incident updates
    "UPDATE_ALERT",
    "ALERT_UPDATED",
    "ALERT_UPDATE",

    #closing incidents
    "CLOSE_ALERT",
    "ALERT_CLOSED",
    "ALL_CLEAR",

    #user safety report
    "STATUS_REPORT",
    "STATUS_RECORDED",
    "STATUS_REJECTED",

    #requesting attachment source
    "ATTACH_REQ",
    "ATTACH_INFO",
    "ATTACH_DENIED",

    #Direct TCP attachment transfer
    "GET_ATTACHMENT",
    "ATTACH_DATA",
    "ATTACH_OK",
    "ATTACH_ERROR",

    #Recovering Current Emergency Information
    "GET_ACTIVE_ALERTS",
    "ACTIVE_ALERTS"
]

#-------------------------------------------------
# define required message fields
#-------------------------------------------------

REQUIRED_FIELDS ={

    #Registration
    "REGISTER":[
        "request_id", "name", "role", "ip", "udp_port", "tcp_port" 
    ],

    "REGISTERED" : [
        "request_id", "location_list", "category_list"
    ],

    "REGISTER-DENIED": [
        "request_id", "reason"
    ],

    "DE-REGISTER": [
        "request_id", "name"
    ],

    #Alert Subscription
    "SUBSCRIBE": [
        "request_id", "location", "category"
    ],
    
    "SUBSCRIBED": [
        "request_id"
    ],

    "SUBSCRIPTION-DENIED": [
        "request_id", "reason"
    ],

    "UNSUBSCRIBE": [
        "request_id", "location", "category"
     ],

    "UNSUBSCRIBED": [
         "request_id"
    ],

    #publishing emergency Incident
    "PUBLISH_ALERT":[
        "request_id", "category", "location", "severity", "title", "description", "attachment"
    ],

    "ALERT_ACCEPTED": [
        "request_id", "incident_id"
    ],

    "ALERT_DENIED": [
        "request_id", "reason"
    ],

    # Emergency Alert Distribution
    "ALERT": [
        "request_id", "incident_id", "version","category", "location", "severity", "title", "description", "attachment"
    ],

    "ALERT_ACK": [
        "request_id", "incident_id", "version", "name"
    ],

    #Updating existing incident
    "UPDATE_ALERT": [
        "request_id", "incident_id", "severity", "title", "description"
    ],

    "ALERT_UPDATED": [
        "request_id", "incident_id", "version"
    ],
     
    "ALERT_UPDATE": [
        "request_id", "incident_id", "version", "severity", "title", "description"
    ],

    # closing incidents
    "CLOSE_ALERT":[
        "request_id", "incident_id", "reason"
    ],

    "ALERT_CLOSED":[
        "request_id", "incident_id"
    ],

    "ALL_CLEAR":[
        "request_id", "incident_id", "version", "message"
    ],

    # User safety 
    "STATUS_REPORT":[
        "request_id", "incident_id", "name", "status"
    ],

    "STATUS_RECORDED": [
        "request_id"
    ],

    "STATUS_REJECTED": [
        "request_id", "reason"
    ],

    # Requesting the Attachment Source

    "ATTACH_REQ": [
        "request_id", "incident_id", "file_name"
    ],

    "ATTACH_INFO":[
        "request_id", "incident_id", "publisher_name", "ip", "tcp_port", "file_name"
    ],

    "ATTACH_DENIED": [
        "request_id", "incident_id", "reason"
    ],

    # Direct Publisher-to-Subscriber Transfer
    "GET_ATTACHMENT": [
        "request_id", "subscriber_name", "incident_id", "file_name"
    ],

    "ATTACH_DATA": [
        "request_id", "incident_id", "file_name", "file_size", "checksum"
    ],

    "ATTACH_OK": [
        "request_id", "incident_id", "file_name"
    ],

    "ATTACH_ERROR": [
        "request_id", "incident_id", "file_name", "reason"
    ], 

    # Recovering Current Emergency Information
    "GET_ACTIVE_ALERTS": [
        "request_id", "name"
    ],

    "ACTIVE_ALERTS": [
        "request_id", "number_alerts"
    ]   
}

#-------------------------------------------------
# Build message - function to create a JSON message instead of us creating it every time
#-------------------------------------------------

def build_msg(command, **fields): # command: type of message, fields: allows to pass other additional info
    
    data = {
        "command": command,
        **fields
    }

    if command not in COMMANDS:
        raise ValueError("Unknown command")
    
    valid, reason = validate_msg(data)

    if not valid:
        raise ValueError(reason)


    return json.dumps(data)


#-------------------------------------------------
# Validate message - check if message follows protocols' rules
#-------------------------------------------------

def check_required_fields(data):
    if "command" not in data:
        return False, "Missing command"

    command = data["command"]

    if command not in COMMANDS:
        return False, "Unknown command"

    if command not in REQUIRED_FIELDS:
        return False, "No required fields defined for command"

    for field in REQUIRED_FIELDS[command]:
        if field not in data:
            return False, f"Missing required field: {field}"

    return True, None


def validate_msg(data):
    if not isinstance(data, dict): #check if msg is in the dictionary
        return False, "message is invalid, follow the rules :( )"
    
    valid, reason = check_required_fields(data) # check if all message fields are there
    if not valid:
        return False, reason

    command = data["command"]

    # perform the check for every command group
    
    if command == "REGISTER": #check role
        if data["role"] not in ROLES:
            return False, "Invalid Role"

    if command in ["ALERT", "SUBSCRIBE", "UNSUBSCRIBE", "PUBLISH_ALERT"]: #check location
        if data["location"] not in LOCATIONS:
            return False, "Invalid location"

    if command == "REGISTERED": #check location list
        if not isinstance(data["location_list"], list):
            return False, "location_list must be a list"

        for location in data["location_list"]:
            if location not in LOCATIONS:
                return False, f"Invalidd location: {location}"

    if command == "REGISTERED": #check category list
        if not isinstance(data["category_list"], list):
                return False, "category_list must be a list"
           
        for category in data["category_list"]:
            if category not in CATEGORIES:
                return False, f"Invalidd category: {category}"
    
    if command in ["SUBSCRIBE", "UNSUBSCRIBE", "PUBLISH_ALERT", "ALERT"]: # check category
        if data["category"] not in CATEGORIES:
            return False, "Invalid Category"        
    
    if command in ["PUBLISH_ALERT", "ALERT", "UPDATE_ALERT", "ALERT_UPDATE"]: # check severity
        if data["severity"] not in SEVERITIES:
            return False, "Invalid Severity"

    if command == "STATUS_REPORT":
        if data["status"] not in USER_STATUSES:
            return False, "Invalid user status"

    return True, None
 
        
#-------------------------------------------------
# Parse message
#-------------------------------------------------

def parse_msg(message):
    try:
        if isinstance(message, bytes): # convert to bytes if needed
            message=message.decode("utf-8")

        data = json.loads(message) 
        valid, reason = validate_msg(data)

        if not valid:
            raise ValueError(reason)

        return data

    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as e:
        raise ValueError(f"Invalid message: {e}")