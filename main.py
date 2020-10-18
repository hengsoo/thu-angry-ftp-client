import tkinter as tk
from angryftp.ftp_client_application import FtpClientApplication

# Creating tkinter window
if __name__ == '__main__':
    window = tk.Tk()
    window.resizable(False, False)
    ftp_client = FtpClientApplication(window)
    window.mainloop()
