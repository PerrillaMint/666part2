
import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(("127.0.0.1", 5001))# making sure it matches with the client.txt
client_socket.settimeout(3)  # wait max 3 seconds for a reply, then raise a timeout error instead of hanging forever
server_ip = "127.0.0.1"
server_port = 12345

# REGISTER
msg = "REGISTER 01 Mari SUBSCRIBER 127.0.0.1 5001 6001"
client_socket.sendto(msg.encode("utf-8"), (server_ip, server_port)) #send message to server
reply,addr= client_socket.recvfrom(4096) #receive reply from server
print("Server replied", reply.decode("utf-8")) #decode the reply and print it


#SUBSCRIBE
msg = "SUBSCRIBE 02 HALL WEATHER"
client_socket.sendto(msg.encode("utf-8"), (server_ip, server_port)) #send message to server
reply,addr= client_socket.recvfrom(4096) #receive reply from server
print("Server replied", reply.decode("utf-8")) #decode the reply and print it

#DEREGISTER
msg= "DE-REGISTER 03 Mari"
client_socket.sendto(msg.encode("utf-8"), (server_ip, server_port)) #send message to server
reply,addr= client_socket.recvfrom(4096) #receive reply from server
print("Server replied", reply.decode("utf-8")) #decode the reply and print it

