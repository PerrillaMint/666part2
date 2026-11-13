import socket
import zlib

server_ip = "127.0.0.1"
server_port = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#REQUEST ATTACHMENT DATA
def handle_get_attachments(sock, rq_nb, sub_name, inc_nb, fname):
    msg = f"GET_ATTACHMENT {rq_nb} {sub_name} {inc_nb} {fname}"
    sock.send(msg.encode("utf-8")) # print(f"Sent: {rawMsg}, waiting for response...")
    reply = sock.recv(4096)
    print("[CRECV] ", reply.decode("utf-8")) #decode the reply and print it
    if reply:
        header_data = reply.decode("utf-8").split("|10000001|")

        parts = header_data[0].split()
        command = parts[0]
        if command == "ATTACH_DATA":
            data = header_data[1]
            for i in range(2, len(header_data)):
                data += "|10000001|" + header_data[i] # Just in case for whatsoever what reason this sequence is in the file as well

            if len(parts) < 6:
                msg = f"ATTACH_ERROR {parts[1]} {parts[2]} {parts[3]} Malformed_Message"
                print("[CSEND] ", msg)
                sock.send(msg.encode("utf-8"))
                return

            checksum = parts[5]
            sumchecker = zlib.crc32(data.encode("utf-8")) & 0xffffffff
            if str(sumchecker) == checksum:
                msg = f"ATTACH_OK {parts[1]} {parts[2]} {parts[3]}"
            else:
                msg = f"ATTACH_ERROR {parts[1]} {parts[2]} {parts[3]} Checksum_Mismatch"
                
            print("[CSEND] ", msg)
            sock.send(msg.encode("utf-8"))
    else:
        msg = f"ATTACH_ERROR {rq_nb} {inc_nb} {fname} Malformed_Message"
        print("[CSEND] ", msg)
        sock.send(msg.encode("utf-8"))

    return data

def connect(ip, port):
    sock.connect((ip, port))  
    # handle_get_attachments(sock, 91, "Andy", "INC100", "Andy_Has_Faith.pdf")

def close():
    sock.close()