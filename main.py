import tkinter as tk
from angryftp.ftp_client_application import AngryFtpClientApplication

# Creating tkinter window
if __name__ == '__main__':
    window = tk.Tk()
    window.resizable(False, False)
    AngryFtpClientApplication(window)
    window.mainloop()
