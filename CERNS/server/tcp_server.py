import socket
import zlib
import struct

#Create a UDP socket
sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#bind it to local ip and port

server_ip="127.0.0.1" #the number is local host ip address
server_port=12345 #port number server will listen to
sock.bind((server_ip, server_port)) #BIND the socket to that ip and port

#part of phase 1 requirement to log communication
def send(reply, connection):
    print(f"[SEND] {addr} <- {reply}")   # log it
    connection.send(reply.encode("utf-8"))   # actually send it

#handler functions
# ATTACH REQUEST
def handle_get_attachment(message, conn):
    parts=message.split() #split the message into parts (list of string, like an array in cpp)
    if len(parts) < 5:
        reply = f"ATTACH-ERROR {parts[1]} {parts[2]} Malformed_Message"
        send(reply, conn)
        return

    command=parts[0] #first prt is the command
    req=parts[1]
    pubs_name=parts[2]
    incident_nb=parts[3]
    filename=parts[4]

    try:
        with open("../incidents.txt", "r") as f: #r is read
            found=False
            for line in f:
                inc_nb, publisher_name, ip_addr, port, filename_in_file = line.strip().split() # format of the incidents in incidents.txt
                print(f"[DEBUG] Checking incident: {inc_nb}, {publisher_name}, {ip_addr}, {port}, {filename} {filename_in_file}")  # Debugging line
                if inc_nb == incident_nb and filename_in_file == filename:
                    found=True
                    break
            if found==False:
                reply = f"ATTACH-DENIED {req} {inc_nb} File_Not_Found"
                send(reply, conn)
                return
    except FileNotFoundError:
        reply = f"ATTACH-DENIED {req} {incident_nb} Incident_Not_Found"
        send(reply, conn)
        return

    print(f"[DEBUG] Found incident: {inc_nb}, {publisher_name}, {ip_addr}, {port}, {filename_in_file}")  # Debugging line
    with open(f"urgent_files/{filename}", "r", encoding="utf-8") as f:
        file_data = f.read()

    checksum = zlib.crc32(file_data.encode("utf-8")) & 0xffffffff  # Calculate CRC32 checksum
    
    reply_header = f"ATTACH_DATA {req} {incident_nb} {filename} {len(file_data)} {checksum}"
    reply = reply_header + "|10000001|" + file_data # 10000001 is a good header, the | | is just to ensure the checksum for some reason isnt that value
    send(reply, conn)
    data = conn.recv(4096)  # Wait for ACK from client
    print(f"[RECV] {addr}: {data.decode('utf-8')}")  # Log the ACK received from the client

def handle_get_active_alerts(message, conn):
    parts=message.split() #split the message into parts (list of string, like an array in cpp)
    if len(parts) < 3:
        reply = f"ATTACH-ERROR {parts[1]} {parts[2]} Malformed_Message"
        send(reply, conn)
        return

    command=parts[0] #first prt is the command
    req=parts[1]
    subs_name=parts[2]

    try:
        with open("clients.txt", "r") as f: #r is read
            found=False
            for line in f:
                name = line.strip().split()[0]
                if name == subs_name:
                    found=True
                    break
            if not found:
                reply = f"ATTACH-DENIED {req} {inc_nb} Not_Registered"
                send(reply, conn)
                return
    except FileNotFoundError:
        pass

    msg = f"ACTIVE_ALERTS {req} 2" # Place holder waiting for ALERTS to be done
    send(msg, conn);
    
# Accept TCP connection
print("Server is listening on {}:{}".format(server_ip, server_port))
sock.listen(1)

#main loop (while)
while True:
    connection, addr = sock.accept()
    with connection:
        data = connection.recv(4096) #4096 max nb of bytes to receive
        message=data.decode("utf-8") #convert raw byte into readable text
        print(f"[RECV] {addr}: {message}") #print the message received from the client
        parts=message.split() #split the message into parts

        if not parts:
            continue
        command=parts[0] #first part is the command

        if command=="GET_ATTACHMENT":
            handle_get_attachment(message, connection)
        else:
            print("[WARN] Unknown command:", command)
