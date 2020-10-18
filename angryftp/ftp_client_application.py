from tkinter import *
from .ftp_client_service import AngryFtpClientService


class AngryFtpClientApplication:
    def __init__(self, master):

        self.master = master
        self.master.title("Angry FTP Client")

        self.main_frame = Frame(self.master).pack(padx=10)

        self.addresses = {
            "ftp_ip": StringVar(value="192.168.0.183"),
            "ftp_port": StringVar(value=2121),
            "host_ip": "127.0.0.1",
            "host_port": 21
        }
        self.username = StringVar(value="anonymous")
        self.password = StringVar(value="banana")
        # Init in login_ui
        self.connection_state_label = None
        self.auth_button = None

        self.status = StringVar(value="Welcome to AngryFtpClient")
        # Init in explorer ui
        self.current_directory = ""
        self.current_directory_label = StringVar(value="Directory Path: ")
        self.file_explorer_listbox = None
        self.upload_file_path = StringVar()
        self.connection_mode = StringVar(value="PASV")

        self.ftp = AngryFtpClientService(self.status)
        self.master.protocol("WM_DELETE_WINDOW", quit)
        self.ui()

    def ui(self):
        self.login_ui()
        self.file_explorer_ui()
        self.status_and_download_ui()
        self.rename_ui()
        self.upload_ui()
        self.connection_mode_ui()

    def quit(self):
        self.ftp.disconnect()
        self.master.destroy()

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

        self.auth_button = Button(self.main_frame, text="Connect", font='Helvetica 9 bold',
                                  width=20, fg="white", bg="green",
                                  command=self.auth)

        self.connection_state_label = \
            Label(self.main_frame, text="Disconnected", bg="red", fg="white",
                  font='Helvetica 11 bold')

        self.connection_state_label.pack(side=TOP, fill=BOTH)
        login_frame.pack(side=TOP, padx=5, pady=2, expand=1, fill=X)

        ip_label.grid(row=0, column=0, pady=2)
        ip_input.grid(row=0, column=1, padx=4)
        port_label.grid(row=0, column=2)
        port_input.grid(row=0, column=3)

        username_label.grid(row=1, column=0)
        username_input.grid(row=1, column=1)
        password_label.grid(row=1, column=2)
        password_input.grid(row=1, column=3)

        self.auth_button.pack(side=TOP, pady=2)

    def auth(self):
        # Login
        if self.connection_state_label.cget("text") == "Disconnected":
            return_val = self.ftp.connect(
                self.addresses["ftp_ip"].get(), int(self.addresses["ftp_port"].get()),
                self.username.get(), self.password.get()
            )
            if return_val == 0:
                self.connection_state_label.config(text="Connected", bg="green")
                self.auth_button.config(text="Disconnect", bg="red")
                self.update_list()
        # Logout
        else:
            self.ftp.disconnect()
            self.connection_state_label.config(text="Disconnected", bg="red")
            self.auth_button.config(text="Connect", bg="green")

    def file_explorer_ui(self):
        file_explorer_frame = Frame(self.main_frame, padx=10)

        file_explorer_label = Label(file_explorer_frame,
                                    textvariable=self.current_directory_label, width=52, anchor=W)

        self.file_explorer_listbox = Listbox(file_explorer_frame, height=10, width=60, activestyle="none")
        scrollbar = Scrollbar(file_explorer_frame)

        self.file_explorer_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_explorer_listbox.yview)

        file_explorer_frame.pack(side=TOP)
        file_explorer_label.pack(side=TOP)
        self.file_explorer_listbox.pack(side=LEFT, fill=BOTH, pady=(0, 10))
        scrollbar.pack(side=RIGHT, fill=BOTH)

        # self.file_explorer_listbox.insert(END, "=== Welcome to ANGRY FTP CLIENT ===")
        # self.update_list()

    def update_list(self):
        self.file_explorer_listbox.delete(0, "end")
        self.ftp.update_list(self.file_explorer_listbox)
        self.update_directory()

    def update_directory(self):
        label = "Directory Path: "
        # remove code and ""
        directory = (self.ftp.print_current_directory())[5:-3]
        label += directory
        self.current_directory_label.set(label)

    def status_and_download_ui(self):
        status_download_frame = Frame(self.main_frame, padx=5)

        status_frame = LabelFrame(status_download_frame, text="Status")
        status_label = \
            Label(status_frame, textvariable=self.status, anchor=W, width=45)

        # Save as file
        download_button = Button(status_download_frame, text="Download")

        status_download_frame.pack(side=TOP, pady=(0, 5), padx=0, expand=1, fill=X)
        status_frame.pack(side=LEFT)
        status_label.pack()
        download_button.pack(side=RIGHT, pady=(8, 0), padx=5)

    def rename_ui(self):
        rename_frame = LabelFrame(self.main_frame, text="Rename to", padx=5, pady=2)
        rename_input = Entry(rename_frame, width=50)
        rename_button = Button(rename_frame, text="Confirm")

        rename_frame.pack(side=TOP, padx=5, pady=2, expand=1, fill=X)
        rename_input.pack(side=LEFT, padx=5)
        rename_button.pack(side=RIGHT)

    def upload_ui(self):
        upload_frame = LabelFrame(self.main_frame, text="Upload", padx=5, pady=2)
        upload_label = Label(upload_frame, text="File:")
        upload_input = Entry(upload_frame, width=40)
        upload_browse_button = Button(upload_frame, text="Browse")
        upload_button = Button(upload_frame, text="Upload")

        upload_frame.pack(side=TOP, padx=5, pady=2, expand=1, fill=X)
        upload_label.pack(side=LEFT)
        upload_input.pack(side=LEFT, padx=5)
        upload_browse_button.pack(side=LEFT, padx=5)
        upload_button.pack(side=LEFT)

    def connection_mode_ui(self):
        mode_frame = Frame(self.main_frame, pady=5)
        mode_label = Label(mode_frame, text="Connection Mode")
        port_button = \
            Radiobutton(mode_frame, text="PORT", value="PORT", variable=self.connection_mode, indicator=0)
        pasv_button = \
            Radiobutton(mode_frame, text="PASV", value="PASV", variable=self.connection_mode, indicator=0)

        mode_frame.pack(side=TOP, padx=5, pady=2, expand=1, fill=X)
        mode_label.pack(side=TOP)
        port_button.pack(side=LEFT, expand=1, fill=X)
        pasv_button.pack(side=LEFT, expand=1, fill=X)
