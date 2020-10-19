import tkinter as tk
from angryftp.ftp_client_application import AngryFtpClientApplication

# Creating tkinter window
if __name__ == '__main__':
    window = tk.Tk()
    window.iconbitmap("D:/Hengsoo/Desktop/ftp-client/angryftp/angry.ico")
    window.resizable(False, False)
    AngryFtpClientApplication(window)
    window.mainloop()
