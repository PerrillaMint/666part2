import socket

#Create a UDP socket
sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#bind it to local ip and port

server_ip="127.0.0.1" #the number is local host ip address
server_port=12345 #port number server will listen to
sock.bind((server_ip, server_port)) #BIND the socket to that ip and port

#part of phase 1 requirement to log communication
def send(reply, addr):
    print(f"[SEND] {addr} <- {reply}")   # log it
    sock.sendto(reply.encode("utf-8"), addr)   # actually send it
print("Server is listening on {}:{}".format(server_ip, server_port))

#handler functions
# REGISTER
def handle_register(message, addr):
    parts=message.split() #split the message into parts (list of string, like an array in cpp)

    if len(parts)<7:
        reply=f"REGISTER-DENIED {parts[1]} Message_format is invalid"
        send(reply, addr)
        return
    #PARSING the message into variables
    command=parts[0] #first part is the command
    req=parts[1] #request number is the second part
    name=parts[2]
    role=parts[3]
    valid_roles=["SUBSCRIBER", "PUBLISHER", "BOTH"] 
    #role condition: if role is not in valid_roles, send reply to client that role is invalid
    if role not in valid_roles:
        reply=f"REGISTER-DENIED {req} Invalid_Role"
        send(reply, addr)
        return
  
    ip=parts[4]
    udp_port=parts[5]
    tcp_port=parts[6] #for phase 2 and 3

    #to prevent duplicate
    exists=False

    try:
        with open("clients.txt", "r") as f: #r is read
            for line in f:
                if line.strip().startswith(name+" "):
                    exists=True
    except FileNotFoundError:
        pass

    if exists:
        reply=f"REGISTER-DENIED {req} Name_Already_Exists"
        send(reply, addr)
        return
    else:
        with open("clients.txt", "a") as f: #a is append
            f.write(f"{name} {role} {ip} {udp_port} {tcp_port}\n")

        locations= "[HALL, EV, JMSB, LOYOLA, SGW, ALL]"
        categories= "[FIRE, SECURITY, WEATHER, POWER, BUILDING, GENERAL, ALL]"
        reply=f"REGISTERED {req} {locations} {categories}"
    send(reply, addr)



# SUBSCRIBE: want alert for this location and this category
def handle_subscribe(message, addr):
    parts=message.split() #split the message into parts (list of string, like an array in cpp)

    if len(parts) < 4:
        reply = f"SUBSCRIPTION-DENIED {parts[1]} Malformed_Message"
        send(reply, addr)
        return
    
    command=parts[0] #first part is the command
    req=parts[1] #request number is the second part
    location=parts[2]
    category=parts[3]

    valid_locations = ["HALL", "EV", "JMSB", "LOYOLA", "SGW", "ALL"]
    valid_categories = ["FIRE", "SECURITY", "WEATHER", "POWER", "BUILDING", "GENERAL", "ALL"]

    if location not in valid_locations:
        reply = f"SUBSCRIPTION-DENIED {req} Invalid_Location"
        send(reply, addr)
        return

    if category not in valid_categories:
        reply = f"SUBSCRIPTION-DENIED {req} Invalid_Category"
        send(reply,addr)
        return
   
    sender_ip = addr[0] #which ip sent the subscribe request
    sender_udp = str(addr[1]) #which udp port sent the subscribe request

    client_name= None
    client_role= None

    try:
        with open("clients.txt", "r") as f: #r is read
            for line in f:
                name, role, ip, udp_port, tcp_port = line.strip().split()
                if ip == sender_ip and udp_port == sender_udp:
                    client_name = name
                    client_role = role
                    break

    except FileNotFoundError:
        pass
    if client_name is None:
        reply = f"SUBSCRIPTION-DENIED {req} Not_Registered"
        send(reply, addr)
        return

    if client_role not in ["SUBSCRIBER", "BOTH"]:
        reply =f"SUBSCRIPTION-DENIED {req} Role_Not_Allowed"
        send(reply, addr)
        return
    
    exists=False

    try:
        with open("subscriptions.txt", "r") as f: #r is read
            for line in f:
                if line.strip() == f"{client_name} {location} {category}":
                    exists = True

    except FileNotFoundError:
        pass

    if exists:
        reply=f"SUBSCRIPTION-DENIED {req} Already_Subscribed"
    else:
        with open("subscriptions.txt", "a") as f: #a is append
            f.write(f"{client_name} {location} {category}\n")
        reply=f"SUBSCRIBED {req}"

    send(reply, addr)

