import socket
import threading
from tkinter import Tk, Text, Label, END
from tkinter import ttk

HOST = '127.0.0.1'
MITM_PORT = 9875
SERVER_PORT = 9876


class MITMForwarderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MITM Forwarder")
        self.root.geometry("600x400")
        self.setup_theme()

        # Add a title label
        title_label = ttk.Label(self.root, text="MITM Forwarder Application", font=("Helvetica", 14, "bold"))
        title_label.pack(pady=10)

        # Log box for displaying intercepted and forwarded data
        self.log_box = Text(self.root, height=20, width=70, bg="#2b2b2b", fg="#ffffff", wrap="word", insertbackground="#ffffff")
        self.log_box.pack(pady=(5, 10), padx=10)

        # Start the forwarder in a separate thread
        threading.Thread(target=self.run_forwarder, daemon=True).start()

    def setup_theme(self):
        """Set up the dark theme for the GUI."""
        self.root.configure(bg="#1e1e1e")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Helvetica", 10))
        style.configure("TButton", background="#3c3f41", foreground="#ffffff", font=("Helvetica", 10))
        style.map("TButton", background=[("active", "#505354")])

    def log_message(self, message):
        """Log a message to the log box."""
        self.log_box.insert(END, message + "\n")
        self.log_box.see(END)

    def run_forwarder(self):
        """Run the MITM forwarder to intercept and relay data between client and server."""
        try:
            # Connect to the server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((HOST, SERVER_PORT))
            self.log_message("Connected to server at 127.0.0.1:9876")

            # Set up listener for the client
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, MITM_PORT))
                s.listen()
                self.log_message(f"Listening for client on port {MITM_PORT}...")
                conn, addr = s.accept()
                self.log_message(f"MITM Forwarder connected by {addr}")
                with conn:
                    while True:
                        try:
                            # Intercept data from client
                            data = conn.recv(4096)
                            if not data:
                                self.log_message("Client disconnected.")
                                break

                            # Split intercepted data into message and signature
                            if b'||' in data:
                                parts = data.split(b'||', 1)
                                message = parts[0]
                                signature = parts[1]

                                # Log the intercepted message and signature
                                self.log_message(f"Intercepted message: {message.decode(errors='ignore')}")
                                #self.log_message(f"Intercepted signature (hex): {signature.hex()}")

                            # Forward data to the server
                            server_socket.sendall(data)
                            self.log_message("Forwarded data to server.")

                            # Receive response from the server
                            response = server_socket.recv(4096)
                            self.log_message(f"Received response: {response.decode(errors='ignore')}")
                            conn.sendall(response)
                        except Exception as e:
                            self.log_message(f"Error during forwarding: {e}")
                            break
        except Exception as e:
            self.log_message(f"Error setting up MITM Forwarder: {e}")


def run_mitm_forwarder():
    """Run the MITM forwarder application."""
    root = Tk()
    app = MITMForwarderApp(root)
    root.mainloop()


if __name__ == '__main__':
    run_mitm_forwarder()
