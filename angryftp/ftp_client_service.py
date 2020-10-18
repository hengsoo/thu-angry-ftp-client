import socket
import re
import random
from tkinter import StringVar, Listbox, END

BUFFER_SIZE = 1024


class AngryFtpClientService:
    def __init__(self, status: StringVar):
        # TCP socket
        self.socket = None
        self.server_ip = "127.0.0.1"
        self.server_port = 21

        self.data_listen_socket = None
        self.data_socket = None
        self.data_connection_mode = "PORT"
        self.data = []
        self.data_download_path = "./"
        self.data_upload_path = ""

        self.status = status

    def __del__(self):
        if self.data_listen_socket:
            self.data_listen_socket.close()
        if self.data_socket:
            self.data_socket.close()
        if self.socket:
            self.socket.close()

    def set_pasv(self, val: bool):
        if not val:
            self.data_connection_mode = "PORT"
        else:
            self.data_connection_mode = "PASV"

    def make_request(self, request):
        encoded_request = (request + "\r\n").encode()

        self.socket.sendall(encoded_request)

        if request[:4] in ["LIST", "RETR", "STOR"]:
            # Listen for connection is mode is PORT
            if self.data_connection_mode == "PORT":
                self.data_listen_socket.listen()
                self.data_socket, addr = self.data_listen_socket.accept()
            # Get 150 Opening binary data mode response
            self.get_response()
            # Save data
            self.save_data_response(self.data)

        return self.get_response()

    def get_response(self):
        while True:
            response = self.socket.recv(BUFFER_SIZE).decode()
            print(response)
            if len(response) <= 0:
                raise Exception("No end statement.")
            if response[3] == ' ':
                break

        self.set_status(response)
        return self.get_code(response), response

    def save_data_response(self, save_point: list):
        data = self.data_socket.recv(BUFFER_SIZE).decode()
        while len(data) > 0:
            save_point.append(data)
            data = self.data_socket.recv(BUFFER_SIZE).decode()
        # Transfer complete or connection dropped
        # Close socket
        if self.data_connection_mode == "PORT":
            self.data_listen_socket.close()
        self.data_socket.close()
        return 0

    @staticmethod
    def get_code(response):
        if len(response) < 3:
            return -1
        return int(response[:3])

    def set_status(self, message):
        length = len(message)
        if length > 55:
            message = message[:52] + "..."
        # Remove \r\n
        if message[length - 2:length] == "\r\n":
            message = message[:length - 2] + '\0'
        self.status.set(message)

    def connect(self, server_ip: str, server_port: int, username="anonymous", password="***"):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((server_ip, server_port))

            code, response = self.get_response()
            if code != 220:
                raise Exception("Connection error")

            self.server_ip, self.server_port = server_ip, server_port

            self.make_request(f"USER {username}")
            self.make_request(f"PASS {password}")
            self.make_request(f"SYST")
            self.make_request(f"TYPE I")

            return 0
        except Exception as e:
            print(f"Error: {str(e)}")
            self.set_status(str(e))
            return -1

    def disconnect(self):
        self.make_request("QUIT")
        self.socket.close()
        return 0

    @staticmethod
    def get_host_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        host_ip = s.getsockname()[0]
        s.close()
        return host_ip

    def setup_data_connection(self):
        try:
            if self.data_connection_mode == "PORT":
                # Create socket
                self.data_listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                ip = self.get_host_ip()
                port = random.randint(20000, 65535)

                self.data_listen_socket.bind((ip, port))

                request_ip = ip.replace('.', ',')
                code, response = self.make_request(f"PORT {request_ip},{port // 256},{port % 256}")
                if code != 200:
                    raise Exception("PORT failed")

            # PASV mode
            else:
                # Create socket
                self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                code, response = self.make_request("PASV")
                if code != 227:
                    raise Exception("PASV failed")
                port_search = re.search(r"^227 .*\d{1,3},\d{1,3},\d{1,3},\d{1,3},(\d{1,3}),(\d{1,3})", response)
                data_port = 20000
                if port_search:
                    data_port = int(port_search.group(1)) * 256 + int(port_search.group(2))

                self.data_socket.connect((self.server_ip, data_port))

        except Exception as e:
            print(f"Data Connection Setup Error: {str(e)}")
            self.set_status(str(e))
            return -1

    def print_current_directory(self):
        code, response = self.make_request("PWD")
        return response

    def change_current_directory(self, new_dir):
        self.make_request(f"CWD {new_dir}")
        return 0

    def update_list(self, listbox: Listbox):
        try:
            if self.setup_data_connection() == 1:
                return -1
            code, response = self.make_request("LIST")
            if code != 226:
                raise Exception("LIST update failed")
            # If list is empty
            if len(self.data) < 1:
                return 1

            # self.data is a list of single string containing the dir list
            self.data = self.data[0].split("\r\n")
            for directory in self.data:
                if len(directory) < 1:
                    continue
                list_detail = " "
                # If directory is folder >, else it is a file -
                list_detail += ("> " if directory[0] == 'd' else "- ")
                directory_name = (re.search(r"\s([\w\d.]+)$", directory)).group(1)
                list_detail += directory_name
                listbox.insert(END, list_detail)
            # Clear data
            self.data.clear()
            return 0

        except Exception as e:
            print(f"Update List error: {str(e)}")
            self.set_status(str(e))
            return -1