# UNSUBSCRIBE
def handle_unsubscribe(message, addr):
    parts=message.split() #split the message into parts (list of string, like an array in cpp)

    if len(parts) < 4:
        reply = f"UNSUBSCRIPTION-DENIED {parts[1]} Malformed_Message"
        send(reply,addr)
        return
    
    command=parts[0] #first part is the command
    req=parts[1]
    location=parts[2]
    category=parts[3]

    sender_ip = addr[0] #which ip sent the subscribe request
    sender_udp = str(addr[1]) #which udp port sent the subscribe request

    client_name= None
    client_role= None

    try:
        with open("clients.txt", "r") as f: #r is read
            for line in f:
                name, role, ip, udp_port, tcp_port = line.strip().split()
                if ip == sender_ip and udp_port == sender_udp:
                    client_name = name
                    client_role = role
                    break

    except FileNotFoundError:
        pass
    if client_name is None:
        reply = f"UNSUBSCRIPTION-DENIED {req} Not_Registered"
        send(reply,addr)
        return

    found=False #found boolean, false means haven't seen subscription yet
    new_lines=[] #list that contains all the lines we want to keep

    try:
        with open("subscriptions.txt", "r") as f: #r is read
            for line in f:
                if line.strip() == f"{client_name} {location} {category}":
                    found=True
                else:
                    new_lines.append(line)
    except FileNotFoundError:
        pass

    if found:
        with open("subscriptions.txt", "w") as f: #w is write
            for line in new_lines:
                f.write(line)
        reply=f"UNSUBSCRIBED {req}"
    else:
        reply=f"UNSUBSCRIPTION-DENIED {req} Not_Subscribed"

    send(reply,addr)

#DE-REGISTER
def handle_deregister(message, addr):
    parts=message.split() #split the message into parts (list of string, like an array in cpp)
    if len(parts) < 3:
        reply = "DE-REGISTRATION-DENIED 0 Malformed_Message"
        send(reply, addr)
        return

    command=parts[0] #first part is the command
    req=parts[1]

    sender_ip = addr[0] #which ip sent the subscribe request
    sender_udp = str(addr[1]) #which udp port sent the subscribe request
    
    client_name= None

    try:
        with open("clients.txt", "r") as f: #r is read
            for line in f:
                name, role, ip, udp_port, tcp_port = line.strip().split()
                if ip == sender_ip and udp_port == sender_udp:
                    client_name = name
                    break
    except FileNotFoundError:
        pass

    if client_name is None:
        reply = f"DE-REGISTRATION-DENIED {req} Not_Registered"
        send(reply,addr)
        return

    new_clients = []

    try:
        with open("clients.txt", "r") as f:
            for line in f:
                if not line.startswith(client_name + " "):
                    new_clients.append(line)
    except FileNotFoundError:
        new_clients = []

    with open("clients.txt", "w") as f:
        for line in new_clients:
            f.write(line)

    new_subs =[]

    try:
        with open("subscriptions.txt", "r") as f:
            for line in f:
                if not line.startswith(client_name + " "):
                    new_subs.append(line)
    except FileNotFoundError:
        new_subs = []

    with open("subscriptions.txt", "w") as f:
        for line in new_subs:
            f.write(line)   

    reply = f"DE-REGISTERED {req}"
    send(reply, addr)

    
#main loop (while)
while True:
    try:
        data, addr=sock.recvfrom(4096) #4096 max nb of bytes to receive
        message=data.decode("utf-8") #convert raw byte into readable text
        print(f"[RECV] {addr}: {message}") #print the message received from the client
        parts=message.split() #split the message into parts

        if not parts:
            continue
        command=parts[0] #first part is the command

        if command=="REGISTER":
            handle_register(message, addr)
        elif command=="SUBSCRIBE":
            handle_subscribe(message, addr)
        elif command=="UNSUBSCRIBE":
            handle_unsubscribe(message, addr)
        elif command=="DE-REGISTER":
            handle_deregister(message, addr)
        else:
            print("[WARN] Unknown command:", command)
    except Exception as e:
        print("[ERROR]", e)    
