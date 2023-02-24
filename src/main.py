import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from wrapup import WrapUpDateCalculator
from cardpayment import CardPayment
from map import Map
from pwmanager import PasswordManager
from authentication import Authenticator
import os
import sys
import json
import requests


FONT = ('Bahnschrift Light', 17, 'normal')
BG_COLOR = '#30323D'
FG_COLOR = 'white'
HOVER_BUTTON_COLOR = 'SlateGray4'
ACTIVE_BG_COLOR = 'SlateGray2'


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title('Project AtBS')
        self.config(bg=BG_COLOR)
        self.resizable(width=False, height=False)
        self.iconphoto(False, tk.PhotoImage(file='assets/img/atbs_icon.png'))
        self.main_app_current_version = 'v4.6.1'

        self.button_images = []
        # Create buttons
        self.cp_but = self.create_button(
            'Payment', 'cc_icon.png', self.open_CardPaymentForm)
        self.wud_but = self.create_button(
            'Wrap Up', 'cal_calc.png', self.open_WrapUpDateCalculator)
        self.m_but = self.create_button(
            'Map', 'map_icon.png', self.open_MapSearch)
        self.pm_but = self.create_button(
            'Password', 'lock_icon.png', self.open_PasswordManager)

        # Place buttons on grid
        self.cp_but.grid(column=0, row=0, sticky='EW')
        self.wud_but.grid(column=0, row=1, sticky='EW')
        self.m_but.grid(column=0, row=2, sticky='EW')
        self.pm_but.grid(column=0, row=3, sticky='EW')

        # Bind events
        self.bind('<Enter>', self.pointerEnter)
        self.bind('<Leave>', self.pointerLeave)

        # Center window to screen
        self.update_idletasks()
        win_width = self.winfo_reqwidth()
        win_height = self.winfo_reqheight()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int(screen_width/2 - win_width/2)
        y = int(screen_height/2 - win_width/2)
        self.geometry(f"{win_width}x{win_height}+{x}+{y}")
        self.deiconify()

        self.after(ms=86_400_000, func=self._check_for_updates_loop) # every 24 hours

    def create_button(self, text, image_path, command):
        img_open = Image.open(fp=f'assets/img/{image_path}')
        img_resized = img_open.resize(size=(50, 50))
        self.img = ImageTk.PhotoImage(img_resized)
        self.button_images.append(self.img)
        button = tk.Button(text=f'  {text}', image=self.img, compound='left', font=FONT, fg=FG_COLOR,
                           bg=BG_COLOR, activebackground=ACTIVE_BG_COLOR, command=command,
                           anchor='w', padx=10, pady=5, width=207)
        return button

    def open_WrapUpDateCalculator(self):
        """Instantiate WrapUpDateCalculator object in a new TopLevel window."""
        WrapUpDateCalculator()

    def open_CardPaymentForm(self):
        """Instantiate CardPayment object in a new TopLevel window."""
        CardPayment()

    def open_MapSearch(self):
        """Instantiate Map object in a new TopLevel window."""
        Map()

    def open_PasswordManager(self):
        """Instantiate Password Manager in a new TopLevel window."""
        a = Authenticator()
        self._check_isVerified_flag(a)

    def _check_isVerified_flag(self, authenticator):
        """Recursively checks isVerified flag to signal instantiation of Password Manager object."""
        if not authenticator.isVerified:
            self.after(50, self._check_isVerified_flag, authenticator)
        else:
            authenticator.top.destroy()
            PasswordManager()

    def pointerEnter(self, event):
        """Change button color on mouse hover."""
        event.widget['bg'] = HOVER_BUTTON_COLOR

    def pointerLeave(self, event):
        """Change button color back to normal when mouse leave button."""
        event.widget['bg'] = BG_COLOR

    def check_for_new_updater_version(self):
        """Check for new version and update the App Update Manager"""
        if getattr(sys, 'frozen', False):
            root_path = os.path.dirname(sys.executable)
        else:
            root_path = os.path.dirname(os.path.abspath(__file__))

        current_updater_version_path = f'{root_path}/dist/current_version/current_updater_version.json'
        latest_updater_version_url = 'https://raw.githubusercontent.com/michael-hoang/project-atbs-work/main/dist/latest_version/latest_updater_version.json'
        with open(current_updater_version_path) as f:
            data = json.load(f)
            updater_current_version = data['updater']

        latest_updater_version_response = requests.get(latest_updater_version_url)
        if latest_updater_version_response.status_code == 200:
            data = json.loads(latest_updater_version_response.content)
            updater_latest_version = data['updater']

        if updater_current_version != updater_latest_version:
            updater_path = f'{root_path}/dist/update.exe'
            updater_dl_url = 'https://github.com/michael-hoang/project-atbs-work/raw/main/dist/update.exe'
            # Download latest update.exe
            block_size = 1024
            response = requests.get(updater_dl_url, stream=True)
            with open(updater_path, 'wb') as f:
                for data in response.iter_content(block_size):
                    f.write(data)
            # Download current_updater_version.json
            block_size = 4
            with open(current_updater_version_path, 'wb') as f:
                for data in latest_updater_version_response.iter_content(block_size):
                    f.write(data)
        
    def _check_for_updates_loop(self):
        """Run with Tkinter after method to check for updates periodically."""
        try:
            self.check_for_new_updater_version()
            if self.check_for_main_app_update(yesno_update_message=2):
                self.open_Updater()
                self.quit()
        except:
            pass

        self.after(ms=86_400_000, func=self._check_for_updates_loop) # every 24 hours 

    def check_for_main_app_update(self, yesno_update_message=1) -> bool:
        """Check if new version of Main App is available."""
        if getattr(sys, 'frozen', False):
            root_path = os.path.dirname(sys.executable)
        else:
            root_path = os.path.dirname(os.path.abspath(__file__))

        current_main_version_path = f'{root_path}\dist\current_version\current_main_version.json'
        latest_version_url = 'https://raw.githubusercontent.com/michael-hoang/project-atbs-work/main/dist/latest_version/latest_main_version.json'
        with open(current_main_version_path) as f:
            data = json.load(f)
            main_app_current_version = data['main']

        latest_version_response = requests.get(latest_version_url)
        if latest_version_response.status_code == 200:
            data = json.loads(latest_version_response.content)
            main_app_latest_version = data['main']

        if main_app_current_version != main_app_latest_version:
            if yesno_update_message == 1:
                message=f'{main_app_latest_version} is now available. Do you want to open App Update Manager?'
            elif yesno_update_message == 2:
                message=f'{main_app_latest_version} is now available. Do you want to close the app and open App Update Manager?'

            return messagebox.askyesno(title='New Update Available', message=message)
                                       
        return False

    def open_Updater(self):
        """Run App Update Manager"""
        if getattr(sys, 'frozen', False):
            root_path = os.path.dirname(sys.executable)
        else:
            root_path = os.path.dirname(os.path.abspath(__file__))
        os.startfile(f'{root_path}/dist/update.exe')


if __name__ == '__main__':
    try:
        MainApp.check_for_new_updater_version(None)
        if MainApp.check_for_main_app_update(None):
            MainApp.open_Updater(None)
        else:
            MainApp().mainloop()
    except:
        MainApp().mainloop()
