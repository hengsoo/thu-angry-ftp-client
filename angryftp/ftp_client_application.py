from tkinter import *
from tkinter.filedialog import asksaveasfile, askopenfilename
from .ftp_client_service import AngryFtpClientService


class AngryFtpClientApplication:
    def __init__(self, master):

        self.master = master
        self.master.title("Angry FTP Client")

        self.main_frame = Frame(self.master).pack(padx=10)

        self.address = {
            "ftp_ip": StringVar(value="192.168.0.183"),
            "ftp_port": StringVar(value=2121)
        }
        self.username = StringVar(value="anonymous")
        self.password = StringVar(value="blue banana")
        # Init in login_ui
        self.connection_state_label = None
        self.auth_button = None

        self.status = StringVar(value="Welcome to AngryFtpClient")
        # Init in explorer ui
        self.current_directory = "/"
        self.current_directory_label = StringVar(value="/")
        self.file_explorer_listbox = None
        self.rename_to = StringVar()
        self.upload_file_path = StringVar()
        self.new_folder_name = StringVar()
        self.data_connection_mode = StringVar(value="PASV")

        self.ftp = AngryFtpClientService(self.status)
        self.master.protocol("WM_DELETE_WINDOW", quit)
        self.ui()

    def ui(self):
        self.login_ui()
        self.file_explorer_ui()
        self.status_and_download_ui()
        self.upload_ui()
        self.folder_ui()
        self.rename_ui()
        self.others_ui()
        self.connection_mode_ui()

    def quit(self):
        self.ftp.disconnect()
        self.master.destroy()

    def login_ui(self):
        # This will create a LabelFrame
        login_frame = LabelFrame(self.main_frame, text='Login', padx=5, pady=5)
        # this wil create a label widget
        ip_label = Label(login_frame, text="IP:", anchor=W, width=8)
        ip_input = Entry(login_frame, textvariable=self.address["ftp_ip"])
        port_label = Label(login_frame, text="Port:", anchor=W, width=8)
        port_input = Entry(login_frame, textvariable=self.address["ftp_port"])
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
                self.address["ftp_ip"].get(), int(self.address["ftp_port"].get()),
                self.username.get(), self.password.get()
            )
            if return_val == 0:
                self.connection_state_label.config(text="Connected", bg="green")
                self.auth_button.config(text="Disconnect", bg="red")
                self.update_list()
        # Logout
        else:
            self.ftp.disconnect()
            self.file_explorer_listbox.delete(0, END)
            self.connection_state_label.config(text="Disconnected", bg="red")
            self.auth_button.config(text="Connect", bg="green")

    def file_explorer_ui(self):
        file_explorer_control_frame = Frame(self.main_frame, padx=10)
        file_explorer_frame = Frame(self.main_frame, padx=10)

        file_explorer_label = Label(file_explorer_control_frame, text="Directory Path: ")
        file_explorer_path = Label(file_explorer_control_frame,
                                   textvariable=self.current_directory_label, width=32, anchor=W)
        go_to_parent_button = Button(file_explorer_control_frame, text="Go back",
                                     command=self.go_to_parent_dir)

        self.file_explorer_listbox = Listbox(file_explorer_frame, height=10, width=62, activestyle="none")
        self.file_explorer_listbox.bind("<Double-Button>", self.change_directory)

        scrollbar = Scrollbar(file_explorer_frame)

        self.file_explorer_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_explorer_listbox.yview)

        file_explorer_control_frame.pack(side=TOP)
        file_explorer_label.pack(side=LEFT)
        file_explorer_path.pack(side=LEFT)
        go_to_parent_button.pack(side=LEFT, padx=5)

        file_explorer_frame.pack(side=TOP, pady=3)
        self.file_explorer_listbox.pack(side=LEFT, fill=BOTH, pady=(0, 10))
        scrollbar.pack(side=RIGHT, fill=BOTH)

    def update_list(self):
        self.file_explorer_listbox.delete(0, END)
        self.update_directory_label()
        self.ftp.update_list(self.file_explorer_listbox)

    def update_directory_label(self):
        # remove code and ""
        directory = self.ftp.print_current_directory()
        self.current_directory_label.set(directory)

    def go_to_parent_dir(self):
        last_index = self.current_directory.rfind("/")
        new_dir = self.current_directory[:last_index]
        self.change_directory(new_dir=new_dir)

    def change_directory(self, event=None, new_dir=None):
        if new_dir is None:
            # 01234
            # _>_dir
            selected_dir = self.get_selected_listbox_item()
            if selected_dir == -1:
                return -1
            # If it is a file, return -1
            if selected_dir[1] == '-':
                return -1
            selected_dir_path = selected_dir[3:]
            self.current_directory = self.current_directory + '/' + selected_dir_path
        else:
            self.current_directory = new_dir

        self.ftp.change_current_directory(self.current_directory)
        self.update_list()

    def status_and_download_ui(self):
        status_download_frame = Frame(self.main_frame, padx=5)

        status_frame = LabelFrame(status_download_frame, text="Status")
        status_label = \
            Label(status_frame, textvariable=self.status, anchor=W, width=45)

        # Save as file
        download_button = Button(status_download_frame, text="Download", command=self.download)

        status_download_frame.pack(side=TOP, pady=(0, 5), padx=0, expand=1, fill=X)
        status_frame.pack(side=LEFT)
        status_label.pack()
        download_button.pack(side=RIGHT, pady=(8, 0), padx=5)

    def get_selected_listbox_item(self):
        selected_dir = (self.file_explorer_listbox.curselection())
        if len(selected_dir) < 1:
            return -1
        selected_dir = self.file_explorer_listbox.get(selected_dir[0])
        return selected_dir

    def download(self):

        selected_dir = self.get_selected_listbox_item()
        if selected_dir == -1:
            return -1
        # If it is a folder, return -1
        if selected_dir[1] == '>':
            return -1

        download_file_name = selected_dir[3:]
        downloaded_data = self.ftp.download_file(download_file_name)
        # Download failed
        if downloaded_data == -1:
            return -1
        downloaded_file = asksaveasfile(title="Save file as...", mode="wb",
                                        initialfile=download_file_name, filetype=[('All Files', '*.*')])
        downloaded_file.write(downloaded_data)
        if downloaded_file:
            downloaded_file.close()

    def rename_ui(self):
        rename_frame = LabelFrame(self.main_frame, text="Rename to", padx=5, pady=2)
        rename_input = Entry(rename_frame, textvariable=self.rename_to, width=50)
        rename_button = Button(rename_frame, text="Confirm", command=self.rename)

        rename_frame.pack(side=TOP, padx=5, pady=2, expand=1, fill=X)
        rename_input.pack(side=LEFT, padx=5)
        rename_button.pack(side=RIGHT)

    def rename(self):
        selected_dir = self.get_selected_listbox_item()
        if selected_dir == -1 or len(self.rename_to.get()) == 0:
            return -1
        # If it is a folder, return -1
        if selected_dir[1] == '>':
            return -1
        old_file_name = selected_dir[3:]
        new_file_name = self.rename_to.get()

        self.ftp.rename_file(old_file_name, new_file_name)
        self.update_list()

    def upload_ui(self):
        upload_frame = LabelFrame(self.main_frame, text="Upload", padx=5, pady=2)
        upload_label = Label(upload_frame, text="File:")
        upload_input = Entry(upload_frame, width=40, textvariable=self.upload_file_path)
        upload_browse_button = Button(upload_frame, text="Browse", command=self.browse_upload_file)
        upload_button = Button(upload_frame, text="Upload", command=self.upload)

        upload_frame.pack(side=TOP, padx=5, pady=2, expand=1, fill=X)
        upload_label.pack(side=LEFT)
        upload_input.pack(side=LEFT, padx=5)
        upload_browse_button.pack(side=LEFT, padx=5)
        upload_button.pack(side=LEFT)

    def browse_upload_file(self):
        file_path = askopenfilename()
        if len(file_path) > 0:
            self.upload_file_path.set(file_path)

    def upload(self):
        path = self.upload_file_path.get()
        if len(path) <= 0:
            return -1
        if self.ftp.upload_file(path) == -1:
            return -1
        self.update_list()

    def folder_ui(self):
        folder_frame = LabelFrame(self.main_frame, text="Folder", padx=5, pady=2)
        folder_label = Label(folder_frame, text="Name:")
        folder_input = Entry(folder_frame, width=40, textvariable=self.new_folder_name)
        create_folder_button = Button(folder_frame, text="Make", command=self.create_folder)
        delete_folder_button = Button(folder_frame, text="Delete", command=self.delete_folder)

        folder_frame.pack(side=TOP, padx=5, pady=2, expand=1, fill=X)
        folder_label.pack(side=LEFT)
        folder_input.pack(side=LEFT, padx=5)
        create_folder_button.pack(side=LEFT, padx=5)
        delete_folder_button.pack(side=LEFT)

    def create_folder(self):
        folder_name = self.new_folder_name.get()
        if len(folder_name) == 0:
            return -1
        self.ftp.create_folder(folder_name)
        self.update_list()

    def delete_folder(self):
        selected_dir = self.get_selected_listbox_item()
        if selected_dir == -1:
            return -1
        # If it is a file, return -1
        if selected_dir[1] == '-':
            return -1
        folder_name = selected_dir[3:]

        self.ftp.delete_folder(folder_name)
        self.update_list()

    def others_ui(self):
        others_frame = LabelFrame(self.main_frame, text="Others", padx=5)
        delete_button = Button(others_frame, text="Delete File", width=15, command=self.delete_file)

        others_frame.pack(side=TOP, padx=5, pady=2, expand=1, fill=X)
        delete_button.pack(side=TOP, pady=5)

    def delete_file(self):
        selected_dir = self.get_selected_listbox_item()
        if selected_dir == -1:
            return -1
        # If it is a folder, return -1
        if selected_dir[1] == '>':
            return -1
        file_name = selected_dir[3:]

        self.ftp.delete_file(file_name)
        self.update_list()

    def connection_mode_ui(self):
        mode_frame = Frame(self.main_frame, pady=5)
        mode_label = Label(mode_frame, text="Connection Mode")
        port_button = \
            Radiobutton(mode_frame, text="PORT", value="PORT",
                        variable=self.data_connection_mode, indicator=0, command=self.update_connection_mode)
        pasv_button = \
            Radiobutton(mode_frame, text="PASV", value="PASV",
                        variable=self.data_connection_mode, indicator=0, command=self.update_connection_mode)

        mode_frame.pack(side=TOP, padx=5, pady=2, expand=1, fill=X)
        mode_label.pack(side=TOP)
        port_button.pack(side=LEFT, expand=1, fill=X)
        pasv_button.pack(side=LEFT, expand=1, fill=X)

    def update_connection_mode(self):
        if self.data_connection_mode.get() == "PASV":
            self.ftp.set_pasv(True)
            print("Connection Mode: PASV")
        else:
            self.ftp.set_pasv(False)
            print("Connection Mode: PORT")
