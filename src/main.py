import ttkbootstrap as tkb
from tkinter import messagebox
from cardpayment import CardPayment
import os
import sys
import json
import requests
from program_files_manager import ProgramFileManager


CURRENT_VERSION = 'v6.2.0'

class MainApp(tkb.Window):
    def __init__(self):
        super().__init__('Card Payment Form', 'litera', resizable=(False, False))
        self.current_version = CURRENT_VERSION
        CardPayment(self, self)
        
       
        self.after(ms=86_400_000, func=self._check_for_updates_loop) # every 24 hours

    def get_exe_script_path(self) -> str:
        """Return the path to the current exe or script file."""
        if getattr(sys, 'frozen', False):
            path = os.path.dirname(sys.executable)
        else:
            path = os.path.dirname(os.path.abspath(__file__))
        return path

    def check_for_new_updater_version(self):
        """Check for new version and update the App Update Manager"""
        try:
            root_path = self.get_exe_script_path()
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
                updater_exe_response = requests.get(updater_dl_url, stream=True)
                with open(updater_path, 'wb') as f:
                    for data in updater_exe_response.iter_content(block_size):
                        f.write(data)
                # Download current_updater_version.json
                block_size = 4
                current_updater_version_path = f'{root_path}/dist/current_version/current_updater_version.json'
                with open(current_updater_version_path, 'wb') as f:
                    for data in latest_updater_version_response.iter_content(block_size):
                        f.write(data)
        except:
            pass
        
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
        latest_version_url = 'https://raw.githubusercontent.com/michael-hoang/project-atbs-work/main/dist/latest_version/latest_main_version.json'
        response = requests.get(latest_version_url)
        if response.status_code == 200:
            data = json.loads(response.content)
            latest_version = data['main']
        
        if CURRENT_VERSION != latest_version:
            if yesno_update_message == 1:
                message=f'{latest_version} is now available. Do you want to open App Update Manager?'
            elif yesno_update_message == 2:
                message=f'{latest_version} is now available. Do you want to close the app and open App Update Manager?'

            return messagebox.askyesno(title='New Update Available', message=message)
                                       
        return False

    def open_Updater(self):
        """Run App Update Manager"""
        root_path = self.get_exe_script_path()
        os.startfile(f'{root_path}/dist/update.exe')


if __name__ == '__main__':
    pfm = ProgramFileManager()
    pfm.download_essential_files(CURRENT_VERSION)
    app = MainApp()
    app.withdraw()
    try:
        app.check_for_new_updater_version()
        if app.check_for_main_app_update():
            app.open_Updater()
            app.quit()
    except:
        pass

    app.place_window_center()
    app.deiconify()
    app.mainloop()
    