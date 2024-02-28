# File Transfer Program

## About This Program

This program implements a file transfer protocol over UDP and TCP. Servers and clients communicate over UDP, while clients communicate with each other over TCP. To keep track of all data, a SQLite database is used. The database comprises two tables: `clientsNew`, which holds all client data, and `filesOffering`, which contains all the file data.

## How to Run

1. **Begin the Server**
   - Run the following command:
     ```
     python <filepath> -s <port>
     ```

2. **Begin Clients**
   - Run the following command:
     ```
     python <filepath> -c <name> <server-ip> <server-port> <client-udp-port> <client-tcp-port>
     ```

3. **To Offer Files:**
   - Set the directory path:
     ```
     setdir <directorypath>
     ```
   - Offer files:
     ```
     offer <files>
     ```
     - Files must be separated by a space.

4. **To See All Offered Files:**
   - Run:
     ```
     list
     ```

5. **To Deregister:**
   - Enter any of the following commands:
     - "Dereg", "Deregister", "dereg", or "deregister"

6. **To Re-register:**
   - Enter any of the following commands:
     - "re-register", "re-reg", "Re-reg", or "Re-register"

7. **To Request Files:**
   - Run:
     ```
     request <filename> <clientname>
     ```

