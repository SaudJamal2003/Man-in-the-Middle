import socket
import threading
from tkinter import Tk, Text, Entry, Label, Button, END
from tkinter import ttk

HOST = '127.0.0.1'
MITM_PORT = 9875
SERVER_PORT = 9876


class MITMAttackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MITM Attacker")
        self.root.geometry("600x500")
        self.setup_theme()

        # Title label
        title_label = ttk.Label(self.root, text="MITM Attacker Application", font=("Helvetica", 14, "bold"))
        title_label.pack(pady=10)

        # Log box for displaying intercepted and modified data
        self.log_box = Text(self.root, height=15, width=70, bg="#2b2b2b", fg="#ffffff", wrap="word", insertbackground="#ffffff")
        self.log_box.pack(pady=(5, 10), padx=10)

        # Entry for modifying intercepted message
        self.modify_label = ttk.Label(self.root, text="Modify intercepted message:")
        self.modify_label.pack(pady=(10, 0))

        self.modify_entry = Entry(self.root, width=70, bg="#2b2b2b", fg="#ffffff", insertbackground="#ffffff")
        self.modify_entry.pack(pady=(5, 10))

        # Bind the Enter key to send the message
        self.modify_entry.bind("<Return>", lambda event: self.send_modified_message())

        # Button to confirm message modification
        self.modify_button = Button(self.root, text="Send Modified Message", command=self.send_modified_message, bg="#3c3f41", fg="#ffffff", activebackground="#505354", activeforeground="#ffffff")
        self.modify_button.pack(pady=(5, 10))

        # Shared variables to manage message state
        self.current_message = None
        self.current_signature = None
        self.client_conn = None
        self.server_socket = None

        # Start the attacker in a separate thread
        threading.Thread(target=self.run_attacker, daemon=True).start()

    def setup_theme(self):
        self.root.configure(bg="#1e1e1e")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Helvetica", 10))
        style.configure("TButton", background="#3c3f41", foreground="#ffffff", font=("Helvetica", 10))
        style.map("TButton", background=[("active", "#505354")])

    def log_message(self, message):
        """Log messages in the log box."""
        self.log_box.insert(END, message + "\n")
        self.log_box.see(END)

    def send_modified_message(self):
        """Send the modified message from the GUI to the server."""
        if not self.current_message or not self.current_signature:
            self.log_message("No intercepted message to modify.")
            return

        # Get the modified message from the user
        modified_message = self.modify_entry.get().encode()
        if not modified_message:
            self.log_message("Modified message cannot be empty.")
            return

        # Reassemble the data
        modified_data = modified_message + b'||' + self.current_signature
        self.log_message(f"Modified message sent: {modified_message.decode(errors='ignore')}")

        try:
            # Forward modified data to the server
            self.server_socket.sendall(modified_data)
            self.log_message("Forwarded modified data to the server.")

            # Receive the server's response
            #response = self.server_socket.recv(4096)
            #self.log_message(f"Received server response: {response.decode(errors='ignore')}")

            # Relay the server's response back to the client
            self.client_conn.sendall(b"ACK")  # Force ACK for the client
           # self.log_message("Relayed ACK response to the client.")
        except Exception as e:
            self.log_message(f"Error sending modified message: {e}")

    def run_attacker(self):
        try:
            # Connect to the server
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((HOST, SERVER_PORT))
            self.log_message("Connected to server at 127.0.0.1:9876")

            # Set up listener for the client
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, MITM_PORT))
                s.listen()
                self.log_message(f"Listening for client on port {MITM_PORT}...")
                self.client_conn, addr = s.accept()
                self.log_message(f"Client connected: {addr}")
                with self.client_conn:
                    while True:
                        try:
                            # Intercept data from the client
                            data = self.client_conn.recv(4096)
                            if not data:
                                self.log_message("Client disconnected.")
                                break

                            # Log the raw intercepted data for testing purpose
                            #self.log_message(f"Raw data intercepted: {data}")

                            # Split the data into message and signature
                            if b'||' in data:
                                parts = data.split(b'||', 1)
                                self.current_message = parts[0]
                                self.current_signature = parts[1]
                                self.log_message(f"Original message: {self.current_message.decode(errors='ignore')}")

                                # Populate the modify entry field with the intercepted message
                                self.modify_entry.delete(0, END)
                                self.modify_entry.insert(0, self.current_message.decode(errors='ignore'))
                        except Exception as e:
                            self.log_message(f"Error during attack: {e}")
                            break
        except Exception as e:
            self.log_message(f"Error setting up MITM Attacker: {e}")


def run_mitm_attacker():
    """Run the MITM attacker application."""
    root = Tk()
    app = MITMAttackerApp(root)
    root.mainloop()


if __name__ == '__main__':
    run_mitm_attacker()
