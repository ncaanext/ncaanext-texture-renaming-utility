import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, PhotoImage
import customtkinter as ctk
from customtkinter import CTkImage
import threading
import configparser
import webbrowser
import os
import subprocess
import platform
from utils.csvrename import run_function
from utils.dumpsfinder import DumpsFinder
from PIL import Image, ImageTk, ImageFont

CONFIG_FILE = 'config.txt'

import tkinter as tk

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None

        # Bind events to show/hide the tooltip
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tooltip is None:
            # Create the tooltip
            self.tooltip = tk.Toplevel(self.widget)
            self.tooltip.wm_overrideredirect(True)

            # Create the label with the tooltip text
            label = tk.Label(self.tooltip, text=self.text, background="#000000", fg="white", borderwidth=1, relief="solid", padx=5, pady=10)
            label.pack()

            # Update the window to calculate the label's width
            self.tooltip.update_idletasks()

            # Get the width of the tooltip content
            tooltip_width = label.winfo_width()
            tooltip_height = label.winfo_height()

            # Calculate position
            x = event.x_root
            y = event.y_root

            # --- OFFSET ADJUSTMENT ---
            x_offset = 10      # move right from cursor
            y_offset = 20      # move down from cursor
            x += x_offset
            y += y_offset

            # Ensure the tooltip is within the screen bounds
            screen_width = self.widget.winfo_screenwidth()
            screen_height = self.widget.winfo_screenheight()
            if x < 0:
                x = 0
            if y + tooltip_height > screen_height:
                y = screen_height - tooltip_height

            # Set the geometry for the tooltip
            self.tooltip.wm_geometry(f"{tooltip_width}x{tooltip_height}+{x}+{y}")

    def hide_tooltip(self, event):
        if self.tooltip is not None:
            self.tooltip.destroy()
            self.tooltip = None

