import json
import os
import pypdf
import sys
import ttkbootstrap as tkb
import webbrowser

from ttkbootstrap.constants import *
from tkinter.ttk import Style

from refill import Refill
from wrapup import WrapUp
from dropship import DropShipLookUp


class Settings(tkb.Frame):

    def __init__(self, master, cardpayment):
        super().__init__(master, padding=12)
        self.pack(fill=BOTH, expand=YES)
        style = Style()
        style.configure('TLabelframe.Label', font=('', 11, 'bold'))
        style.configure('TRadiobutton', font=('', 10, ''))
        style.configure('TButton', font=('', 9, ''))

        self.cardpayment = cardpayment

        # Settings
        self.current_settings = self._read_settings_json_file()
        self.current_theme = tkb.StringVar()

        self.settings_labelframe = self.create_labelframe(
            master=self,
            text='Settings',
            row=0,
        )

        self.always_top_int_var = tkb.IntVar()
        always_top_btn = self.create_toggle_btn(
            master=self.settings_labelframe,
            text='Always on top',
            command=self.set_always_on_top,
            variable=self.always_top_int_var,
        )
        always_top_btn.pack_configure(anchor='w')

        # Row 2

        settings_row_2 = self.create_inner_frame(
            master=self.settings_labelframe)

        print_blank_form_label = self.create_label(
            master=settings_row_2,
            text='Print blank card payment forms',
        )

        print_blank_form_btn = self.create_solid_btn(
            master=settings_row_2,
            text='Print',
            command=self.open_print_blank_form_window,
            width=7,
        )
        print_blank_form_btn.pack_configure(side=RIGHT, padx=(10, 0))

        # Row 3

        settings_row_3 = self.create_inner_frame(
            master=self.settings_labelframe)

        change_user_label = self.create_label(
            master=settings_row_3,
            text='Change user'
        )

        self.change_user_btn = self.create_solid_btn(
            master=settings_row_3,
            text='Edit',
            command=self.change_user,
            width=7,
            state='disabled'
        )
        self.change_user_btn.pack_configure(side=RIGHT, padx=(10, 0))

        # Mode

        self.mode_str_var = tkb.StringVar()

        mode_labelframe = self.create_labelframe(
            master=self,
            text='Mode',
            row=1,
        )

        payment_mode = self.create_radio_btn(
            master=mode_labelframe,
            text='Payment',
            command=self.check_mode,
            variable=self.mode_str_var,
            value='Payment'
        )

        refill_mode = self.create_radio_btn(
            master=mode_labelframe,
            text='Refill',
            command=self.check_mode,
            variable=self.mode_str_var,
            value='Refill'
        )
        refill_mode.pack_configure(padx=(20, 0))

        # Other apps

        other_apps = self.create_labelframe(
            master=self,
            text='Other Apps',
            row=2
        )

        refill = self.create_solid_btn(
            master=other_apps,
            text='Refill',
            command=self.open_refill_app
        )

        wrapup = self.create_solid_btn(
            master=other_apps,
            text='Wrap Up',
            command=self.open_wrapup_app
        )
        wrapup.pack_configure(padx=(10, 0))

        dropship = self.create_solid_btn(
            master=other_apps,
            text='Drop Ship',
            command=self.open_dropship_app
        )
        dropship.pack_configure(padx=(10, 0))

        # Theme menu
        themes = ['superhero', 'solar', 'darkly', 'cyborg', 'vapor',
                  'cosmo', 'flatly', 'journal', 'litera', 'lumen',
                  'minty', 'pulse', 'sandstone', 'united', 'yeti',
                  'morph', 'simplex', 'cerculean']

        theme_labelframe = self.create_labelframe(
            master=self,
            text='Theme',
            row=3,
        )

        self.themes_combobox = self.create_combobox(
            master=theme_labelframe,
            options=themes,
            default_index=0,
            variable=self.current_theme
        )

        # Info

        info_labelframe = self.create_labelframe(
            master=self,
            text='Info',
            row=4,
        )

        # Row 1

        title_label = self.create_label(
            master=info_labelframe,
            text='My Pharmacy Buddy App'
        )

        title_label.pack_configure(side=TOP)

        version_label = self.create_label(
            master=info_labelframe,
            text=f'{self.cardpayment.root.current_version}'
        )

        version_label.pack_configure(side=TOP)

        link_btn = tkb.Button(
            master=info_labelframe,
            text='michael-hoang.github.io/project-atbs-work/',
            bootstyle='success-link',
            command=self.open_link_btn,
        )

        link_btn.pack(side=TOP)

        # Ok button
        ok_btn = tkb.Button(
            master=self,
            text='OK',
            command=self.save_settings,
            width=10,
            style='TButton'
        )

        ok_btn.grid(row=5, pady=(10, 0))

    def _check_always_on_top(self):
        """Check always on top setting from settings.json. (Used by CardPayment)"""
        if self.current_settings['always_on_top'] == 'yes':
            self.always_top_int_var.set(1)
        else:
            self.always_top_int_var.set(0)

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

    def _get_settings_json_path(self) -> str:
        """Return the absolute path to 'settings.json' file."""
        directory_abs_path = self._get_abs_path_to_data_directory()
        file_name = 'settings.json'
        file_path = os.path.join(directory_abs_path, file_name)
        return file_path

    def _read_settings_json_file(self) -> dict:
        """Read the 'settings.json' file."""
        settings_json_path = self._get_settings_json_path()
        with open(settings_json_path, 'r') as f:
            data = json.load(f)

        return data

    def _set_user_settings(self):
        """Set user settings from settings.json file."""
        self.cardpayment._set_always_on_top_setting(self.current_settings)
        self.cardpayment._set_theme_setting(self.current_settings)

    def _user_setup_window(self, changing_mode=True):
        """Create user setup window."""
        self.setup_window = tkb.Toplevel(self)
        self.setup_window.title('User Setup')
        self.setup_window.config(padx=25, pady=15)
        self.setup_window.resizable(False, False)

        row_1 = self.create_inner_frame(self.setup_window)

        self.create_label(
            master=row_1,
            text='First Name:'
        )

        self.first_name_entry = self.create_short_entry(master=row_1, width=20)

        row_2 = self.create_inner_frame(self.setup_window)

        self.create_label(
            master=row_2,
            text='Last Name:'
        )

        self.last_name_entry = self.create_short_entry(master=row_2, width=20)

        ok_btn = self.create_solid_btn(
            master=self.setup_window,
            text='OK',
            command=lambda: self.user_setup_ok_btn_command(
                changing_mode=changing_mode
            ),
            width=7
        )
        ok_btn.pack_configure(side=BOTTOM, pady=(15, 0))

        self.center_child_to_parent(self.setup_window, self.cardpayment.root)
        self.cardpayment.settings_window.attributes('-disabled', 1)
        self.setup_window.wm_transient(self)
        self.setup_window.deiconify()
        self.first_name_entry.focus()

        self.setup_window.protocol(
            'WM_DELETE_WINDOW', lambda: self.on_closing_user_setup_window(
                self.setup_window
            )
        )
        self.setup_window.bind(
            '<Return>', lambda e: self.user_setup_ok_btn_command(
                changing_mode=changing_mode, e=e
            )
        )
        self.setup_window.bind(
            '<Escape>', lambda e: self.on_closing_user_setup_window(
                self.setup_window, e
            )
        )

    def center_child_to_parent(self, child, parent):
        """Center child window to parent window."""
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_reqwidth()
        parent_height = parent.winfo_reqheight()
        child_width = child.winfo_reqwidth()
        child_height = child.winfo_reqwidth()
        dx = int((parent_width / 2)) - child_width / 2
        dy = int((parent_height / 2)) - child_height / 2
        child.geometry('+%d+%d' % (parent_x + dx, parent_y + dy))

    def on_closing_user_setup_window(self, setup_window, e=None):
        """Enable root window on closing user setup window."""
        self.cardpayment.settings_window.attributes('-disabled', 0)

        if not self.current_settings['user']:
            self.mode_str_var.set('Payment')

        self.setup_window.destroy()

    def on_closing_print_window(self, e):
        """Enable root window on closing the print window."""
        self.cardpayment.settings_window.attributes('-disabled', 0)
        self.print_window.destroy()
        self.cardpayment.settings_window.focus()

    def highlight_print_pages(self, e):
        """Highlight number of pages entry box when clicked."""
        self.num_page_entry.selection_range(0, END)

    def print_blank_forms(self):
        """Print blank payment forms."""
        num_copies = self.num_page_entry.get()
        if not num_copies.isdigit():
            return
        
        program_path = self._get_program_path()
        pdf_file_path = os.path.join(
            program_path, 'assets', 'form', 'cardpayment-blank.pdf'
        )

        pdf_reader = pypdf.PdfReader(open(pdf_file_path, 'rb'))
        num_pages = len(pdf_reader.pages)
        pdf_writer = pypdf.PdfWriter()
        # Add each page to the writer object num_copies times
        for i in range(int(num_copies)):
            for page_num in range(num_pages):
                pdf_writer.add_page(pdf_reader.pages[page_num])

        # Create a temporary file to write the output to
        temp_output_path = os.path.join(program_path, '.tmp', 'blank_form.pdf')
        with open(temp_output_path, 'wb') as out_file:
            pdf_writer.write(out_file)

        # Print the file using the OS print command
        os.startfile(temp_output_path, 'print')
        self.cardpayment.settings_window.attributes('-disabled', 0)
        self.print_window.destroy()

    # Button commands

    def open_print_blank_form_window(self):
        """Open a window to print blank card payment forms."""
        self.print_window = tkb.Toplevel(
            title='Print', resizable=(False, False)
        )
        self.print_window.config(padx=50, pady=20)

        inquiry_label = self.create_label(
            master=self.print_window,
            text='How many pages?'
        )
        inquiry_label.pack_configure(side=TOP)

        self.num_page_entry = self.create_short_entry(
            master=self.print_window,
            width=3,
        )
        self.num_page_entry.pack_configure(side=TOP, pady=(10, 0))
        self.num_page_entry.insert(0, '1')

        print_btn = self.create_solid_btn(
            master=self.print_window,
            text='Print',
            command=self.print_blank_forms,
            width=7
        )
        print_btn.pack_configure(side=TOP, pady=(15, 0))

        self.center_child_to_parent(self.print_window, self.cardpayment.root)
        self.cardpayment.settings_window.attributes('-disabled', 1)
        self.print_window.attributes('-topmost', 1)
        self.num_page_entry.focus()

        self.print_window.bind('<Escape>', self.on_closing_print_window)
        self.num_page_entry.bind('<FocusIn>', self.highlight_print_pages)
        self.print_window.protocol(
            'WM_DELETE_WINDOW', lambda: self.on_closing_print_window(e=None)
        )

    def open_refill_app(self):
        """Instantiate Refill Coordination form app if a user is registered."""
        user = self.current_settings['user']
        if user:
            first = user['first_name']
            last = user['last_name']
            full = f'{first} {last}'
            refill_window = tkb.Toplevel(
                title=f'Refill Coordination - {full}', resizable=(False, False)
            )
            refill_window.withdraw()
            # refill_window.iconbitmap('./assets/img/robot_icon_title.ico')
            Refill(
                self.cardpayment.root, refill_window, wrapup=None, settings=self
            )
            refill_window.place_window_center()
            refill_window.iconbitmap('./assets/img/robot_icon_title.ico')
            refill_window.deiconify()
        else:
            self._user_setup_window(changing_mode=False)

    def open_wrapup_app(self):
        """Instantiate Wrap Up app."""
        wrapup_window = tkb.Toplevel(
            title='Wrap Up Calculator', resizable=(False, False)
        )
        wrapup_window.withdraw()
        wrapup_window.config(padx=10)
        WrapUp(wrapup_window)
        wrapup_window.place_window_center()
        wrapup_window.iconbitmap('./assets/img/robot_icon_title.ico')
        wrapup_window.deiconify()

    def open_dropship_app(self):
        """Instantiate Drop Ship app."""
        dropship_window = tkb.Toplevel(
            title='Drop Ship Look Up', resizable=(False, False)
        )
        dropship_window.withdraw()
        DropShipLookUp(master=dropship_window, root=dropship_window)
        dropship_window.place_window_center()
        dropship_window.iconbitmap('./assets/img/robot_icon_title.ico')
        dropship_window.deiconify()

    def open_link_btn(self):
        """Open link to GitHub page."""
        link = 'https://michael-hoang.github.io/project-atbs-work/'
        webbrowser.open(url=link, new=2, autoraise=True)

    def user_setup_ok_btn_command(self, changing_mode=True, e=None):
        """Confirm user setup and save data to json file."""
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        if first_name and last_name:
            first_name_title = first_name.title()
            last_name_title = last_name.title()
            self.current_settings['user'] = {
                'first_name': first_name_title,
                'last_name': last_name_title,
            }
            self.save_settings(toggle_settings_after_save=False)
            if changing_mode:
                mode = self.current_settings['mode']
                self.mode_str_var.set(mode)
            else:
                self.open_refill_app()
                self.change_user_btn.config(state='normal')

            self.cardpayment.settings_window.attributes('-disabled', 0)
            self.change_user_btn.config(state='normal')
            self.setup_window.destroy()
        elif first_name and not last_name:
            self.first_name_entry.config(style='TEntry')
            self.last_name_entry.config(style='danger.TEntry')
        elif not first_name and last_name:
            self.first_name_entry.config(style='danger.TEntry')
            self.last_name_entry.config(style='TEntry')
        else:
            self.first_name_entry.config(style='danger.TEntry')
            self.last_name_entry.config(style='danger.TEntry')

    def save_settings(self, toggle_settings_after_save=True):
        """Save current user settings to json file."""
        self.current_settings['theme'] = self.current_theme.get()
        settings_json_path = self._get_settings_json_path()
        with open(settings_json_path, 'w') as f:
            data = json.dumps(self.current_settings, indent=4)
            f.write(data)

        if self.current_settings['mode'] == 'Payment':
            self.cardpayment.set_payment_mode()
        elif self.current_settings['mode'] == 'Refill':
            self.cardpayment.set_refill_mode(self.cardpayment.root)

        self._set_user_settings()
        if toggle_settings_after_save:
            self.cardpayment.toggle_settings_window(e=None)

    def set_always_on_top(self):
        """Set always on top setting attribute"""
        if self.always_top_int_var.get() == 0:
            self.current_settings['always_on_top'] = 'no'
        else:
            self.current_settings['always_on_top'] = 'yes'

    def check_mode(self):
        """Check if changing mode conditions are satisfied."""
        selected_mode = self.mode_str_var.get()
        if selected_mode == 'Payment':
            self.current_settings['mode'] = 'Payment'
        elif selected_mode == 'Refill':
            if self.current_settings['user']:
                self.current_settings['mode'] = 'Refill'
                self.change_user_btn.config(state='normal')
            else:
                self._user_setup_window()

    def change_user(self):
        """Change the current user and save to json file."""
        self._user_setup_window()

    # Widget creation methods

    def create_labelframe(self, master, text, row, col=0, sticky='we', padding=True):
        """Create a label frame grid."""
        labelframe = tkb.Labelframe(
            master=master,
            text=text,
            style='TLabelframe.Label',
            padding=15,
        )

        labelframe.grid(row=row, column=col, sticky=sticky, pady=(0, 10))
        if not padding:
            labelframe.grid_configure(pady=0)

        return labelframe

    def create_inner_frame(self, master, grid=False):
        """Create an inner frame."""
        frame = tkb.Frame(master)
        if not grid:
            frame.pack(anchor='w', fill=BOTH, pady=(10, 0))

        return frame

    def create_label(self, master, text, anchor='e',  width=DEFAULT, grid=False):
        """Create a label."""
        label = tkb.Label(
            master=master,
            text=text,
            width=width,
            anchor=anchor,
            font=('', 10, '')
        )
        if not grid:
            label.pack(side=LEFT)

        return label

    def create_toggle_btn(self, master, text: str, command, variable: tkb.IntVar):
        """Create a toggle button ."""
        toggle_btn = tkb.Checkbutton(
            master=master,
            text=text,
            command=command,
            bootstyle='round-toggle',
            variable=variable,
        )

        toggle_btn.pack(side=TOP)
        return toggle_btn

    def create_solid_btn(self, master, text, command, width=DEFAULT, state='normal'):
        """Create a solid button."""
        solid_btn = tkb.Button(
            master=master,
            text=text,
            command=command,
            width=width,
            state=state,
            style='TButton'
        )

        solid_btn.pack(side=LEFT)
        return solid_btn

    def create_radio_btn(self, master, text, command, variable, value):
        """Create a radiobutton."""
        radiobutton = tkb.Radiobutton(
            master=master,
            text=text,
            command=command,
            variable=variable,
            value=value,
            style='TRadiobutton'
        )

        radiobutton.pack(side=LEFT)
        return radiobutton

    def create_combobox(self, master, options: list, default_index: int, variable: tkb.StringVar):
        """Create a combobox drop down menu."""
        combobox = tkb.Combobox(
            master=master,
            values=options,
            textvariable=variable
        )

        combobox.current(default_index)
        combobox.pack(fill=X)

        return combobox

    def create_short_entry(self, master, width=15, padding=True, text_var=None, state='normal'):
        """Create an entry field."""
        entry = tkb.Entry(
            master=master,
            width=width,
            textvariable=text_var,
            state=state
        )

        entry.pack(side=LEFT, padx=(3, 0))
        if not padding:
            entry.pack_configure(padx=0)

        return entry


if __name__ == '__main__':
    from cardpayment import CardPayment

    app = tkb.Window("Settings", "superhero")
    cardpayment = CardPayment(app, app)
    a = Settings(app, cardpayment)
    app.mainloop()
