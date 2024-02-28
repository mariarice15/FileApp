About this program:
This program implements a file transfer protocol over UDP and TCP. Servers and clients communicate over UDP and clients communicate with each other over TCP. In order to keep track of all data, a sqlite database is used. In the database, one table ‘clientsNew’ holds all client data and another database ‘filesOffering’ holds all the file data.

How to run:
1. Begin the server
a. python <filepath> -s <port>
2. Begin clients
a. python <filepath> -c <name> <server-ip> <server-port> <client-udp-port>
<client-tcp-port> 3. To offer files:
a. setdir <directorypath>
b. offer <files>
i. files must be separated by a space
4. To see all offered file:
a. list
5. To deregister:
a. “Dereg”, “Deregister”, “dereg”, or “deregister” 6. To re-register
a. "re-register", "re-reg", "Re-reg", or "Re-register" 7. To request files
a. request <filename> <clientname>
