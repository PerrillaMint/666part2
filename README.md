# COEN366 – Phase 1: UDP Client/Server

This project implements the Phase 1 requirements for the COEN366 emergency notification system.

## Features

- REGISTER
- SUBSCRIBE
- UNSUBSCRIBE
- DE-REGISTER
- ATTACH_REQ
- GET_ATTACHMENTS

  All commands are handled by the UDP and TCP servers, which store client and subscription data in text files.

## How to Run

1. Start the UDP server:
   python udp_server.py

2. Start the TCP server:
   python tcp_server.py
   
3. Run the client:
   python main_client.py

The client sends REGISTER, SUBSCRIBE, ATTACH_REQ, GET_ATTACHMENTS, UNSUBSCRIBE, and DE-REGISTER commands to the server.

## Notes

- `clients.txt` and `subscriptions.txt` are generated at runtime.
- Do **not** push these files to GitHub.
