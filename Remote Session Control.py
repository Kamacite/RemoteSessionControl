# Remote session viewer/contoller for terminal servers
# Rob D'Andrea
# 2/27/2019
# Windows only

import subprocess
import tkinter as tk

class Application(tk.Frame):
    
    user = ""
    computer = ""

    
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        self.pack()

        self.create_widgets()

        self.poll_sessions()

    # Fill Application Window
    def create_widgets(self):
        # Organizes the labels, entry fields, and buttons to the top
        self.panel = tk.PanedWindow()
        self.panel.pack(fill=tk.BOTH, expand=1)  

        self.computer_label = tk.Label(self.master, text="Server(blank=local): ")
        self.panel.add(self.computer_label)

        self.computer_entry = tk.Entry(self.master)
        self.panel.add(self.computer_entry)

        self.username_label = tk.Label(self.master, text = "Username: ")
        self.panel.add(self.username_label)

        self.username_entry = tk.Entry(self.master)
        self.panel.add(self.username_entry)

        self.session_button = tk.Button(self.master, text="Find Sessions", command=self.get_sessions)
        self.panel.add(self.session_button)

        self.connect_button = tk.Button(self.master, text="Control", command=self.control_session, state=tk.DISABLED)
        self.panel.add(self.connect_button)
        # Displays active sessions after Find Sessions is pressed
        self.sessions_listbox = tk.Listbox(self.master, width=100)
        self.sessions_listbox.pack()

    # Find all sessions of a specified user on a specified machine
    def quser(self, username = "", computername = 0):
        if computername != 0 and username != "":
            #Both computer and user specified
            output = subprocess.run("quser" + " " + username + " " + "/server:" + computername,
                    shell=True,
                    check=False,
                    capture_output=True)
        elif username != "" and computername == 0:
            # User specified but not computer
            output = subprocess.run("quser" + " " + username,
                    shell=True,
                    check=False,
                    capture_output=True)  
        elif username == "" and computername != 0:
            # Computer specified but not user
            output = subprocess.run("quser" + " " + "/server:" + computername,
                    shell=True,
                    check=False,
                    capture_output=True)
        else:
            # No user or server specified
            output = subprocess.run("quser",
                    shell=True,
                    check=False,
                    capture_output=True)

        return output.stdout.decode('UTF-8')

    def get_sessions(self):
        # Clear out previous searches
        old_sessions = self.sessions_listbox.size()
        self.sessions_listbox.delete(0,old_sessions-1)
        # Grab data in entry fields 
        computer = self.computer_entry.get()
        user = self.username_entry.get()
        # Get session info and returned as UTF-8
        output = self.quser(user, computer).splitlines()
        if len(output) > 1:
            i = 0
            if computer == "":
                computer = "local"
        
            for line in output:
                #print(line)
                line = line.split()
                if line[2] != 'Disc' and i != 0: # Skip first line containing headers
                    self.sessions_listbox.insert(i, line[0] + " " + line[1] + " " + line[2] + " || " + computer)
                i += 1
        else:
            self.sessions_listbox.insert(0, "No sessions found. Check spelling of computername and/or username")

    def control_session(self):
        # Get ID from active listbox
        index = self.sessions_listbox.curselection()
        sess_info = self.sessions_listbox.get(index).split()
        sess_id = sess_info[2]
        # Get computer from active listbox
        sess_serv = sess_info[4]
        if sess_serv == "local":
            # Case computer is local
            subprocess.run("mstsc.exe /shadow:"+ sess_id + " /control", check= False, capture_output=False)
        else:
            # Case computer is specified
            subprocess.run("mstsc.exe /shadow:"+ sess_id + " /v:" + sess_serv + " /control", check= False, capture_output=False)

    # Check if a session is active
    def poll_sessions(self):
        index = self.sessions_listbox.curselection()
        first_line = self.sessions_listbox.get(0)
        if index and first_line != "No sessions found. Check spelling of computername and/or username" :
            self.connect_button.configure(state = tk.NORMAL)
        else:
            self.connect_button.configure(state = tk.DISABLED)
        self.after(250, self.poll_sessions)


root= tk.Tk()
root.title("Remote Session Control")
app = Application(root)

root.mainloop()