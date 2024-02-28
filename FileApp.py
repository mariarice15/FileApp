import sys
import sqlite3
import time
from socket import *
import json
import threading
import re
import os

regex = r"^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
num_files = 0
file_table = []
global database_path


# Checks if given ip address is valid
def check_ip(ip):
    if re.search(regex, ip):
        return True
    else:
        return False


# Creates a table in the 'clientsNew.db' database to store all file information
def create_file_table():
    conn = sqlite3.connect('clientNew.db')
    c = conn.cursor()

    # Check if table already exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fileOffering'")
    table_exists = c.fetchone()
    if table_exists:
        # Drop table if it exists
        c.execute("DROP TABLE IF EXISTS fileOffering")
    # Create table
    c.execute('''CREATE TABLE fileOffering
                     (filename TEXT NOT NULL,
                      owner TEXT NOT NULL,
                      owner_ip TEXT NOT NULL,
                      owner_port INTEGER NOT NULL);''')
    conn.commit()
    conn.close()


# Returns the number of files a client has offered. Identifies client based off their tcp port number
def get_num_files_for_client(port):
    conn = sqlite3.connect('clientNew.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM fileOffering WHERE owner_port=?", (port,))
    files_num = c.fetchone()[0]
    conn.close()
    return files_num


# Inserts a new file into the 'fileOffering' table
def insert_file(filename, owner, client_ip, port):  # ADD CHECK IF ALREADY THERE
    global num_files
    conn = sqlite3.connect('clientNew.db')
    c = conn.cursor()

    # check if the file already exists in the table
    c.execute("SELECT * FROM fileOffering WHERE filename=? AND owner=?", (filename, owner))
    existing_file = c.fetchone()

    if existing_file:
        print("[File already exists in the table.]")
    else:
        c.execute("INSERT INTO fileOffering (filename, owner, owner_ip, owner_port) \
                   VALUES (?, ?, ?, ?)", (filename, owner, client_ip, port))
        conn.commit()
        num_files += 1
        print("[File added to the table.]")

    conn.close()


# Updates the data in 'fileOffering'. Used after significant program commands have been processed.
def update_files(rows):
    conn = sqlite3.connect('clientNew.db')
    c = conn.cursor()

    # iterate through each row
    for row in rows:
        client_name = row[1]
        online = row[2]
        ip = row[3]
        tcp_port = row[5]
        files = row[6]

        # split the files string into a list of filenames
        file_list = files.split(',')

        # iterate through each file for this client
        if online:
            for file in file_list:
                # check if the file already exists in the table
                c.execute("SELECT * FROM fileOffering WHERE filename=? AND owner=?", (file, client_name))
                existing_file = c.fetchone()
                if len(file) > 0 and not existing_file:
                    insert_file(file.replace(" ", ""), client_name, ip, tcp_port)

    conn.close()


# Returns all files in 'fileOffering' table
def get_all_files():
    conn = sqlite3.connect('clientNew.db')
    c = conn.cursor()
    c.execute("SELECT * FROM fileOffering")
    rows = c.fetchall()
    conn.close()
    return rows


# Returns the files a client offers. Identifies client based off their tcp port number.
def get_owner_files(port):
    conn = sqlite3.connect('clientNew.db')
    c = conn.cursor()
    c.execute("SELECT * FROM fileOffering WHERE owner_port=?", (port,))
    rows = c.fetchall()
    conn.close()
    return rows


# Prints a table of files offered (displays data in 'fileOffering')
def print_files(rows):
    # header
    print("{:<20} {:<20} {:<15} {:<10}".format("FILENAME", "OWNER", "IP ADDRESS", "TCP PORT"))

    # iterate through each row
    for row in rows:
        filename = row[0]
        filename = filename.replace("[", "")
        filename = filename.replace("]", "")
        owner = row[1]
        ip_address = row[2]
        tcp_port = row[3]
        tcp_port = tcp_port.replace("[", "")
        tcp_port = tcp_port.replace("]", "")
        # print each row
        print("{:<20} {:<20} {:<15} {:<10}".format(filename, owner, ip_address, tcp_port))


# Creates a table 'clientsNew' in 'clientsNew.db' database to store all the client information
def create_table():
    global database_path
    conn = sqlite3.connect('clientNew.db')
    c = conn.cursor()

    # Check if table already exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clientsNew'")
    table_exists = c.fetchone()
    if table_exists:
        # Drop table if it exists
        c.execute("DROP TABLE IF EXISTS clientsNew")
    # Create table

    c.execute('''CREATE TABLE clientsNew
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  online BOOLEAN NOT NULL,
                  ip TEXT NOT NULL,
                  udp_port INTEGER NOT NULL,
                  tcp_port INTEGER NOT NULL,
                  files TEXT NOT NULL);''')
    conn.commit()
    conn.close()


# Returns if a given client is online based off their name input
def is_client_online(name):
    conn = sqlite3.connect('clientNew.db')
    c = conn.cursor()
    c.execute("SELECT online FROM clientsNew WHERE name=?", (name,))
    row = c.fetchone()
    conn.close()

    if row is not None:
        if row[0] == "True":
            return True
    else:
        return False


# Inserts a new client into the 'clientsNew' table
def insert_client(name, online, ip, udp_port, tcp_port, files):
    conn = sqlite3.connect('clientNew.db')
    c = conn.cursor()
    c.execute("SELECT * FROM clientsNew WHERE name=? AND online=? AND ip=? AND udp_port=? AND tcp_port=?",
              (name, online, ip, udp_port, tcp_port))
    existing_client = c.fetchone()
    if existing_client:
        print("[Error: Client already exists in the table.]")
    else:
        # Insert new client
        c.execute(f"INSERT INTO clientsNew (name, online, ip, udp_port, tcp_port, files) \
                      VALUES ('{name}', '{online}', '{ip}', '{udp_port}', '{tcp_port}', '{files}')")
        print("[Client added to the table.]")

    conn.commit()
    conn.close()


# Returns all clients in 'clientsNew' table
def get_all_clients():
    conn = sqlite3.connect('clientNew.db')
    c = conn.cursor()
    c.execute("SELECT * FROM clientsNew")
    rows = c.fetchall()
    conn.close()
    return rows


# Returns client data for a client of a given name
def get_client_by_name(name):
    conn = sqlite3.connect('clientNew.db')
    c = conn.cursor()
    c.execute(f"SELECT * FROM clientsNew WHERE name='{name}'")
    row = c.fetchone()
    conn.close()
    return row


# Updates client data in 'clientsNew' table if the client already exists in the table
def update_client(name, online, ip=None, udp_port=None, tcp_port=None, files=None):
    conn = sqlite3.connect('clientNew.db')
    c = conn.cursor()

    if ip is not None:
        c.execute(f"UPDATE clientsNew SET ip='{ip}' WHERE name='{name}'")

    if online is not None:
        c.execute(f"UPDATE clientsNew SET online='{online}' WHERE name='{name}'")

    if udp_port is not None:
        c.execute(f"UPDATE clientsNew SET udp_port='{udp_port}' WHERE name='{name}'")

    if tcp_port is not None:
        c.execute(f"UPDATE clientsNew SET tcp_port='{tcp_port}' WHERE name='{name}'")

    if files is not None:
        c.execute(f"UPDATE clientsNew SET files='{files}' WHERE name='{name}'")

    conn.commit()
    conn.close()


# De-registers an offline client
def offline_client(udp_port, tcp_port):
    global num_files
    # update the number of files offered
    n = get_num_files_for_client(tcp_port)
    num_files = num_files - n

    conn = sqlite3.connect('clientNew.db')
    c = conn.cursor()
    # Update the online status of the client to False
    c.execute(f"UPDATE clientsNew SET online='False' WHERE udp_port='{udp_port}'")
    conn.commit()
    conn.close()


# Re-registers an online client
def online_client(udp_port, tcp_port):
    global num_files
    # update the number of files offered
    n = get_num_files_for_client(tcp_port)
    num_files = num_files + n

    conn = sqlite3.connect('clientNew.db')
    c = conn.cursor()
    # Update the online status of the client to False
    c.execute(f"UPDATE clientsNew SET online='True' WHERE udp_port='{udp_port}'")
    conn.commit()
    conn.close()


# Sends a message once and waits for an ACK. If a message is not sent successfully, retries twice. Returns whether
# message sent successfully.
def send_with_retry(from_socket, message, send_address):
    # Send a message and retry up to 2 times after 500 milliseconds if the server does not respond with an ACK
    for i in range(3):  # Try sending the message 3 times (initial try + 2 retries
        failed = False
        from_socket.sendto(message.encode(), send_address)
        start_time = time.time_ns()
        while not failed:
            if (time.time_ns() - start_time) > 5000000:
                failed = True
        packet, address = from_socket.recvfrom(1024)  # Receive a response
        if packet.decode() == 'ACK':
            # We received an ACK, so return
            return True
        else:
            print(f"[Timeout occurred. Retrying ({i + 1}/3)...]")
    return False


# Updates the data of files offered for a given client address in the 'clientsNew' table
def files_client(files, client_address):
    conn = sqlite3.connect('clientNew.db')
    c = conn.cursor()

    # Retrieve the previous value of the files field for the client
    c.execute("SELECT files FROM clientsNew WHERE udp_port=?", (int(client_address[1]),))
    row = c.fetchone()
    combined = ""
    if row is not None:
        prev_files = row[0]
        # Clean data
        combined = prev_files.replace("\"", "")
        combined = combined.replace(",", '')
        combined = combined.replace("'", '"')
        combined = combined.replace("\\", "")
        combined = combined.replace("/", "")
    else:
        prev_files = ''

    prev_files_list = combined.split()

    # Combine the new and previous files and remove duplicates
    for x in files:
        if str(x) not in prev_files:
            prev_files_list.append(x)

    # clean data to get rid of random symbols
    combined = json.dumps(prev_files_list)[1:-1].replace("\"", "")
    combined = combined.replace(",,", ',')
    combined = combined.replace("'", '"')
    combined = combined.replace("\\", "")
    combined = combined.replace("/", "")

    # Update the file offerings of the client
    c.execute(f"UPDATE clientsNew SET files='{combined}' WHERE udp_port='{int(client_address[1])}'")
    conn.commit()
    conn.close()

    # Updates the data in the 'fileOffering' table accordingly
    update_files(get_all_clients())


# Sends all clients the most updated version of the files data table. Sent from a given server udp port.
def broadcast_clients(server_udp):
    # Buffer to allow for all updates to be made before sending
    time.sleep(.5)

    global num_files
    rows_clients = get_all_clients()
    rows_files = get_all_files()
    all_files = []

    # Iterates through all files
    for i, x in enumerate(rows_files):
        # If a file owner is online, adds the file to the data table
        if is_client_online(str(rows_files[i][1])):
            all_files.append(x)

    # Iterates through all clients
    for row in rows_clients:
        if row[2] == "True":
            online = True
        else:
            online = False
        ip = row[3]
        udp_port = row[4]

        time.sleep(.5)

        # If a client is online, send the client data table to them
        if online:
            response = f"CLIENT TABLE {num_files}"
            server_udp.sendto(response.encode(), (ip, int(udp_port)))
            if len(all_files) > 0:
                for i in range(num_files):
                    # Properly clean and format data for sending
                    response = json.dumps(all_files[i])
                    response = response.replace("[", "")
                    response = response.replace("]", "")
                    send_with_retry(server_udp, response, (ip, int(udp_port)))
        else:
            response = f"CLIENT TABLE {num_files}"
            server_udp.sendto(response.encode(), (ip, int(udp_port)))


# Main Server Method
def create_server(port):
    # Clears database from previous runs
    if os.path.exists("clientsNew.db"):
        os.remove("clientsNew.db")
    # Creates table of clients
    create_table()
    # Creates table of files
    create_file_table()

    # Establishes the server IP and UDP port
    server_address = (gethostbyname(gethostname()), int(port))
    server_udp = socket(AF_INET, SOCK_DGRAM)
    server_udp.bind(server_address)
    print(f"[Server listening on port {port}]")

    # Server is in a constant loop of listening for messages from clients
    while True:
        # Receives incoming data
        packet, client_address = server_udp.recvfrom(1024)
        if packet.decode().startswith("ACK"):
            ack = True
        # A client de-registers
        elif packet.decode().startswith("OFFLINE"):
            # Get a client's tcp port given their udp port number
            conn = sqlite3.connect('clientNew.db')
            c = conn.cursor()
            udp_port = int(client_address[1])
            c.execute("SELECT tcp_port FROM clientsNew WHERE udp_port=?", (udp_port,))
            result = c.fetchone()
            conn.close()
            tcp_port = result[0] if result else None
            # Mark client as Offline
            offline_client(udp_port, tcp_port)
            # Send acknowledgement of receipt to client
            response = 'ACK'.encode()
            server_udp.sendto(response, client_address)
            response = 'ACK'.encode()
            server_udp.sendto(response, client_address)
            # Send updates to all clients
            broadcast_clients(server_udp)
        # A client re-registers
        elif packet.decode().startswith("ONLINE"):
            # Get a client's tcp port given their udp port number
            conn = sqlite3.connect('clientNew.db')
            c = conn.cursor()
            udp_port = int(client_address[1])
            c.execute("SELECT tcp_port FROM clientsNew WHERE udp_port=?", (udp_port,))
            result = c.fetchone()
            conn.close()
            tcp_port = result[0] if result else None
            # Mark client as Online
            online_client(udp_port, tcp_port)
            # Send acknowledgement of receipt to client
            response = 'ACK'.encode()
            server_udp.sendto(response, client_address)
            response = 'ACK'.encode()
            server_udp.sendto(response, client_address)
            # Send updates to all clients
            broadcast_clients(server_udp)
        # A client is offering files
        elif packet.decode().startswith("FILES"):
            # Creates a list of the files
            client_data = packet.decode().split()
            client_data.remove("FILES")
            try:
                # Attempts to begin a file thread which updates the data of files in the 'clientsNew' table
                files_thread = threading.Thread(target=files_client, args=[client_data, client_address])
                files_thread.start()
            except Exception:
                # Prints error message if unsuccessful
                print("[Error: Could not update files. Please retry.]")
            finally:
                # If successful, send ACKs
                response = 'ACK'.encode()
                server_udp.sendto(response, client_address)
                response = 'ACK'.encode()
                server_udp.sendto(response, client_address)
                # Broadcast updated file data to all clients
                broadcast_clients(server_udp)
        # Assume other incoming messages are for client registration
        else:
            client_data = packet.decode().split()
            if get_client_by_name(client_data[1]) is None:
                # If the client is not in the data table, add it
                insert_client(client_data[1], True, str(client_address[0]), int(client_data[2]), int(client_data[3]),
                              "")
            else:
                # If the client is in the data table, update its data using given info
                update_client(client_data[1], True, str(client_address[0]), int(client_data[2]), int(client_data[3]),
                              "")

            # Send ack to signal that the client was successfully added
            response = "ACK".encode()
            server_udp.sendto(response, client_address)

            # respond to the client with a table offered files by all clients
            response = f"CLIENT TABLE {num_files}"
            server_udp.sendto(response.encode(), client_address)
            all_files = get_all_files()
            test = num_files
            for i in range(num_files):
                response = json.dumps(all_files[i])
                if i == test - 1:
                    if send_with_retry(server_udp, response, client_address):
                        # Successfully sent
                        print("[Client table updated.]")
                    else:
                        # Error sending
                        print("[Error updating client table.]")
                else:
                    server_udp.sendto(response.encode(), client_address)

    # clean up the server socket when the program ends
    server_socket.close()


# Main Client Method
def create_client(name, server_ip, server_port, client_udp_port, client_tcp_port):

    # Create a UDP socket for communicating with the server
    client_udp = socket(AF_INET, SOCK_DGRAM)
    client_udp.bind(('', int(client_udp_port)))

    # Create a TCP socket for communicating with other clients
    client_tcp = socket(AF_INET, SOCK_STREAM)
    client_tcp.bind(('', int(client_tcp_port)))

    # Starts a thread for listening to and sending UDP messages (communication with server)
    client_udp_thread = threading.Thread(target=client_udp_listen,
                                         args=[name, client_udp, client_udp_port, client_tcp_port, server_ip,
                                               server_port])
    client_udp_thread.start()

    # Starts a thread for listening to TCP messages (communication with other clients)
    client_tcp_thread = threading.Thread(target=client_tcp_communication,
                                         args=[client_tcp, name])
    client_tcp_thread.start()

    # Starts a thread for listening to command line input
    client_command_thread = threading.Thread(target=client_command_listen,
                                             args=[name, client_udp, server_ip, server_port])
    client_command_thread.start()


# Client: listening to and sending UDP messages (communication with server)
def client_udp_listen(name, client_udp, client_udp_port, client_tcp_port, server_ip, server_port):
    # Register the client with the server by sending a UDP packet
    message = f"REGISTER {name} {client_udp_port} {client_tcp_port}"

    # Register the client with the server by sending a UDP packet
    if send_with_retry(client_udp, message, (server_ip, int(server_port))):
        print("[Welcome, You are registered.]")
    else:
        print("[Registration failed.]")
        exit()

    # Boolean to check if client is receiving file table data
    in_table = False

    # Constantly listen for messages
    while True:

        global file_table

        # Wait for server to send message
        response, server_address = client_udp.recvfrom(1024)

        if response.decode().startswith("ACK"):
            ack = True

        elif response.decode().startswith("CLIENT"):
            in_table = True
            num = int(response.decode()[13])
            i = 0
            file_table = []

        # Accept and properly save table data
        elif in_table and is_client_online(name):
            if len(response.decode()) > 0:
                i += 1
                row = response.decode()
                row = row.replace("\"", "")
                row = row.replace(",", "")
                row = row.split()
                file_table.append(row)
                client_udp.sendto("ACK".encode(), server_address)

            if i == num:
                # Send ack to the server
                client_udp.sendto("ACK".encode(), server_address)

                # Display appropriate message
                print("[Client table updated.]")
                in_table = False

        else:
            # Display error if unsuccessful
            print("[Error updating client table.]")
            exit()

    # disconnect
    client_udp.close()


# Client: listening to TCP messages (communication with other clients)
def client_tcp_communication(client_tcp, name):
    client_tcp.listen(1)  # listen for incoming connections, maximum 1 connection

    # Constantly listen
    while True:
        # Checks if client is online (if client offline, ignore requests)
        if is_client_online(name):
            recv_socket, recv_address = client_tcp.accept()  # accept incoming connection

            # Accept incoming message
            msg = recv_socket.recv(1024)
            msg = msg.decode('utf-8')

            # Checks if the message is a request
            if msg.startswith("request"):
                msg = msg.split()
                name = msg[2]
                print(f'< Accepted connection request from {recv_address[0]} >')

                # Confirms connection with other client
                message = "ACK"
                recv_socket.send(message.encode())

                # Boolean to check if first data packet is being sent
                first = True
                try:
                    # Send the requested file to the receiving client
                    with open(msg[1], "rb") as f:
                        while True:
                            if first:
                                print(f'< Transferring {msg[1]}... >')
                                first = False
                            data = f.read(1024)
                            if not data:
                                break
                            recv_socket.sendall(data)
                    recv_socket.send(b'SEND_DONE')
                    print(f'< {msg[1]} transferred successfully >')
                except ConnectionRefusedError:
                    print("< Error: Connection failed >")
                    return
                except TimeoutError:
                    print("< Error: Connection attempt timed out >")
                    return

                recv_socket.close()
                print(f'< Connection with {msg[2]} closed >')

    client_tcp.close()  # close the client socket


# Client: method for receiving a file after sending a request
def receive_file(msg, name):
    conn = sqlite3.connect('clientNew.db')
    c = conn.cursor()
    # check if the file already exists in the table
    c.execute("SELECT * FROM fileOffering WHERE filename=? AND owner=?", (msg[1], msg[2]))
    existing_file = c.fetchone()
    conn.close()

    # if the file doesn't exist in the table, print error
    if not existing_file:
        print("< Invalid Request >")
    else:
        # Get owner's IP and TCP port from the clients table
        conn = sqlite3.connect('clientNew.db')
        c = conn.cursor()
        c.execute("SELECT ip, tcp_port FROM clientsNew WHERE name=?", (msg[2],))
        result = c.fetchone()
        conn.close()
        if result is None:
            print("< Error: Could not find owner in clients table >")
            return
        owner_ip, owner_tcp_port = result

        # Establish TCP connection with owner
        print("< Establishing TCP connection with owner... >")
        owner_tcp_sock = socket(AF_INET, SOCK_STREAM)
        try:
            owner_tcp_sock.connect((owner_ip, owner_tcp_port))
        # Display error messages if connection could not be established
        except ConnectionRefusedError:
            print("< Error: Connection was refused by owner's machine >")
            return
        except TimeoutError:
            print("< Error: Connection attempt timed out >")
            return
        print("< Connection with", msg[2], "established. >")

        # Send request message to owner
        message = f"request {msg[1]} {name}"
        owner_tcp_sock.send(message.encode())

        # Receive response from owner
        response = owner_tcp_sock.recv(1024).decode()
        if response != "ACK":
            print("< Error: Owner could not fulfill request >")
            owner_tcp_sock.close()
            return

        # Receive file from owner and save to local directory
        local_file_path = os.path.join(os.getcwd(), msg[1])
        first = True
        with open(local_file_path, 'wb') as f:
            while True:
                if first:
                    print(f'< Downloading {msg[1]}... >')
                    first = False
                data = owner_tcp_sock.recv(1024)
                if not data or data.startswith(b'SEND_DONE'):
                    break
                f.write(data)

        print(f"< File {msg[1]} downloaded successfully! >")
        owner_tcp_sock.close()
        print("< Connection with", msg[2] ,"closed. >")


# Client: listens for command line input
def client_command_listen(name, client_udp, server_ip, server_port):
    # Boolean to track if a directory has been set before file offering
    isSet = False
    set_dir = ""
    # Constantly listen for input
    while True:
        sys.stdin = open('/dev/tty')
        value = str(sys.stdin.readline()).strip()
        # Check for deregister command
        if value in ['deregister', 'dereg', 'Dereg', 'Deregister']:
            if not is_client_online(name):
                print("[Client is already offline.]")
            else:
                server_address = (server_ip, int(server_port))
                # Marks client offline
                result = send_with_retry(client_udp, "OFFLINE", server_address)
                if result:
                    print("[You are Offline. Bye.]")
                else:
                    print("[Server not responding]")
                    print("[Exiting]")
                    exit()
        # Check for re-register command
        elif value in ["re-register", "re-reg", "Re-reg", "Re-register"]:
            if is_client_online(name):
                print("[Client is already online.]")
            else:
                server_address = (server_ip, int(server_port))
                # Marks client online
                result = send_with_retry(client_udp, "ONLINE", server_address)
                if result:
                    print("[Successfully Re-registered]")
                else:
                    print("[No ACK from Server, please try again later.]")

        # Check for list command (display file table)
        elif value == "list":
            global file_table
            if len(file_table) > 0:
                print_files(file_table)
            else:
                print("[No files available for download at the moment.]")
        # Check for setdir command to set a directory
        elif value.startswith("setdir"):
            values = value.split()
            set_dir = values[1]
            try:
                os.chdir(set_dir)
                isSet = True
                print("[Successfully set", set_dir, "as the directory for searching offered files.]")
            except OSError:
                print("[setdir failed:", set_dir, "does not exist.]")
        # Check for files being offered
        elif value.startswith("offer"):
            # Confirm a directory has first been set
            if isSet:
                values = value.split()
                files = values[1:]
                valid = True
                message = f"FILES"
                # Concatenate a string of all files being offered
                for x in files:
                    file_path = set_dir + "/" + x
                    try:
                        os.path.isfile(file_path)
                        message += " "
                        message += str(x)
                    # Display error if file is not in given directory
                    except OSError:
                        print("[Error: file", x, "cannot be found in the directory.]")
                        valid = False
                # If no error, send string of files to the server
                if valid:
                    server_address = (server_ip, int(server_port))
                    result = send_with_retry(client_udp, message, server_address)
                    if result:
                        print("[Offer Message received by Server.]")
                    else:
                        print("[No ACK from Server, please try again later.]")

                    isSet = False
            # Display error if directory has not been set
            else:
                print("[Error: Must set directory first]")
        # Check for file request
        elif value.startswith("request"):
            msg = value
            msg = msg.replace("<", "")
            msg = msg.replace(">", "")
            msg_list = msg.split()

            # Request file
            receive_file(msg_list, name)
        else:
            print("[Error: Invalid command]")


if __name__ == '__main__':
    if len(sys.argv) >= 2:

        if sys.argv[1] == "-s":
            if not (1024 <= int(sys.argv[2]) <= 65535):
                print("[Error: Port is not in range 1024-65535.]")
                exit()
            else:
                print("[Starting Server]")
                server_thread = threading.Thread(target=create_server, args=[int(sys.argv[2])])
                server_thread.start()

        elif sys.argv[1] == "-c":
            if len(sys.argv) != 7:
                print("[Please enter all necessary arguments]")
                print("[-c <name> <server-ip> <server-port> <client-udp-port> <client-tcp-port>]")
                exit()
            exist = get_client_by_name(sys.argv[2])
            if exist is not None:
                print("[Error: Client name already exists.]")
                exit()
            elif not (1024 <= int(sys.argv[5]) <= 65535):
                print("[Error: UDP port is not in range 1024-65535.]")
                exit()
            elif not (1024 <= int(sys.argv[6]) <= 65535):
                print("[Error: TCP port is not in range 1024-65535.]")
                exit()
            elif not check_ip(sys.argv[3]):
                print("[Error: Invalid IP address.]")
                exit()
            else:
                create_client(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])

    else:
        print(f"[Please select a mode.]")
        print(f"[CLIENT: '-c <name> <server-ip> <server-port> <client-udp-port> <client-tcp-port>']")
        print(f"[SERVER: '-s <port>']")
        exit()
