import datetime as dt
import json
import os
import sys
import tkinter as tk
import ttkbootstrap as tkb
import time
import win32print

from ttkbootstrap.constants import *

from encryption import MyEncryption


DAYS_EXPIRATION = 1
SECONDS_PER_DAY = 86400
SECONDS_PER_HOUR = 3600
SECONDS_PER_MINUTE = 60


class Reprint(tkb.Frame):
    """
    Interface to reprint filled card payment forms.
    """

    def __init__(self, master, reprint_command):
        super().__init__(master)
        self.pack()
        self.encryption = MyEncryption()
        self.selected_printer = tkb.StringVar()

        self.create_treeview(master)
        self.create_printer_selector(
            master, self._get_printer_list(), self.selected_printer
        )

        self.button = self.create_solid_button(
            master, 'Print', reprint_command
        )

    def create_treeview(self, master):
        """Create ttkbootstrap Treeview object."""

        # Tree container (Treeview + Scrollbar)
        tree_container = tkb.Frame(master)
        tree_container.pack(padx=20, pady=20)

        # Scrollbar
        tree_scroll = tkb.Scrollbar(
            master=tree_container,
            bootstyle='primary-round'
        )
        tree_scroll.pack(side=RIGHT, fill=Y)

        # Define columns
        columns = ('#', 'reference', 'date_created', 'expiration')

        # Create Treeview
        self.my_tree = tkb.Treeview(
            master=tree_container,
            bootstyle='',
            columns=columns,
            show='headings',
            yscrollcommand=tree_scroll.set,
            selectmode='browse',
            height=10
        )
        self.my_tree.pack()

        # Configure scrollbar
        tree_scroll.config(command=self.my_tree.yview)

        # Format columns
        self.my_tree.column('#', anchor=CENTER, width=50)
        self.my_tree.column('reference', anchor=W, width=150)
        self.my_tree.column('date_created', anchor=W, width=135)
        self.my_tree.column('expiration', anchor=W, width=90)

        # Headings
        self.my_tree.heading('#', text='#', anchor=CENTER)
        self.my_tree.heading('reference', text='Reference', anchor=W)
        self.my_tree.heading('date_created', text='Date Created', anchor=W)
        self.my_tree.heading('expiration', text='Expiration', anchor=W)

        # Populate Data
        self._populate_data()

    def create_printer_selector(
            self,
            master,
            printer_list: list,
            variable: tkb.StringVar
    ):
        """Create printer selector drop down menu."""
        selector_container = tkb.Frame(master)
        selector_container.pack(side=LEFT, pady=(0, 20))

        printer_selector_label = tkb.Label(
            master=selector_container,
            text='Select printer:'
        )
        printer_selector_label.pack(side=LEFT, padx=(20, 10))

        self.printer_selector = tkb.Combobox(
            master=selector_container,
            values=printer_list,
            textvariable=variable,
            width=30
        )
        self.printer_selector.pack(side=LEFT)
        variable.set(self._get_default_printer())

    def create_solid_button(self, master, text, command) -> tkb.Button:
        """Create ttkbootstrap Solid Button object."""
        button = tkb.Button(
            master=master,
            text=text,
            command=command,
            width=10
        )
        button.pack(pady=(0, 20))

        return button

    def _get_printer_list(self) -> list:
        """Return a list of all available printers."""
        local_printers = [printer[2] for printer in win32print.EnumPrinters(2)]
        network_printers = [printer[2] for printer in win32print.EnumPrinters(
            win32print.PRINTER_ENUM_CONNECTIONS, None, 1)
        ]

        all_printers = local_printers + network_printers
        return all_printers

    def _get_default_printer(self) -> str:
        """Return the name of the default printer."""
        return win32print.GetDefaultPrinter()

    def _get_program_path(self) -> str:
        """Return the path to the running executable or script."""
        if getattr(sys, 'frozen', False):
            path = os.path.dirname(sys.executable)
        else:
            path = os.path.dirname(os.path.abspath(__file__))

        return path

    def _get_abs_path_to_data_directory(self) -> str:
        """Return the absolute path to the '.data' directory."""
        program_path = self._get_program_path()
        directory_path = '.data'
        directory_abs_path = os.path.join(program_path, directory_path)
        return directory_abs_path

    def _get_formatted_creation_time(self, epoch_ctime: str) -> str:
        """Return the creation time in 12H format."""
        dt_obj = dt.datetime.fromtimestamp(epoch_ctime)
        time_str = dt_obj.strftime('%m/%d/%Y %I:%M %p')
        return time_str

    def _get_epoch_exp_time(self, epoch_ctime: str) -> int:
        epoch_exp_time = int(epoch_ctime) + (DAYS_EXPIRATION * SECONDS_PER_DAY)
        return epoch_exp_time

    def _get_formatted_exp_time(self, epoch_exp_time: int) -> str:
        epoch_current_time = time.time()
        remaining_epoch_time = epoch_exp_time - epoch_current_time
        # days = int(remaining_epoch_time // SECONDS_PER_DAY)
        remaining_epoch_sec = remaining_epoch_time % SECONDS_PER_DAY
        hours = int(remaining_epoch_sec // SECONDS_PER_HOUR)
        remaining_epoch_sec %= SECONDS_PER_HOUR
        minutes = int(remaining_epoch_sec // SECONDS_PER_MINUTE)
        remaining_epoch_sec %= SECONDS_PER_MINUTE
        formatted_exp_time = f'{hours}h {minutes}m {int(remaining_epoch_sec)}s'
        return formatted_exp_time

    def _almost_expired(self, epoch_ctime: str) -> bool:
        """Return True if card payment information is almost expired."""
        epoch_exp_time = self._get_epoch_exp_time(int(epoch_ctime))
        epoch_current_time = time.time()
        remaining_time = epoch_exp_time - epoch_current_time
        if remaining_time < 3600:
            return True
        else:
            return False

    def _decrypt_data(self, data) -> dict:
        """Decrypt data using MyEncryption."""
        decrypted_data = {}
        for ref_id in data:
            decrypted_ref_id = self.encryption.decrypt(ref_id)
            epoch_ctime = data[ref_id]['epoch_ctime']
            decrypted_data[decrypted_ref_id] = {
                'epoch_ctime': epoch_ctime,
                'fields': {}
            }
            fields = data[ref_id]['fields']
            for k, v in fields.items():
                decrypted_k = self.encryption.decrypt(k)
                decrypted_v = self.encryption.decrypt(v)
                decrypted_data[decrypted_ref_id]['fields'][decrypted_k] = decrypted_v

        return decrypted_data

    def _populate_data(self):
        """Populate data from data.json into Treeview."""
        data_dir_path = self._get_abs_path_to_data_directory()
        json_file_path = os.path.join(data_dir_path, 'data.json')
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            decrypted_data = self._decrypt_data(data)
            iid = 1
            for ref_id in decrypted_data:
                epoch_ctime = decrypted_data[ref_id]['epoch_ctime']
                fmt_ctime = self._get_formatted_creation_time(epoch_ctime)
                epoch_exp_time = self._get_epoch_exp_time(epoch_ctime)
                fmt_exp_time = self._get_formatted_exp_time(epoch_exp_time)
                if self._almost_expired(epoch_ctime):
                    tag = 'almost_expired'
                else:
                    tag = ''

                self.my_tree.insert(
                    parent='',
                    index=END,
                    iid=iid,
                    values=(iid, ref_id, fmt_ctime, fmt_exp_time),
                    text=epoch_ctime,
                    tags=tag
                )
                iid += 1

            self.my_tree.tag_configure('almost_expired', foreground='#eb6864')
        except:
            pass

    def _refresh_treeview(self):
        """Refresh items in Treeview window."""
        try:
            current_selection = self.my_tree.focus()
        except:
            pass

        for child in self.my_tree.get_children():
            self.my_tree.delete(child)

        self._populate_data()

        try:
            self.my_tree.selection_set(current_selection)
            self.my_tree.focus(current_selection)
        except:
            pass

    def _get_reference_id(self) -> str:
        """
        Return the reference id of selected item from Treeview window.
        """
        iid = self.my_tree.focus()
        reference_id = self.my_tree.item(iid)['values'][1]
        return reference_id


if __name__ == '__main__':
    reprint_window = tkb.Window(
        title='Reprint',
        themename='litera',
        resizable=(False, False)
    )
    reprint_window.withdraw()
    reprint_window.place_window_center()
    Reprint(reprint_window, None)
    reprint_window.deiconify()

    reprint_window.mainloop()
