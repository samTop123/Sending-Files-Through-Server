import socket
import os

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 9999))
server.listen(5)

print("Server has been started!")

if __name__ == "__main__":
    while True:
        client, addr = server.accept()
        print(f"Accepted connection from {addr}")

        try:
            while True:  # Keep the connection open for multiple choices
                choice = client.recv(1024).decode()
                if not choice:
                    break  # Exit loop if client disconnects

                print(f"Choice received: {choice}")

                if choice == "1":
                    file_name_data = b""
                    while True:
                        part = client.recv(1)
                        if part == b'\n':
                            break
                        file_name_data += part
                    file_name = file_name_data.decode()
                    print(f"File name: {file_name}")

                    size_data = b""
                    while True:
                        part = client.recv(1)
                        if part == b'\n':
                            break
                        size_data += part
                    file_size = int(size_data.decode())
                    print(f"File size: {file_size}")

                    file_bytes = b""
                    received_size = 0

                    while received_size < file_size:
                        data = client.recv(1024)
                        if not data:
                            break
                        file_bytes += data
                        received_size += len(data)

                    if received_size == file_size:
                        os.makedirs("UserFiles", exist_ok=True)
                        with open(f"UserFiles/{file_name}", "wb") as file:
                            file.write(file_bytes)
                        print(f"File '{file_name}' received and saved.")
                    else:
                        print(f"File '{file_name}' received incompletely. Expected {file_size} bytes, received {received_size} bytes.")

                elif choice == "2":
                    file_list = os.listdir("UserFiles") if os.path.exists("UserFiles") else []
                    response = "\n".join([f"{i} : {file}" for i, file in enumerate(file_list)]) + "\n"
                    client.send(response.encode())

                    index_file = int(client.recv(1024).decode())
                    print(f"The index file is : {index_file} !")

                    is_normal = False

                    if abs(index_file) >= len(file_list):
                        client.send("0".encode())
                        is_normal = False
                    else:
                        client.send("1".encode())
                        is_normal = True

                    if is_normal:
                        folder_result = client.recv(1024).decode()

                        if folder_result == "1-folder":
                            print("The folder is existing !")
                        else:
                            print("The folder is not existing !")
                            is_normal = False
                    
                        if is_normal:
                            file_path = f"UserFiles\\{file_list[index_file]}"
                            file_name = os.path.basename(file_path)
                            file_size = os.path.getsize(file_path)

                            print(f"File path : {file_path}")

                            client.send(f"{file_name}\n".encode())  # Send the name WITH the newline
                            client.send(f"{file_size}\n".encode())

                            with open(file_path, "rb") as file:
                                while True:
                                    data = file.read(1024)
                                    if not data:
                                        break
                                    client.sendall(data)
                            print("File sent")
                elif choice == "3":
                    print(f"Client {addr} has been disconnected.")
                    break  # Exit the loop and close the connection

                else:
                    print(f"Invalid choice from {addr}: {choice}")

        except ConnectionResetError:
            print(f"Client {addr} disconnected abruptly.")
        except Exception as e:
            print(f"An error occurred with client {addr}: {e}")
        finally:
            client.close()