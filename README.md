# COEN366 – Phase 1: UDP Client/Server

This project implements the Phase 1 requirements for the COEN366 emergency notification system.

## Features

- REGISTER
- SUBSCRIBE
- UNSUBSCRIBE
- DE-REGISTER

All commands are handled by the UDP server, which stores client and subscription data in text files.

## How to Run

1. Start the server:
   python udp_server.py

2. Run the client:
   python udp_client.py

The client sends REGISTER, SUBSCRIBE, and DE-REGISTER commands to the server.

## Notes

- `clients.txt` and `subscriptions.txt` are generated at runtime.
- Do **not** push these files to GitHub.
