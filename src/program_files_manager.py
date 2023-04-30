"""This module provides a class that handles critical files necessary for the Main app to operate correctly."""

import json
import os
import requests
import sys
import urllib.request

from assets_manager import AssetManager


class ProgramFileManager:
    """
    This class provides methods to retrieve the paths to the running script or
    executable and download all critical files required for the Main app to
    function correctly.
    """

    def __init__(self):
        """
        Initialize AssetManager object, latest version URL, and update
        executable URL attributes.
        """
        self.assets = AssetManager()
        self.latest_version_url = 'https://raw.githubusercontent.com/michael-hoang/project-atbs-work/main/dist/latest_version/latest_main_version.json'
        self.update_exe_url = 'https://github.com/michael-hoang/project-atbs-work/raw/main/dist/update.exe'
        self.directories = None

    def get_latest_version_number(self) -> str:
        """Return the latest version number for the Main app."""
        try:
            response = requests.get(self.latest_version_url)
            if response.status_code == 200:
                data = json.loads(response.content)
                latest_version = data['main']
                return latest_version
        except:
            return ''

    def get_program_directory_path(self):
        """
        Create an attribute for the absolute path to the running program
        directory (root path). The program can be an executable or a script.
        """
        if getattr(sys, 'frozen', False):
            path = os.path.dirname(sys.executable)
        else:
            path = os.path.dirname(os.path.abspath(__file__))
        self.root_path = path

    def create_required_directories(self):
        """
        Create all the necessary directories that contain essential files for
        the Main app. The paths are stored in a Python dictionary as an attribute.
        """
        directories = {
            'assets': os.path.join(self.root_path, 'assets'),
            'form': os.path.join(self.root_path, 'assets', 'form'),
            'img': os.path.join(self.root_path, 'assets', 'img'),
            'dist': os.path.join(self.root_path, 'dist'),
            'current_version': os.path.join(self.root_path, 'dist', 'current_version')
        }
        for directory in directories.values():
            if not os.path.exists(directory):
                os.mkdir(directory)

        self.directories = directories

    def create_current_version_json(self, current_version_number: str):
        """Create current_main_version.json file if it doesn't exist."""
        json_path = os.path.join(
            self.directories['current_version'], 'current_main_version.json'
        )
        if not os.path.exists(json_path):
            with open(json_path, 'w') as f:
                json.dump({'main': current_version_number}, f, indent=4)

    def download_img_files(self):
        """Download the image files if they don't exist in the img directory."""
        contents_of_img_dir = os.listdir(self.directories['img'])
        for img in self.assets.assets_img:
            if img not in contents_of_img_dir:
                img_url = self.assets.img_content_url + img
                try:
                    urllib.request.urlretrieve(
                        img_url, os.path.join(self.directories['img'], img)
                    )
                except:
                    pass

    def download_form_files(self):
        """Download the form files if they don't exist in the form directory."""
        contents_of_form_dir = os.listdir(self.directories['form'])
        for form in self.assets.assets_form:
            if form not in contents_of_form_dir:
                form_url = self.assets.assets_form[form]
                try:
                    urllib.request.urlretrieve(
                        form_url, os.path.join(self.directories['form'], form)
                    )
                except:
                    pass

    def download_update_exe(self):
        """Download update.exe file if it does not exist in the dist directory."""
        update_exe_path = os.path.join(self.directories['dist'], 'update.exe')
        if not os.path.exists(update_exe_path):
            block_size = 1024
            try:
                response = requests.get(self.update_exe_url, stream=True)
                with open(update_exe_path, 'wb') as f:
                    for data in response.iter_content(block_size):
                        f.write(data)
            except:
                pass

    def download_essential_files(self, current_version_number):
        """
        Download all essential files required for the Main app to run properly.
        Instantiates an object called AssetManager to look for required files.
        """
        self.get_program_directory_path()
        self.create_required_directories()
        self.create_current_version_json(current_version_number)
        self.download_img_files()
        self.download_form_files()
        self.download_update_exe()
