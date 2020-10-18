import socket
import re
from tkinter import StringVar, Listbox

BUFFER_SIZE = 1024


class AngryFtpClientService:
    def __init__(self, status: StringVar):
        # TCP socket
        self.socket = None
        self.server_ip = "127.0.0.1"
        self.server_port = 21

        self.data_socket = None
        self.data_mode = "PASV"
        self.data = []
        self.data_download_path = "./"
        self.data_upload_path = ""

        self.status = status

    def set_pasv(self, val: bool):
        if not val:
            self.data_mode = "PORT"
        else:
            self.data_mode = "PASV"

    def make_request(self, request):
        encoded_request = (request + "\r\n").encode()

        self.socket.sendall(encoded_request)

        if request in ["LIST", "RETR", "STOR"]:
            # Get 150 Opening binary data mode response
            self.get_response()
            self.process_data_response(request)

        return self.get_response()

    def get_response(self):
        response = self.socket.recv(BUFFER_SIZE).decode()
        print(response)
        while response[3] != ' ':
            response = self.socket.recv(BUFFER_SIZE).decode()
            print(response)
            if len(response) <= 0:
                raise Exception("No end statement.")
        self.set_status(response)
        return self.get_code(response), response

    def process_data_response(self, request: str):
        data = self.data_socket.recv(BUFFER_SIZE).decode()
        while len(data) > 0:
            print(data)
            self.data.append(data)
            data = self.data_socket.recv(BUFFER_SIZE).decode()
        # Transfer complete or connection dropped
        # Close socket and clear data
        self.data_socket.close()
        self.data.clear()
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
        else:
            # Remove \r\n
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

    def setup_data_connection(self):
        try:
            if self.data_mode == "PORT":
                pass
            # PASV mode
            else:
                code, response = self.make_request("PASV")
                if code != 227:
                    raise Exception("PASV failed")
                port_search = re.search(r"^227 .*\d{1,3},\d{1,3},\d{1,3},\d{1,3},(\d{1,3}),(\d{1,3})", response)
                data_port = 20000
                if port_search:
                    data_port = int(port_search.group(1)) * 256 + int(port_search.group(2))

                self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.data_socket.connect((self.server_ip, data_port))

        except Exception as e:
            print(f"Data Connection Setup Error: {str(e)}")
            self.set_status(str(e))
            return -1

    def update_list(self, listbox: Listbox):
        if self.setup_data_connection() == 1:
            return -1
        code, response = self.make_request("LIST")
        pass