def open_folder(folder_name):
    folder_path = os.path.join(os.getcwd(), folder_name)
    
    if platform.system() == "Windows":
        os.startfile(folder_path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.call(["open", folder_path])
    else:  # Linux/other
        subprocess.call(["xdg-open", folder_path])

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("NCAA NEXT Texture Renaming Utility v1.1")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("assets/theme.json")

        # Define a common background color
        bg_color = "#242424"
        
        # Determine the default monospaced and sans-serif fonts based on the OS
        if platform.system() == "Darwin":  # macOS
            mono_font_family = "Menlo"
            sans_font_family = "System"  # Updated to "System" for macOS
        elif platform.system() == "Windows":  # Windows
            mono_font_family = "Consolas"
            sans_font_family = "Segoe UI"
        elif platform.system() == "Linux":  # Linux
            mono_font_family = "Monospace"
            sans_font_family = "Sans"
        elif platform.system() == "Android":  # Android
            mono_font_family = "Monospace"  # Android uses "monospace" as the generic name
            sans_font_family = "Roboto"  # Android's default sans-serif font
        else:
            mono_font_family = "Monospace"  # Fallback to a generic monospaced font
            sans_font_family = "Sans"  # Fallback to a generic sans-serif font

        # Load icon images
        # self.refresh_icon = PhotoImage(file="assets/icon-refresh.png")

        self.dumps_finder = DumpsFinder()  # Initialize DumpsFinder instance

        self.error_event = threading.Event()  # Initialize the error event

        # Set the window size
        self.root.geometry("950x1")  # Start with a small height

        # Configure the root window grid
        self.root.grid_rowconfigure(0, weight=1)  # Row 0 will expand
        self.root.grid_columnconfigure(0, weight=1)  # Column 0 will expand

        # Main Frame
        self.main_frame = ctk.CTkFrame(root, corner_radius=0)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Layout grid
        self.main_frame.grid_columnconfigure(0, weight=1)  # Main column
        self.main_frame.grid_columnconfigure(1, weight=0)  # Side column for configuration
        self.main_frame.grid_rowconfigure(0, weight=0)  # Header row
        self.main_frame.grid_rowconfigure(1, weight=0)  # Main content row
        self.main_frame.grid_rowconfigure(2, weight=2)  # Output row
        self.main_frame.grid_rowconfigure(3, weight=0)  # Bottom row for configuration options
        self.main_frame.grid_rowconfigure(4, weight=0)  # Bottom row for configuration options

        # Header frame
        self.header_frame = ctk.CTkFrame(self.main_frame, corner_radius=0)
        self.header_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="nw")

        # Load the image (you need to have a PNG version of the SVG)
        header_image = Image.open("assets/icon-ncaanext-tool.png")  # Load your SVG or another image file
        header_image = header_image.resize((45, 45), Image.LANCZOS)  # Resize if necessary
        # Convert to CTkImage and specify the master (header_frame) to scale correctly
        self.header_image = ctk.CTkImage(light_image=header_image, dark_image=header_image, size=(45, 45))

        # Image label with defined height and width
        self.image_label = ctk.CTkLabel(self.header_frame, image=self.header_image, text="", width=45, height=45)
        self.image_label.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="w")


        # Header label
        self.header_label = ctk.CTkLabel(self.header_frame, text="Texture Renaming Utility", font=(sans_font_family,30))
        self.header_label.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")


        # CSV status text widget and buttons
        self.csv_frame = ctk.CTkFrame(self.main_frame)
        self.csv_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky=ctk.NSEW)

        # Configure row and column weights
        self.csv_frame.grid_rowconfigure(0, weight=1)
        self.csv_frame.grid_columnconfigure(0, weight=1)
        self.csv_frame.grid_columnconfigure(1, weight=0)

        # CSV status text widget
        self.csv_text = tk.Text(self.csv_frame, font=(sans_font_family,13), wrap="word", height=2, background=bg_color, fg="white", borderwidth=0, padx=5, pady=5, state=tk.DISABLED, cursor="arrow", relief="flat", highlightthickness=0)
        self.csv_text.grid(row=0, column=0, padx=(0, 10), pady=5, sticky=ctk.NSEW)

        # Buttons frame
        self.button_frame = ctk.CTkFrame(self.csv_frame)
        self.button_frame.grid(row=0, column=1, pady=5, sticky=ctk.NS)

        # Buttons
        self.browse_csv_button = ctk.CTkButton(self.button_frame, text="Open CSV Folder", command=self.open_csv_folder, fg_color="transparent", border_color="#1f538d", border_width=2)
        self.browse_csv_button.pack(pady=(0, 5))  # Add padding below the button

        # self.refresh_button = ctk.CTkButton(self.button_frame, text="Refresh App", image=self.refresh_icon, compound="left", command=self.refresh_csv_check, fg_color="transparent", border_color="#1f538d", border_width=2)
        self.refresh_button = ctk.CTkButton(self.button_frame, text="Refresh App", command=self.refresh_csv_check, fg_color="transparent", border_color="#1f538d", border_width=2)
        self.refresh_button.pack()


        # Create a scrolling text output pane using tkinter.Text
        self.output_text = tk.Text(self.main_frame, wrap="word", height=10, padx=10, pady=10, state=tk.NORMAL, font=(mono_font_family, 12), background="#1a1a1a", fg="#f1f1f1")
        self.scrollbar = tk.Scrollbar(self.main_frame, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=self.scrollbar.set)
        self.output_text.grid(row=2, column=0, padx=10, pady=10, sticky=ctk.NSEW)
        self.scrollbar.grid(row=2, column=1, sticky=ctk.NS)

        # Frame for checkboxes above run button
        self.checkbox_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.checkbox_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky=ctk.W)

        # Include Team Gloves checkbox
        self.team_glove = ctk.BooleanVar(value=True)
        self.team_glove_checkbox = ctk.CTkCheckBox(self.checkbox_frame, text="Include team gloves", variable=self.team_glove, command=self.on_team_glove_checked)
        self.team_glove_checkbox.pack(side="left", padx=(0, 20))
        Tooltip(self.team_glove_checkbox, "Must be done at least once per team. Doesn't hurt to leave it checked.")
        
        # Second Glove Checkbox
        self.second_glove = ctk.BooleanVar()
        self.second_glove_checkbox = ctk.CTkCheckBox(self.checkbox_frame, text="Opposite Home/Away Glove (See README!)", variable=self.second_glove, command=self.on_second_glove_checked)
        self.second_glove_checkbox.pack(side="left")
        Tooltip(self.second_glove_checkbox, "Run with this disabled first. Then again with it enabled. See the README for instructions!")

        # Run Function button (larger, at bottom of the main column)
        self.run_button = ctk.CTkButton(self.main_frame, text="Rename Source Textures", font=("Arial", 14, "bold"), command=self.start_function_thread, width=200, height=40)
        self.run_button.grid(row=4, column=0, padx=10, pady=10, sticky=ctk.EW)
        

        # ==== RIGHT COLUMN ================================


        # Define tags for colors in the tkinter.Text widget
        self.output_text.tag_configure("green", foreground="#40c131")
        self.output_text.tag_configure("blue", foreground="#6a42f6")
        self.output_text.tag_configure("red", foreground="red")
        self.output_text.tag_configure("yellow", foreground="yellow")

        # Side column for configuration options
        self.config_frame = ctk.CTkFrame(self.main_frame)
        self.config_frame.grid(row=0, column=1, rowspan=5, padx=10, pady=10, sticky=ctk.NS)


        # Sidebar top buttons frame
        self.side_buttons_frame = ctk.CTkFrame(self.config_frame)
        self.side_buttons_frame.grid(row=0, column=0, padx=10, pady=(5, 10), sticky=ctk.NSEW)

        # Configure the frame to have 2 columns
        self.side_buttons_frame.grid_rowconfigure(0, weight=1)  # Row for labels
        self.side_buttons_frame.grid_columnconfigure(0, weight=1)  # Column for Team Name
        self.side_buttons_frame.grid_columnconfigure(1, weight=1)  # Column for Slot

        self.readme_button = ctk.CTkButton(self.side_buttons_frame, text="View README", command=self.open_readme)
        self.readme_button.grid(row=0, column=0, padx=(0,5), pady=(3,8), sticky=ctk.W)

        self.readme_button = ctk.CTkButton(self.side_buttons_frame, text="Open RENAMED", fg_color="transparent", border_color="#1f538d", border_width=2, command=self.open_renamed)
        self.readme_button.grid(row=0, column=1, padx=(5, 0), pady=(3,8), sticky=ctk.W)


        # Sidebar header
        self.config_label = ctk.CTkLabel(self.config_frame, text="Config Settings:", font=("Arial", 18, "bold"))
        self.config_label.grid(row=1, column=0, padx=10, pady=(0, 5), sticky=ctk.NW)



        # Uniform Name frame
        self.uniname_frame = ctk.CTkFrame(self.config_frame)
        self.uniname_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky=ctk.NSEW)

        # Configure the frame to have 2 columns
        self.uniname_frame.grid_rowconfigure(0, weight=1)  # Row for labels
        self.uniname_frame.grid_rowconfigure(1, weight=1)  # Row for entry fields
        self.uniname_frame.grid_columnconfigure(0, weight=1)  # Column for Team Name
        self.uniname_frame.grid_columnconfigure(1, weight=1)  # Column for Slot

        # Team Name
        self.team_name_label = ctk.CTkLabel(self.uniname_frame, text="Team Name:")
        self.team_name_label.grid(row=0, column=0, padx=0, pady=(5, 0), sticky=ctk.W)  # Place label in column 0
        self.team_name_entry = ctk.CTkEntry(self.uniname_frame, width=100)
        self.team_name_entry.grid(row=1, column=0, padx=0, pady=(3, 3), sticky=ctk.EW)  # Place entry in column 0 below label
        Tooltip(self.team_name_label, "All lowercase, no spaces (Eg. 'appstate' instead of 'App State')")


        # Slot Selector with up/down arrows
        self.slot_label = ctk.CTkLabel(self.uniname_frame, text="Slot:")
        self.slot_label.grid(row=0, column=1, padx=(10, 0), pady=(5, 0), sticky=ctk.W)  # Place label in column 1
        Tooltip(self.slot_label, "The uniform slot (Eg. home, away, alt01, alt02)")

        # Create a list of allowed slots
        self.allowed_slots = ['home', 'away'] + [f'alt{str(i).zfill(2)}' for i in range(1, 19)]

        # Create a Spinbox-like control using an Entry with up/down buttons
        self.slot_value = tk.StringVar(value=self.allowed_slots[0])  # default to 'home'
        self.slot_entry = ctk.CTkEntry(self.uniname_frame, width=80, textvariable=self.slot_value)
        self.slot_entry.grid(row=1, column=1, padx=(10, 0), pady=(3, 3), sticky=ctk.EW)  # Place entry in column 1 below label

        # Up and Down buttons to change the Slot value
        def increment_slot():
            current_index = self.allowed_slots.index(self.slot_value.get())
            if current_index < len(self.allowed_slots) - 1:
                new_value = self.allowed_slots[current_index + 1]
                self.slot_value.set(new_value)
                update_radio_buttons(new_value)

        def decrement_slot():
            current_index = self.allowed_slots.index(self.slot_value.get())
            if current_index > 0:
                new_value = self.allowed_slots[current_index - 1]
                self.slot_value.set(new_value)
                update_radio_buttons(new_value)

        # Stack the buttons vertically
        self.increment_button = ctk.CTkButton(self.uniname_frame, text="▲", font=("Arial", 8, "bold"), width=10, height=4, command=increment_slot)
        self.increment_button.grid(row=1, column=2, padx=(0, 0), pady=(0, 0), sticky=ctk.N)  # To the right of slot entry

        self.decrement_button = ctk.CTkButton(self.uniname_frame, text="▼", font=("Arial", 8, "bold"), width=10, height=4, command=decrement_slot)
        self.decrement_button.grid(row=1, column=2, padx=(0, 0), pady=(0, 0), sticky=ctk.S)  # Below the increment button

        # Function to update the radio buttons based on the selected slot value
        def update_radio_buttons(slot_value):
            if slot_value == 'home':
                self.uniform_type.set('dark')  # Set to dark for home slot
            elif slot_value == 'away':
                self.uniform_type.set('light')  # Set to light for away slot
            else:
                alt_num = int(slot_value[-2:])  # Extract the number from 'altXX'
                # Alternate between dark and light for alt uniforms
                if alt_num % 2 == 0:
                    self.uniform_type.set('light')
                else:
                    self.uniform_type.set('dark')

        # Uniform Type (radio buttons)
        self.uniform_type_label = ctk.CTkLabel(self.config_frame, text="Uniform Type:")
        self.uniform_type_label.grid(row=4, column=0, padx=10, pady=(5,0), sticky=ctk.W)
        Tooltip(self.uniform_type_label, "Is this a DARK (typically home) uniform or LIGHT uniform?")

        self.uniform_type_frame = ctk.CTkFrame(self.config_frame)
        self.uniform_type_frame.grid(row=5, column=0, padx=10, pady=5, sticky=ctk.W+ctk.E)

        self.uniform_type = ctk.StringVar(value="dark")
        self.dark_radio = ctk.CTkRadioButton(self.uniform_type_frame, text="Dark", variable=self.uniform_type, value="dark")
        self.dark_radio.pack(side=tk.LEFT, padx=(0, 10))
        self.light_radio = ctk.CTkRadioButton(self.uniform_type_frame, text="Light", variable=self.uniform_type, value="light")
        self.light_radio.pack(side=tk.LEFT)

        # Ensure the radio buttons frame expands horizontally
        self.uniform_type_frame.grid_columnconfigure(0, weight=1)
        self.uniform_type_frame.grid_columnconfigure(1, weight=1)























        # Helmet Numbers Checkbox
        self.helmet_numbers = ctk.BooleanVar()
        self.helmet_checkbox = ctk.CTkCheckBox(self.config_frame, text="Helmet Numbers", variable=self.helmet_numbers)
        self.helmet_checkbox.grid(row=6, column=0, padx=10, pady=5, sticky=ctk.W)
        Tooltip(self.helmet_checkbox, "Enable if uniform has helmet numbers of any kind – back or side)")

        # Sleeve/Shoulder Numbers Checkbox
        self.sleeve_numbers = ctk.BooleanVar()
        self.sleeve_checkbox = ctk.CTkCheckBox(self.config_frame, text="Sleeve/Shoulder Numbers", variable=self.sleeve_numbers)
        self.sleeve_checkbox.grid(row=7, column=0, padx=10, pady=5, sticky=ctk.W)
        Tooltip(self.sleeve_checkbox, "Enable if uniform has numbers on the top of the shoulders OR side of sleeves.")

        # Pride Stickers Checkbox
        self.pride_stickers = ctk.BooleanVar()
        self.pride_checkbox = ctk.CTkCheckBox(self.config_frame, text="Pride Stickers", variable=self.pride_stickers)
        self.pride_checkbox.grid(row=8, column=0, padx=10, pady=5, sticky=ctk.W)
        Tooltip(self.pride_checkbox, "Enable if helmet will have visible pride stickers.")


        # Dumps Folder Path
        self.path_label = ctk.CTkLabel(self.config_frame, text="Dumps Folder Path:")
        self.path_label.grid(row=9, column=0, padx=10, pady=(5, 0), sticky=ctk.W)

        self.path_entry = ctk.CTkEntry(self.config_frame)
        self.path_entry.grid(row=10, column=0, padx=10, pady=(3,0), sticky=ctk.EW)

        # Frame to hold both buttons
        self.path_buttons_frame = ctk.CTkFrame(self.config_frame, fg_color="transparent", corner_radius=0)
        self.path_buttons_frame.grid(row=11, column=0, padx=10, pady=(3,8), sticky=ctk.W)

        self.path_button = ctk.CTkButton(
            self.path_buttons_frame, text="Choose Folder",
            command=self.browse_folder, fg_color="transparent",
            border_color="#1f538d", border_width=2
        )
        self.path_button.grid(row=0, column=0, padx=(0, 5))

        self.delete_button = ctk.CTkButton(
            self.path_buttons_frame, text="Delete Dumps",
            command=self.delete_dumps, fg_color="transparent",
            border_color="#d9534f", border_width=2
        )
        self.delete_button.grid(row=0, column=1)

        Tooltip(self.path_label, "Eg. C:\\PCSX2\\textures\\SLUS-21214\\dumps")


        # Save Configuration Button
        self.save_button = ctk.CTkButton(self.config_frame, text="Save Configuration", command=self.save_config)
        self.save_button.grid(row=12, column=0, padx=10, pady=(20, 10), sticky=ctk.EW)
        Tooltip(self.save_button, "Save these configuration options for the next time the app opens.")


        # Broswe Source button frame
        self.source_button_outer_frame = tk.Frame(self.config_frame, bg="#333333", bd=0)
        self.source_button_outer_frame.grid(row=13, column=0, pady=15, sticky=ctk.NSEW)
        # Broswe Source button frame
        self.source_button_frame = tk.Frame(self.source_button_outer_frame, bg=bg_color)
        self.source_button_frame.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)

        # Browse Source Folder
        self.browse_csv_button = ctk.CTkButton(self.source_button_frame, text="Open Source Textures Folder", command=self.open_source_folder, fg_color="transparent", border_color="#1f538d", border_width=2)
        self.browse_csv_button.pack(padx=5, pady=(15, 5))  # Add padding below the button

        # Only Make CSV Checkbox
        self.only_make_csv = ctk.BooleanVar()
        self.only_make_csv_checkbox = ctk.CTkCheckBox(
            self.source_button_frame,
            width=18,
            height=18,
            checkbox_width=18,
            checkbox_height=18,
            border_width=1,
            text="Don't rename, only make CSV",
            variable=self.only_make_csv,
            font=(sans_font_family, 10),
            command=self.toggle_other_checkboxes  # <-- Add callback here
        )
        self.only_make_csv_checkbox.pack(padx=5, pady=(5, 15))
        Tooltip(self.only_make_csv_checkbox, "Enable if only want to make a CSV file")


        # Defer the call to load_config using the after method
        self.root.after(100, self.load_config)
        # Check the CSV folder after everything is set up
        self.root.after(100, self.check_csv_folder)  # Ensure check_csv_folder runs after everything is set up

        # Update the window height based on content
        self.update_window_height()

    def toggle_other_checkboxes(self):
        """Enable or disable other checkboxes based on only_make_csv."""
        state = "disabled" if self.only_make_csv.get() else "normal"
        self.helmet_checkbox.configure(state=state)
        self.sleeve_checkbox.configure(state=state)
        self.pride_checkbox.configure(state=state)
    
    def add_link_to_csv_text(self, link_text, url):
        # Get the current index before inserting the link
        start_index = self.csv_text.index(tk.INSERT)
        
        # Insert the link text
        self.csv_text.insert(tk.INSERT, link_text)
        
        # Get the position after the link text is inserted
        end_index = self.csv_text.index(tk.INSERT)
        
        # Add a tag only to the "Click here" text
        self.csv_text.tag_add("link", start_index, end_index)
        self.csv_text.tag_configure("link", foreground="#588cc3", underline=True)
        
        # Bind the tag to open the link when clicked
        self.csv_text.tag_bind("link", "<Button-1>", lambda e: self.open_link(url))


    def delete_dumps(self):
        folder = self.path_entry.get()
        if not folder or not os.path.isdir(folder):
            self.update_output("\nError: Please select a valid folder first.\n")
            return

        png_files = [f for f in os.listdir(folder) if f.lower().endswith(".png")]
        if not png_files:
            self.update_output("\nNo PNG files found in the folder.\n")
            return

        count = 0
        for file in png_files:
            file_path = os.path.join(folder, file)
            try:
                os.remove(file_path)
                count += 1
            except Exception as e:
                self.update_output(f"\nError deleting {file_path}: {e}\n")

        self.update_output(f"\nDeleted {count} PNG file(s) from the dumps folder. Switch back to PCSX2 and press F9 twice to re-initiate dumping.\nDumps folder: {folder}\n")


    def open_link(self, url):
        import webbrowser
        webbrowser.open_new(url)


    def refresh_csv_check(self):
        self.check_csv_folder()

    def check_csv_folder(self):
        # Clear the output window
        # self.output_text.configure(state=tk.NORMAL)
        # self.output_text.delete("1.0", tk.END)
        # self.output_text.configure(state=tk.NORMAL)

        self.update_output("\nChecking CSV folder...\n")
        csv_folder = os.path.join(os.getcwd(), 'csv-override')
        # self.update_output(f"CSV folder path: {csv_folder}\n")
        
        if not os.path.exists(csv_folder):
            self.update_output("ERROR: CSV folder does not exist.\n", "red")
            return
        
        csv_files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]
        
        # Clear the previous text
        self.csv_text.configure(state=tk.NORMAL)
        self.csv_text.delete(1.0, tk.END)  # Clear previous text
        
        self.csv_source_file = ""

        if len(csv_files) == 0:
            self.csv_text.configure(state=tk.NORMAL)
            self.csv_text.insert(tk.END, "No CSV found. Ready to search the dumps folder. NOTE: Dumping must be done in a very specific way! ")
            self.csv_source_file = ""
            # Insert the clickable link
            self.add_link_to_csv_text("Click here for the guide →", "https://docs.google.com/document/d/1RI2ceiXVRgVu8H-POCee2n3O08iQxa_Q/edit#heading=h.inb40xudxrzt")
            self.csv_text.insert(tk.END, "\n\n")
            self.csv_text.configure(state=tk.DISABLED)
            self.run_button.configure(
                text="Find Dumped Textures",
                command=self.start_dumpsfinder_thread,
                state="normal"
            )
            self.path_label.configure(state="normal")
            self.path_entry.configure(state="normal")
            self.path_button.configure(state="normal")
            self.second_glove_checkbox.configure(state="normal")
            self.team_glove_checkbox.configure(state="normal")
            self.team_name_entry.configure(state="normal")
            self.slot_entry.configure(state="normal")
            self.increment_button.configure(state="normal")
            self.decrement_button.configure(state="normal")
            self.uniform_type_label.configure(state="normal")
            self.dark_radio.configure(state="normal")
            self.light_radio.configure(state="normal")
            if self.only_make_csv == "no":
              self.helmet_checkbox.configure(state="normal")
              self.sleeve_checkbox.configure(state="normal")
              self.pride_checkbox.configure(state="normal")
            self.only_make_csv_checkbox.configure(state="normal")
            self.header_label.configure(text="Dumps Image Recognition")
            self.update_output("No CSV found. Ready to search the dumps folder.\n\n")
        elif len(csv_files) == 1:
            self.update_output(f"CSV folder path: {csv_folder}\n")
            self.update_output(f"Found CSV file: {csv_files}\n\n")
            csv_source_folder = os.path.join(os.getcwd(), 'csv-source')
            self.update_output("Checking if a SOURCE CSV exists...\n")
            if os.path.exists(csv_source_folder):
              csv_source_files = [
                  os.path.join(root, f)
                  for root, _, files in os.walk(csv_source_folder)
                  for f in files
                  if f.endswith('.csv')
              ]
              
              # Check for PNG files
              png_source_files = [
                  os.path.join(root, f)
                  for root, _, files in os.walk(csv_source_folder)
                  for f in files
                  if f.lower().endswith('.png')
              ]
              folder_no_pngs = (len(png_source_files) == 0)
              folder_has_pngs = (len(png_source_files) > 0)

              if len(csv_source_files) == 0 and folder_no_pngs:
                  # Folder is completely empty
                  self.update_csv_text("CSV provided. Skipping dumps image matching. Using texture names in CSV.")
                  self.update_output("No source CSV provided in 'csv-source'. Folder is empty. Using source textures in YOUR_TEXTURES_HERE.\n")

              elif len(csv_source_files) == 0 and folder_has_pngs:
                  # Folder has files or folders but no CSVs
                  self.update_csv_text("No CSV found. Using textures in YOUR_TEXTURES_HERE for matching.")
                  self.update_output("!!! ATTENTION !!! ", "yellow")
                  self.update_output("No CSV provided in 'csv-source', but other files/folders were found. Did you mean to provide a source uniform? If not, you can ignore this message. Renaming will use the source textures in YOUR_TEXTURES_HERE.\n")

              elif len(csv_source_files) == 1 and folder_no_pngs:
                 self.csv_source_file = csv_source_files[0]
                 self.update_csv_text("A source CSV was found, but no textures were provided in 'csv-source'. Add a complete uniform folder and refresh the app.", "red")
                 self.update_output("!!! ERROR !!! ", "red")
                 self.update_output("A source CSV was found, but no textures were provided in 'csv-source'. Add a complete uniform folder and refresh the app.\n")
              
              elif len(csv_source_files) == 1 and folder_has_pngs:
                 self.csv_source_file = csv_source_files[0]
                 self.update_csv_text("CSVs provided. Skipping dumps image matching. Using texture names in 'csv-override' folder. Using source textures and CSV in 'csv-source' folder.")
                 self.update_output("A source CSV was provided. Using the textures in csv-source folder for renaming.\n")
              else:
                self.update_csv_text("More than one CSV provided in csv-source. Remove all but one CSV (or all to use textures in YOUR_TEXTURES_HERE for the source files).", "red")
                self.update_output("!!! ERROR !!! ", "red")
                self.update_output("More than one CSV provided in csv-source. Remove all but one CSV (or all to use textures in YOUR_TEXTURES_HERE for the source files).", "red")
            else:
              self.update_output("No source CSV and textures provided. Using the YOUR_TEXTURES_HERE folder.\n")

            self.run_button.configure(
                text="Rename Source Textures",
                command=self.start_function_thread,
                state="normal"
            )
            self.path_label.configure(state="disabled")
            self.path_entry.configure(state="disabled")
            self.path_button.configure(state="disabled")
            self.second_glove.set(False)
            self.team_glove.set(False)
            self.second_glove_checkbox.configure(state="disabled")
            self.team_glove_checkbox.configure(state="disabled")
            self.team_name_entry.configure(state="disabled")
            self.slot_entry.configure(state="disabled")
            self.increment_button.configure(state="disabled")
            self.decrement_button.configure(state="disabled")
            self.uniform_type_label.configure(state="disabled")
            self.dark_radio.configure(state="disabled")
            self.light_radio.configure(state="disabled")
            self.helmet_checkbox.configure(state="normal")
            self.sleeve_checkbox.configure(state="normal")
            self.pride_checkbox.configure(state="normal")
            self.header_label.configure(text="CSV Renaming")
            self.only_make_csv.set(False)
            self.only_make_csv_checkbox.configure(state="disabled")
            
            
            self.process_csv(os.path.join(csv_folder, csv_files[0]))  # Process the CSV file
        else:
            self.update_csv_text("More than one CSV provided. Remove all but one CSV (or all to search dumps).", "red")
            self.update_output("More than one CSV provided. Remove all but one CSV (or all to search dumps).", "red")
            self.run_button.configure(state="disabled")
            self.header_label.configure(text="CSV Renaming (ERROR)")
            self.update_output("ERROR: Multiple CSV files found. Remove all but one.\n\n", "red")


    def update_csv_text(self, message, color="white"):
        # Function to update the text widget
        self.csv_text.configure(state=tk.NORMAL)
        self.csv_text.delete(1.0, tk.END)  # Clear previous text
        self.csv_text.insert(tk.END, message)
        self.csv_text.tag_add(color, "1.0", tk.END)
        self.csv_text.tag_configure(color, foreground=color)
        self.csv_text.configure(state=tk.DISABLED)


    def process_csv(self, csv_file):
        # Read the CSV file and update the fields
        import csv


        with open(csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            if len(rows) > 1 and len(rows[1]) >= 3:
                uniform_slot_name = f"{rows[1][0]}-{rows[1][1]}"

                # Extract team name and slot from the uniform_slot_name
                team_name, slot = uniform_slot_name.split('-')
                team_name = team_name.replace(" ", "").lower()  # Remove spaces and make lowercase
                
                # Update the team name and slot fields
                self.team_name_entry.configure(state="normal")
                self.team_name_entry.delete(0, tk.END)
                self.team_name_entry.insert(0, team_name)
                self.team_name_entry.configure(state="disabled")

                self.slot_entry.configure(state="normal")
                self.slot_entry.delete(0, tk.END)
                self.slot_entry.insert(0, slot)
                self.slot_entry.configure(state="disabled")

                uniform_type = rows[1][2].strip().lower()
                if uniform_type == "light":
                    self.uniform_type.set("light")
                elif uniform_type == "dark":
                    self.uniform_type.set("dark")
                # Disable the uniform type radio buttons
                self.dark_radio.configure(state="disabled")
                self.light_radio.configure(state="disabled")

    def open_csv_folder(self):
        open_folder('csv-override')

    def open_source_folder(self):
        open_folder('YOUR_TEXTURES_HERE')
            
    def open_renamed(self):
        open_folder('RENAMED')

    def start_function_thread(self):
        # Clear the output window
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.configure(state=tk.NORMAL)

        # Collect values from the GUI
        dumps_path = self.path_entry.get()

        # Get and format the team name and slot
        team_name = self.team_name_entry.get().replace(" ", "").lower()  # Remove spaces and make lowercase
        slot = self.slot_entry.get().replace(" ", "").lower()  # Remove spaces and make lowercase
        uniform_slot_name = f"{team_name}-{slot}"  # Concatenate with a dash

        uniform_type = self.uniform_type.get()
        second_glove = "yes" if self.second_glove.get() else "no"
        team_glove = "yes" if self.team_glove.get() else "no"
        photoshop_pref = "1"  # Default value
        pridesticker_pref = "yes" if self.pride_stickers.get() else "no"
        helmetnumbers_pref = "yes" if self.helmet_numbers.get() else "no"
        ssnumbers_pref = "yes" if self.sleeve_numbers.get() else "no"
        only_make_csv = "yes" if self.sleeve_numbers.get() else "no"
        
        # Start the function in a separate thread to avoid freezing the GUI
        threading.Thread(target=self.run_function_with_output, args=(dumps_path, uniform_slot_name, uniform_type, team_glove, second_glove, photoshop_pref, pridesticker_pref, helmetnumbers_pref, ssnumbers_pref, only_make_csv, self.csv_source_file), daemon=True).start()
    
    def start_dumpsfinder_thread(self):
        # Clear the output window
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.configure(state=tk.NORMAL)

        # Collect values from the GUI
        dumps_path = self.path_entry.get()

        # Get and format the team name and slot
        team_name = self.team_name_entry.get().replace(" ", "").lower()  # Remove spaces and make lowercase
        slot = self.slot_entry.get().replace(" ", "").lower()  # Remove spaces and make lowercase
        uniform_slot_name = f"{team_name}-{slot}"  # Concatenate with a dash

        uniform_type = self.uniform_type.get()
        team_glove = "yes" if self.team_glove.get() else "no"
        second_glove = "yes" if self.second_glove.get() else "no"
        photoshop_pref = "1"  # Default value
        pridesticker_pref = "yes" if self.pride_stickers.get() else "no"
        helmetnumbers_pref = "yes" if self.helmet_numbers.get() else "no"
        ssnumbers_pref = "yes" if self.sleeve_numbers.get() else "no"
        only_make_csv = "yes" if self.only_make_csv.get() else "no"
        
        # Start the function in a separate thread to avoid freezing the GUI
        threading.Thread(target=self.run_dumpsfinder_with_output, args=(dumps_path, uniform_slot_name, uniform_type, team_glove, second_glove, photoshop_pref, pridesticker_pref, helmetnumbers_pref, ssnumbers_pref, only_make_csv), daemon=True).start()

    def run_function_with_output(self, dumps_path, uniform_slot_name, uniform_type, team_glove, second_glove, photoshop_pref, pridesticker_pref, helmetnumbers_pref, ssnumbers_pref, only_make_csv, csv_source_file):
        try:
            # Use the run_function from utils/functions.py and pass the callback for output
            run_function(self.update_output, dumps_path, uniform_slot_name, uniform_type, team_glove, second_glove, photoshop_pref, pridesticker_pref, helmetnumbers_pref, ssnumbers_pref, only_make_csv, csv_source_file)
        except Exception as e:
            self.update_output(f"Error occurred: {str(e)}", "red")
            self.error_event.set()  # Signal that an error occurred

    def run_dumpsfinder_with_output(self, dumps_path, uniform_slot_name, uniform_type, team_glove, second_glove, photoshop_pref, pridesticker_pref, helmetnumbers_pref, ssnumbers_pref, only_make_csv):
        try:
            # Check if dumps_path is not defined or the folder does not exist
            if not dumps_path or not os.path.exists(dumps_path):
                self.update_output(f"[!] The DUMPS FOLDER does not exist.\n", "red")
                self.update_output(f"{dumps_path}\n", "yellow")
                self.error_event.set()  # Signal that an error occurred
                return
            # Use the run_function from utils/functions.py and pass the callback for output
            self.dumps_finder.run_dumpsfinder(self.update_output, dumps_path, uniform_slot_name, uniform_type, team_glove, second_glove, photoshop_pref, pridesticker_pref, helmetnumbers_pref, ssnumbers_pref, only_make_csv)
        except Exception as e:
            self.update_output(f"Error occurred: {str(e)}", "red")
            self.error_event.set()  # Signal that an error occurred

    def update_output(self, message, color="black"):
        # Function to update the text output pane
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.insert(tk.END, message, (color,))
        self.output_text.see(tk.END)  # Automatically scroll to the end
        self.output_text.configure(state=tk.DISABLED)

    def browse_folder(self):
        # Open a file dialog to select a folder
        folder_path = filedialog.askdirectory()
        
        # Update the entry if a folder was selected
        if folder_path:
            self.path_entry.delete(0, tk.END)  # Clear the entry
            self.path_entry.insert(0, folder_path)  # Insert the selected folder path


    def save_config(self):

        
        # Save the configuration to a config.txt file
        config = configparser.ConfigParser()

        # Combine team_name_entry and slot_entry into a dash-separated value
        team_name = self.team_name_entry.get()
        # Format Team Name: remove spaces and convert to lowercase
        formatted_team_name = team_name.replace(" ", "").lower()
        slot = self.slot_value.get()
        uniform_slot_name = f"{formatted_team_name}-{slot}"  # Combine the values

        config['Settings'] = {
            'dumps_path': 'r"' + self.path_entry.get() + '"',  # Add "r" for raw string
            'uniform_slot_name': uniform_slot_name,  # Save the combined value
            'uniform_type': self.uniform_type.get(),
            'photoshop_pref': "1",  # Default to Photoshop as "1"
            'pridesticker_pref': "yes" if self.pride_stickers.get() else "no",
            'helmetnumbers_pref': "yes" if self.helmet_numbers.get() else "no",
            'ssnumbers_pref': "yes" if self.sleeve_numbers.get() else "no",
            'second_glove': "yes" if self.second_glove.get() else "no"
        }

        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
        self.update_output("\nConfig saved!\n")

    def load_config(self):
        self.update_output("Loading config...\n")
        if os.path.exists(CONFIG_FILE):
            config = configparser.ConfigParser()
            config.read(CONFIG_FILE)
            self.update_output(f"Config file path: {CONFIG_FILE}\n")

            # Get the uniform_slot_name value and split it into team_name and slot
            uniform_slot_name = config.get('Settings', 'uniform_slot_name', fallback="")
            if "-" in uniform_slot_name:
                team_name, slot = uniform_slot_name.split("-", 1)
                self.team_name_entry.insert(0, team_name)  # Populate the team_name_entry
                self.slot_value.set(slot)  # Populate the slot_entry with the second segment
            else:
                self.update_output("Invalid format for uniform_slot_name in config.\n")

            self.path_entry.insert(0, config.get('Settings', 'dumps_path', fallback="")[2:-1])  # Remove the raw string "r" and quotes
            self.uniform_type.set(config.get('Settings', 'uniform_type', fallback="dark"))
            self.helmet_numbers.set(config.getboolean('Settings', 'helmetnumbers_pref', fallback=False))
            self.sleeve_numbers.set(config.getboolean('Settings', 'ssnumbers_pref', fallback=False))
            self.pride_stickers.set(config.getboolean('Settings', 'pridesticker_pref', fallback=False))
            self.second_glove.set(config.getboolean('Settings', 'second_glove', fallback=False))

            self.update_output("Config loaded. 👍\n")
        else:
            self.update_output("Config file does not exist.\n")
            self.update_output("\nConfig file not found.\n")
    
    def open_readme(self):
        # Path to the HTML file
        html_file_path = "README.html"

        try:
            # Check if the HTML file exists
            if not os.path.isfile(html_file_path):
                raise FileNotFoundError(f"The file {html_file_path} does not exist.")

            # Open the HTML file in the default web browser
            webbrowser.open("file://" + os.path.abspath(html_file_path))
        except Exception as e:
            print(f"Error loading README file: {e}")

    def update_window_height(self):
        # Update the window height based on the content
        self.root.update_idletasks()  # Ensure that all layout updates are processed
        height = self.root.winfo_reqheight()  # Get the required height
        self.root.geometry(f"950x{height}")  # Set the width and height

    # Callback function for second glove checkbox
    def on_second_glove_checked(self):
        if self.second_glove.get():  # If second_glove_checkbox is checked
            self.team_glove.set(False)  # Uncheck team_glove_checkbox
    # Callback function for team glove checkbox
    def on_team_glove_checked(self):
        if self.team_glove.get():  # If team_glove_checkbox is checked
            self.second_glove.set(False)  # Uncheck second_glove_checkbox

if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()
