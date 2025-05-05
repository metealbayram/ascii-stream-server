import socket
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont

# Client configuration
HOST = '127.0.0.1'
PORT = 65432

class ASCIITelevisionClient:
    def __init__(self, root):
        self.root = root
        self.root.title("ASCII Television")
        
        # Get screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Set initial window size to 80% of screen
        self.width = int(screen_width * 0.8)
        self.height = int(screen_height * 0.8)
        self.root.geometry(f"{self.width}x{self.height}")
        
        # TV state variables
        self.is_powered_on = False
        self.client_socket = None
        self.connected = False
        self.stream_thread = None
        self.current_channel = 0
        self.muted = False
        self.volume = 50  # 0-100
        self.fullscreen = False
        self.show_info = False
        self.info_timer = None
        
       
        self.create_icons()
        self.setup_ui()
        self.bind_keys()
        
    def create_icons(self):
        # Create TV power icon
        power_img = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
        draw = ImageDraw.Draw(power_img)
        draw.ellipse((0, 0, 40, 40), outline="white", width=2)
        draw.line((20, 10, 20, 20), fill="white", width=2)
        self.power_icon = ImageTk.PhotoImage(power_img)
        
        # Create volume icons
        vol_img = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
        draw = ImageDraw.Draw(vol_img)
        # Draw speaker outline
        draw.polygon([(10, 15), (20, 15), (30, 5), (30, 35), (20, 25), (10, 25)], outline="white", width=2)
        # Draw sound waves
        draw.arc((32, 12, 38, 28), start=270, end=90, fill="white", width=2)
        self.volume_icon = ImageTk.PhotoImage(vol_img)
        
        
        mute_img = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
        draw = ImageDraw.Draw(mute_img)
        
        draw.polygon([(10, 15), (20, 15), (30, 5), (30, 35), (20, 25), (10, 25)], outline="white", width=2)
       
        draw.line((32, 12, 38, 28), fill="white", width=2)
        draw.line((32, 28, 38, 12), fill="white", width=2)
        self.mute_icon = ImageTk.PhotoImage(mute_img)
        
        
        self.channel_icons = []
        channel_colors = ["#FF4136", "#2ECC40", "#0074D9"]
        for i in range(3):
            ch_img = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
            draw = ImageDraw.Draw(ch_img)
            draw.ellipse((5, 5, 55, 55), fill=channel_colors[i])
          
            try:
                font = ImageFont.truetype("arial.ttf", 30)
            except:
                font = ImageFont.load_default()
            draw.text((30, 30), str(i+1), fill="white", font=font, anchor="mm")
            self.channel_icons.append(ImageTk.PhotoImage(ch_img))
    
    def setup_ui(self):
        
        self.root.configure(bg="black")
        self.tv_frame = tk.Frame(self.root, bg="black", bd=20, relief=tk.RAISED)
        self.tv_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.screen_frame = tk.Frame(self.tv_frame, bg="black", bd=2, relief=tk.SUNKEN)
        self.screen_frame.pack(fill=tk.BOTH, expand=True)
        
        self.screen = scrolledtext.ScrolledText(
            self.screen_frame, 
            wrap=tk.WORD, 
            font=("Courier New", 12),
            bg="black", 
            fg="#33FF33",  # Green color for ASCII
            insertbackground="#33FF33",
            highlightthickness=0,
            bd=0
        )
        self.screen.pack(fill=tk.BOTH, expand=True)
        self.screen.insert(tk.END, "TV is powered off. Press the power button to turn on.")
        self.screen.config(state=tk.DISABLED)
        
        self.control_panel = tk.Frame(self.root, bg="#333333", height=60)
        self.control_panel.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.power_btn = tk.Button(
            self.control_panel, 
            image=self.power_icon,
            bg="#333333", 
            activebackground="#444444",
            bd=0,
            command=self.toggle_power
        )
        self.power_btn.pack(side=tk.LEFT, padx=10)
        
        self.ch_frame = tk.Frame(self.control_panel, bg="#333333")
        self.ch_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(self.ch_frame, text="CHANNELS", fg="white", bg="#333333").pack()
        
        ch_buttons_frame = tk.Frame(self.ch_frame, bg="#333333")
        ch_buttons_frame.pack()
        
        for i in range(3):
            ch_btn = tk.Button(
                ch_buttons_frame,
                image=self.channel_icons[i],
                bg="#333333",
                activebackground="#444444",
                bd=0,
                command=lambda ch=i: self.change_channel(ch)
            )
            ch_btn.grid(row=0, column=i, padx=5)
        
        self.vol_frame = tk.Frame(self.control_panel, bg="#333333")
        self.vol_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(self.vol_frame, text="VOLUME", fg="white", bg="#333333").pack()
        
        vol_control_frame = tk.Frame(self.vol_frame, bg="#333333")
        vol_control_frame.pack()
        
        self.vol_icon_label = tk.Label(
            vol_control_frame, 
            image=self.volume_icon, 
            bg="#333333"
        )
        self.vol_icon_label.grid(row=0, column=0, padx=5)
        
        self.volume_scale = ttk.Scale(
            vol_control_frame, 
            from_=0, 
            to=100, 
            orient=tk.HORIZONTAL, 
            value=self.volume,
            length=100,
            command=self.set_volume
        )
        self.volume_scale.grid(row=0, column=1, padx=5)
        
        self.fullscreen_btn = tk.Button(
            self.control_panel,
            text="[ ]",
            font=("Arial", 12, "bold"),
            bg="#333333",
            fg="white",
            activebackground="#444444",
            bd=0,
            command=self.toggle_fullscreen
        )
        self.fullscreen_btn.pack(side=tk.RIGHT, padx=10)
        
        self.info_overlay = tk.Frame(
            self.screen_frame, 
            bg="#333333", 
            bd=1, 
            relief=tk.RAISED
        )
        
        self.channel_info = tk.Label(
            self.info_overlay, 
            text="Channel 1", 
            font=("Arial", 12), 
            bg="#333333", 
            fg="white"
        )
        self.channel_info.pack(padx=10, pady=5)
        
        
        self.status_var = tk.StringVar()
        self.status_var.set("Powered Off")
        self.status_bar = tk.Label(
            self.root, 
            textvariable=self.status_var, 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            bg="#222222",
            fg="#AAAAAA"
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def bind_keys(self):
        self.root.bind("p", lambda event: self.toggle_power())
        self.root.bind("1", lambda event: self.change_channel(0))
        self.root.bind("2", lambda event: self.change_channel(1))
        self.root.bind("3", lambda event: self.change_channel(2))
        self.root.bind("<Up>", lambda event: self.adjust_volume(10))
        self.root.bind("<Down>", lambda event: self.adjust_volume(-10))
        self.root.bind("m", lambda event: self.toggle_mute())
        self.root.bind("f", lambda event: self.toggle_fullscreen())
        self.root.bind("i", lambda event: self.show_channel_info())
        self.root.bind("<Escape>", lambda event: self.exit_fullscreen())
    
    def toggle_power(self):
        if self.is_powered_on:
            self.power_off()
        else:
            self.power_on()
    
    def power_on(self):
        self.screen.config(state=tk.NORMAL)
        self.screen.delete(1.0, tk.END)
        self.screen.insert(tk.END, "Powering on...\n\nInitializing television...\n")
        self.screen.config(state=tk.DISABLED)
        self.status_var.set("Starting up...")
        self.is_powered_on = True
        self.root.after(1000, self.connect_to_channel)
    
    def power_off(self):
        if self.connected:
            self.disconnect_from_server()
        
        self.screen.config(state=tk.NORMAL)
        self.screen.delete(1.0, tk.END)
        self.screen.insert(tk.END, "TV is powered off. Press the power button to turn on.")
        self.screen.config(state=tk.DISABLED)
        
        self.status_var.set("Powered Off")
        self.is_powered_on = False
    
    def connect_to_channel(self):
        if not self.is_powered_on:
            return
            
        if self.connected:
            self.disconnect_from_server()
        
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))
            self.connected = True
            self.status_var.set(f"Connected to server on {HOST}:{PORT}")
            self.client_socket.sendall(str(self.current_channel).encode('utf-8'))
            self.show_channel_info()
            self.stream_thread = threading.Thread(target=self.receive_frames)
            self.stream_thread.daemon = True
            self.stream_thread.start()
            
        except Exception as e:
            self.screen.config(state=tk.NORMAL)
            self.screen.delete(1.0, tk.END)
            self.screen.insert(tk.END, f"No signal!\n\nCould not connect to server: {e}\n\nPlease check your connection.")
            self.screen.config(state=tk.DISABLED)
            self.status_var.set(f"Connection error: {e}")
    
    def disconnect_from_server(self):
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        self.connected = False
    def receive_frames(self):
        try:
            self.screen.config(state=tk.NORMAL)
            self.screen.delete(1.0, tk.END)
            self.screen.config(state=tk.DISABLED)
            buffer = ""
            while self.connected and self.is_powered_on:
                frame = self.client_socket.recv(1024)
                if not frame:
                    break
                buffer += frame.decode('utf-8')
                
                self.screen.config(state=tk.NORMAL)
                self.screen.delete(1.0, tk.END)
                self.screen.insert(tk.END, buffer)
                
                lines = buffer.split('\n')
                if len(lines) > 50:
                    buffer = '\n'.join(lines[-50:])
                
                self.screen.see(tk.END)
                self.screen.config(state=tk.DISABLED)
        
        except Exception as e:
            if self.connected and self.is_powered_on:  
                self.screen.config(state=tk.NORMAL)
                self.screen.insert(tk.END, f"\n\nSignal lost: {e}\n")
                self.screen.config(state=tk.DISABLED)
                self.status_var.set(f"Connection lost: {e}")
                self.connected = False
    
    def change_channel(self, channel_number):
        if not self.is_powered_on:
            return
            
        if channel_number == self.current_channel and self.connected:
            # Already on this channel
            self.show_channel_info()
            return
            
        self.current_channel = channel_number
        
        
        self.screen.config(state=tk.NORMAL)
        self.screen.delete(1.0, tk.END)
        self.screen.insert(tk.END, f"Changing to channel {channel_number + 1}...\n\nPlease wait...")
        self.screen.config(state=tk.DISABLED)
        
       
        self.connect_to_channel()
    
    def set_volume(self, value):
        self.volume = int(float(value))
        if self.muted and self.volume > 0:
            self.toggle_mute()  
        self.show_volume_info()
    
    def adjust_volume(self, amount):
        if not self.is_powered_on:
            return
            
        new_volume = self.volume + amount
        new_volume = max(0, min(100, new_volume)) 
        self.volume_scale.set(new_volume)
        self.volume = new_volume
        
        if self.muted and self.volume > 0:
            self.toggle_mute()  
            
        self.show_volume_info()
    
    def toggle_mute(self):
        if not self.is_powered_on:
            return
            
        self.muted = not self.muted
        if self.muted:
            self.vol_icon_label.config(image=self.mute_icon)
        else:
            self.vol_icon_label.config(image=self.volume_icon)
        
        self.show_volume_info()
    
    def show_volume_info(self):
        if not self.is_powered_on:
            return
            
       
        volume_overlay = tk.Toplevel(self.root)
        volume_overlay.overrideredirect(True) 
        volume_overlay.attributes('-topmost', True)
        
        
        x = self.root.winfo_x() + self.root.winfo_width() - 150
        y = self.root.winfo_y() + self.root.winfo_height() - 100
        volume_overlay.geometry(f"120x60+{x}+{y}")
        
       
        frame = tk.Frame(volume_overlay, bg="#333333", bd=1, relief=tk.RAISED)
        frame.pack(fill=tk.BOTH, expand=True)
        
        if self.muted:
            icon_label = tk.Label(frame, image=self.mute_icon, bg="#333333")
            vol_text = "MUTED"
        else:
            icon_label = tk.Label(frame, image=self.volume_icon, bg="#333333")
            vol_text = f"{self.volume}%"
        
        icon_label.pack(pady=2)
        
        vol_label = tk.Label(frame, text=vol_text, font=("Arial", 10), bg="#333333", fg="white")
        vol_label.pack(pady=2)
        
       
        self.root.after(2000, volume_overlay.destroy)
    
    def show_channel_info(self):
        if not self.is_powered_on:
            return
            
        if self.info_timer:
            self.root.after_cancel(self.info_timer)
            
       
        self.info_overlay.place(relx=0.02, rely=0.02, anchor=tk.NW)
        
       
        self.channel_info.config(text=f"Channel {self.current_channel + 1}")
        
     
        self.info_timer = self.root.after(3000, self.hide_info)
        
        self.show_info = True
    
    def hide_info(self):
        self.info_overlay.place_forget()
        self.show_info = False
        self.info_timer = None
    
    def toggle_fullscreen(self):
        if not self.fullscreen:
            self.original_geometry = self.root.geometry()
            self.root.geometry("") 
            self.root.attributes("-fullscreen", True)
            self.fullscreen_btn.config(text="▢")
            self.fullscreen = True
        else:
            self.exit_fullscreen()
    
    def exit_fullscreen(self):
        if self.fullscreen:
            self.root.attributes("-fullscreen", False)
            self.root.geometry(self.original_geometry)
            self.fullscreen_btn.config(text="[ ]")
            self.fullscreen = False

def main():
    root = tk.Tk()
    app = ASCIITelevisionClient(root)
    root.protocol("WM_DELETE_WINDOW", lambda: quit_app(root, app))
    root.mainloop()

def quit_app(root, app):
    if app.connected:
        app.disconnect_from_server()
    root.destroy()

if __name__ == "__main__":
    try:
        from PIL import Image, ImageTk, ImageDraw, ImageFont
    except ImportError:
        print("This program requires the Pillow library.")
        print("Please install it using: pip install pillow")
        print("Then run the program again.")
        exit(1)
        
    main()
