import os
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 9999))

def file_saving():
    file_path = input("Enter the file path: ")
    if not os.path.exists(file_path):
        print("File not found.")
        return

    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    client.send("1".encode())
    client.send(f"{file_name}\n".encode())  # Send the name WITH the newline
    client.send(f"{file_size}\n".encode())

    with open(file_path, "rb") as file:
        while True:
            data = file.read(1024)
            if not data:
                break
            client.sendall(data)
    print("File sent")

def download_file():
    client.send("2".encode())
    data = client.recv(4096).decode()  # Receive the list of files
    print("Available files:")
    print(data)
    
    index_file = int(input("Enter the number of the file : "))

    client.send(f"{index_file}".encode())
    is_normal = int(client.recv(1024).decode())

    if not is_normal: return

    folder_path = input("Enter the folder path you want to save in : ")
    if (os.path.exists(folder_path)):
        client.send("1-folder".encode())
    else:
        is_normal = False
        client.send("0-folder".encode())
        return
    
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
        with open(f"{folder_path}/{file_name}", "wb") as file:
            file.write(file_bytes)
        print(f"File '{file_name}' received and saved.")
    else:
        print(f"File '{file_name}' received incompletely. Expected {file_size} bytes, received {received_size} bytes.")

if __name__ == "__main__":
    choice = -1

    while choice != 3:
        try:
            choice = int(input("Enter the choice (1 - save file, 2 - download file, 3 - disconnect): "))

            if choice == 3:
                client.send("3".encode())
                break  # Exit loop but keep the connection open until the server closes it
            elif choice == 1:
                file_saving()
            elif choice == 2:
                download_file()
            else:
                print("Invalid choice")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except Exception as e:
            print(f"An error occurred: {e}")

    client.close()  # Close the connection only after exiting the loop