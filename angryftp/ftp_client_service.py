import socket
from tkinter import StringVar

BUFFER_SIZE = 1024


class AngryFtpClientService:
    def __init__(self, status: StringVar):
        # TCP socket
        self.socket = None
        self.data_socket = None
        self.status = status

    def make_request(self, request):
        request = request + "\r\n"
        self.socket.sendall(request.encode())
        return self.get_response()

    def get_response(self):
        response = self.socket.recv(BUFFER_SIZE).decode()
        print(response)
        # while response[4] != ' ':
        #     response = self.socket.recv(BUFFER_SIZE).decode()
        #     if len(response) <= 0:
        #         raise Exception("No end statement.")
        self.set_status(response)
        return self.get_code(response), response

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
            message = message[:length-2] + '\0'
        self.status.set(message)

    def connect(self, server_ip, server_port, username="anonymous", password="***"):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((server_ip, server_port))

            code, response = self.get_response()
            if code != 220:
                raise Exception("Connection error")

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
