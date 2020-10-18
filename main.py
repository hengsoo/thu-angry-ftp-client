import tkinter as tk
from angryftp.ftp_client_application import FtpClientApplication

# Creating tkinter window
if __name__ == '__main__':
    window = tk.Tk()
    # window.geometry('550x150')
    ftp_client = FtpClientApplication(window)
    window.mainloop()
