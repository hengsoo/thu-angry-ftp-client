from tkinter import *


class FtpClientApplication:
    def __init__(self, master):
        self.master = master
        self.main_frame = Frame(self.master).pack(padx=2, pady=(0, 2))

        self.addresses = {
            "ftp_ip": StringVar(value="127.0.0.1"),
            "ftp_port": StringVar(value=21),
            "host_ip": "127.0.0.1",
            "host_port": 21
        }
        self.username = StringVar(value="anonymous")
        self.password = StringVar(value="banana")
        self.connection_state = StringVar(value="Disconnected")

        self.status = StringVar(value="Welcome to AngryFtpClient")
        self.file_explorer = ""
        self.ui()

    def ui(self):
        self.master.title("Angry Ftp Client")
        self.login_ui()
        self.file_explorer_ui()
        self.status_and_download_ui()

    def login_ui(self):
        # This will create a LabelFrame
        login_frame = LabelFrame(self.main_frame, text='Login', padx=5, pady=5)
        # this wil create a label widget
        ip_label = Label(login_frame, text="IP:", anchor=W, width=8)
        ip_input = Entry(login_frame, textvariable=self.addresses["ftp_ip"])
        port_label = Label(login_frame, text="Port:", anchor=W, width=8)
        port_input = Entry(login_frame, textvariable=self.addresses["ftp_port"])
        username_label = Label(login_frame, text="Username:")
        username_input = Entry(login_frame, textvariable=self.username)
        password_label = Label(login_frame, text="Password:")
        password_input = Entry(login_frame, textvariable=self.password, show="*")

        auth_button = Button(self.main_frame, text="Connect", width=20)

        connection_state_label = \
            Label(self.master, textvariable=self.connection_state, bg="red", fg="white",
                  font='Helvetica 11 bold')

        connection_state_label.pack(side=TOP, fill=BOTH)
        login_frame.pack(side=TOP, padx=5, pady=2)

        ip_label.grid(row=0, column=0, pady=2)
        ip_input.grid(row=0, column=1, padx=4)
        port_label.grid(row=0, column=2)
        port_input.grid(row=0, column=3)

        username_label.grid(row=1, column=0)
        username_input.grid(row=1, column=1)
        password_label.grid(row=1, column=2)
        password_input.grid(row=1, column=3)

        auth_button.pack(side=TOP, pady=2)

    def file_explorer_ui(self):
        file_explorer_frame = Frame(self.main_frame, padx=10)
        self.file_explorer = Listbox(file_explorer_frame, height=10, width=60)
        scrollbar = Scrollbar(file_explorer_frame)

        self.file_explorer.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_explorer.yview)

        file_explorer_frame.pack(side=TOP)
        self.file_explorer.pack(side=LEFT, fill=BOTH, pady=10)
        scrollbar.pack(side=RIGHT, fill=BOTH)
        for values in range(100):
            self.file_explorer.insert(END, values)

    def status_and_download_ui(self):
        status_download_frame = Frame(self.main_frame)

        status_frame = LabelFrame(status_download_frame, text="Status")
        status_label = \
            Label(status_frame, textvariable=self.status, anchor=W, width=40)

        download_button = Button(status_download_frame, text="Download")

        status_download_frame.pack(side=TOP, pady=(0, 5))
        status_frame.pack(side=LEFT, padx=5, fill=X)
        status_label.pack()
        download_button.pack(side=LEFT, pady=(8, 0))
