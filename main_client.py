import udp_client
import tcp_client

def getFileContent():
    msg = udp_client.get_attach_info()
    parts = msg.decode("utf-8").split()
    
    if len(parts) < 7:
        print("Unable to retrieve file")
        return

    command = parts[0]
    if command == "ATTACH_INFO":
        rq_nb   = parts[1]
        inc_nb  = parts[2]
        pubs_nm = parts[3]
        ip_addr = parts[4]
        tcp_prt = parts[5]
        file_nm = parts[6]
        print(f"From the given reply {ip_addr} {tcp_prt} {file_nm}")
        tcp_client.connect(ip_addr, int(tcp_prt))
        data = tcp_client.handle_get_attachments(tcp_client.sock, rq_nb, pubs_nm, inc_nb, file_nm)
        tcp_client.close()

        return data

udp_client.connect()
udp_client.register()
udp_client.subscribe()

print(f"Obtained file content of Andy_Has_Faith.pdf from Publisher Andy as: \n{getFileContent()}")

udp_client.unsubscribe()
udp_client.deregister()
udp_client.close()