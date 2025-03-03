import socket
from tkinter import Tk, Text, Label, END
from tkinter import ttk
from common_functions import generate_digital_signature

HOST = '127.0.0.1'
PORT = 9875

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dark Theme Client")
        self.root.geometry("600x400")
        self.setup_theme()

        # Add a title label at the top
        title_label = ttk.Label(self.root, text="Client Application", font=("Helvetica", 14, "bold"))
        title_label.pack(pady=10)

        # Input field for message
        self.message_label = ttk.Label(self.root, text="Enter message:")
        self.message_label.pack(pady=(5, 0))
        self.message_entry = ttk.Entry(self.root, width=70)
        self.message_entry.pack(pady=(5, 10))

        # Bind the Enter key to the send_message method
        self.message_entry.bind("<Return>", lambda event: self.send_message())

        # Log box for server responses
        self.log_label = ttk.Label(self.root, text="Server Responses:")
        self.log_label.pack(pady=(10, 0))

        self.log_box = Text(self.root, height=15, width=70, bg="#2b2b2b", fg="#ffffff", wrap="word", insertbackground="#ffffff")
        self.log_box.pack(pady=(5, 10), padx=10)

        # Establish connection
        self.socket = None
        self.connect_to_server()

    def setup_theme(self):
        self.root.configure(bg="#1e1e1e")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Helvetica", 10))
        style.configure("TButton", background="#3c3f41", foreground="#ffffff", font=("Helvetica", 10))
        style.map("TButton", background=[("active", "#505354")])

    def connect_to_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((HOST, PORT))
            self.log_message("Connected to the server.")
        except Exception as e:
            self.log_message(f"Connection error: {e}")

    def send_message(self):
        message = self.message_entry.get()
        if not message:
            self.log_message("Message cannot be empty.")
            return
        if message.lower() == 'exit':
            self.log_message("Exiting client...")
            self.root.quit()
            return

        try:
            with open("private.pem", "rb") as priv_file:
                rsa_priv = priv_file.read()
            signature = generate_digital_signature(message, rsa_priv)
            self.socket.sendall(message.encode() + b"||" + signature)
            response = self.socket.recv(1024)
            self.log_message(f"Server response: {response.decode()}")
            # Clear the message entry field after sending
            self.message_entry.delete(0, END)
        except Exception as e:
            self.log_message(f"Error sending message: {e}")

    def log_message(self, message):
        self.log_box.insert(END, message + "\n")
        self.log_box.see(END)

def run_client():
    root = Tk()
    app = ClientApp(root)
    root.mainloop()

if __name__ == '__main__':
    run_client()
