import socket
import threading
from tkinter import Tk, Text, Label, END
from tkinter import ttk
from common_functions import verify_digital_signature

HOST = '127.0.0.1'
PORT = 9876

class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Server")
        self.root.geometry("600x400")
        self.setup_theme()

        # Dark-themed widgets
        self.log_box = Text(root, height=20, width=70, bg="#2b2b2b", fg="#ffffff", insertbackground="#ffffff", wrap="word")
        self.log_box.pack(pady=10, padx=10)

        threading.Thread(target=self.run_server, daemon=True).start()

    def setup_theme(self):
        # Apply a dark theme to the root window
        self.root.configure(bg="#1e1e1e")
        style = ttk.Style()
        style.theme_use("clam")  # Use a modern style
        style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Helvetica", 10))
        style.configure("TButton", background="#3c3f41", foreground="#ffffff", font=("Helvetica", 10))
        style.map("TButton", background=[("active", "#505354")])

        # Add a title label
        title_label = ttk.Label(self.root, text="Server Application", font=("Helvetica", 14, "bold"))
        title_label.pack(pady=10)

    def log_message(self, message):
        self.log_box.insert(END, message + "\n")
        self.log_box.see(END)

    def run_server(self):
        try:
            with open("public.pem", "rb") as pub_file:
                rsa_pub = pub_file.read()
        except FileNotFoundError:
            self.log_message("Error: Public key file not found.")
            return

        self.log_message("Server running...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            while True:
                conn, addr = s.accept()
                self.log_message(f"Connected by {addr}")
                threading.Thread(target=self.handle_client, args=(conn, addr, rsa_pub), daemon=True).start()

    def handle_client(self, conn, addr, rsa_pub):
        with conn:
            while True:
                try:
                    data = conn.recv(4096)
                    if not data:
                        break
                    message, signature = data.split(b'||')
                    self.log_message(f"Message from {addr}: {message.decode()}")
                    if verify_digital_signature(message.decode(), signature, rsa_pub):
                        self.log_message("Message verified.")
                        conn.sendall(b"ACK")
                    else:
                        self.log_message("Message verification failed.")
                        conn.sendall(b"VERIFICATION FAILED")
                except Exception as e:
                    self.log_message(f"Error handling client {addr}: {e}")
                    conn.sendall(b"ERROR")
                    break

def run_server():
    root = Tk()
    app = ServerApp(root)
    root.mainloop()

if __name__ == '__main__':
    run_server()
