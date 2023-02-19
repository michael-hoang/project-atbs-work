"""This module contains a class called Updater which checks on Github for the
latest release on a repository and downloads it to the user's root directory."""


import requests
import sys
import os
import tkinter as tk
from tkinter import END
import json


FONT = ('Helvetica', 12, 'normal')
STATUS_FONT = ('Helvetica', 12, 'bold')


class Updater:
    """This class creates a GUI which checks for latest repo updates and prompts
    the user to download and install."""

    def __init__(self):
        """Initialize version number, Github URL, paths, and GUI."""

        self.updater_current_version = 'v1.0.0'
        self.latest_version_url = 'https://raw.githubusercontent.com/michael-hoang/project-atbs-work/main/dist/latest_version/latest_version.json'
        self.latest_app_dl_url = 'https://github.com/michael-hoang/project-atbs-work/raw/main/dist/latest_version/main.exe'
        self.updater_path = ''
        self.root_directory = ''
        self.main_app_path = ''
        self.current_version_path = ''
        self.main_app_current_version = ''
        self.main_app_latest_version = ''

        # GUI
        self.root = tk.Tk()
        self.root.title('App Update Manager')
        self.root.resizable(width=False, height=False)

        self.lf_current_version = tk.LabelFrame(self.root, text='Current Version', font=FONT)
        self.lf_current_version.grid(column=0, row=0, columnspan=2, padx=20, pady=(20, 0))

        self.l_updater_current_version = tk.Label(
            self.lf_current_version, text='App Update Manager:', font=FONT)
        self.l_updater_current_version.grid(column=0, row=0, sticky='e', padx=(15, 0), pady=(15, 0))
        self.e_updater_current_version = tk.Entry(self.lf_current_version, width=8, font=FONT)
        self.e_updater_current_version.insert(0, self.updater_current_version)
        self.e_updater_current_version.grid(column=1, row=0, padx=(0, 15), pady=(15, 0))
        self.e_updater_current_version.config(state='disabled')

        self.l_main_app_current_version = tk.Label(
            self.lf_current_version, text='Main App:', font=FONT)
        self.l_main_app_current_version.grid(column=0, row=1, sticky='e', padx=(15, 0), pady=(0, 15))
        self.e_main_app_current_version = tk.Entry(self.lf_current_version, width=8, font=FONT)
        self.e_main_app_current_version.grid(column=1, row=1, padx=(0, 15), pady=(0, 15))

        self.l_status = tk.Label(self.root, text='Status:', font=STATUS_FONT)
        self.l_status.grid(column=0, row=1, padx=(15, 0), pady=(20), sticky='w')
        self.l_status_message = tk.Label(self.root, text='', font=STATUS_FONT)
        self.l_status_message.grid(column=1, row=1, padx=(0, 15), pady=(20), sticky='w')

        self.b_check_update = tk.Button(
            self.root, text='Check for updates', font=FONT, command=self.check_for_latest_main_app_version, width=17)
        self.b_check_update.grid(columnspan=2, pady=(0, 20))

        self.center_root_window_to_screen()
        self.get_paths()
        self.get_current_main_app_version()
        # GUI icon
        icon_path = self.root_directory.replace('\\', '/')
        self.root.iconphoto(False, tk.PhotoImage(file=f'{icon_path}/assets/img/update.png'))
        
        self.root.mainloop()


    def center_root_window_to_screen(self):
        """Center root window"""

        self.root.update_idletasks()
        win_width = self.root.winfo_reqwidth()
        win_height = self.root.winfo_reqheight()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int(screen_width/2 - win_width/2)
        y = int(screen_height/2 - win_width/2)
        self.root.geometry(f"{win_width}x{win_height}+{x}+{y}")
        self.root.deiconify()

    def get_paths(self):
        """Get paths for current working directory, main app, and updater."""

        if getattr(sys, 'frozen', False):
            self.updater_path = os.path.dirname(sys.executable)
        else:
            self.updater_path = os.path.dirname(os.path.abspath(__file__))

        self.root_directory = self.updater_path[:-5]
        self.main_app_path = f'{self.root_directory}\main.exe'
        self.current_version_path = f'{self.updater_path}\current_version\current_version.json'

    def get_current_main_app_version(self):
        """Retrieve the current version number for the main app"""

        with open(self.current_version_path) as f:
            data = json.load(f)
            self.main_app_current_version = data['main']

        self.e_main_app_current_version.config(state='normal')
        self.e_main_app_current_version.delete(0, END)
        self.e_main_app_current_version.insert(0, f'{self.main_app_current_version}')
        self.e_main_app_current_version.config(state='disabled')

    def get_latest_main_app_version(self):
        """Retrieve the latest version number for the main app."""

        latest_version_response = requests.get(self.latest_version_url)
        if latest_version_response.status_code == 200:
            data = json.loads(latest_version_response.content)
            self.main_app_latest_version = data['main']

    def update_status_message(self, message, font_color):
        """Update status Label with new text message, text color, and font."""

        self.l_status_message.config(text=message, fg=font_color)

    def check_for_latest_main_app_version(self):
        """Compare main app's current version with the latest version on Github repo."""

        self.get_latest_main_app_version()
        if self.main_app_current_version != self.main_app_latest_version:
            message = f'{self.main_app_latest_version} available'
            font_color = 'green'
            # Change button to Update if new main app version is available to download.
            self.b_check_update.config(text='Update', command=self.update_main_app)
        else:
            message = 'No update available'
            font_color = 'black'

        self.update_status_message(message, font_color)

    def download_latest_files(self):
        """Download the latest files from Github repo."""

        # Download main.exe
        response = requests.get(self.latest_app_dl_url, stream=True)
        block_size = 1024
        with open(self.main_app_path, 'wb') as f:
            for data in response.iter_content(block_size):
                f.write(data)
        # Download current_version.json
        response = requests.get(self.latest_version_url, stream=True)
        block_size = 4
        with open(self.current_version_path, 'wb') as f:
            for data in response.iter_content(block_size):
                f.write(data)

    def reset_button(self):
        """Reset button back to 'Check for updates'"""

        self.b_check_update.config(
            text='Check for updates', command=self.check_for_latest_main_app_version, fg='black')
        
    def open_main_app(self):
        """Run main.exe from root directory."""

        os.startfile(self.main_app_path, cwd=self.root_directory)

    def update_main_app(self):
        """Update the main app"""

        self.download_latest_files()
        self.get_current_main_app_version()
        self.update_status_message('App has been updated', 'green')
        self.reset_button()
        self.open_main_app()
            

if __name__ == '__main__':
    Updater()
