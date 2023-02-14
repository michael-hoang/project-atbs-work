import tkinter as tk
from tkinter import messagebox, END
import random
import string
import json
from PIL import Image, ImageTk
from encryption import EnDeCrypt
from database import DataBase
import os
import subprocess


BG_COLOR = '#30323D'
GOLD_COLOR = 'gold2'
DARK_GOLD_COLOR = '#8B7536'
BUTTON_COLOR = '#4D5061'
LIGHT_GRAY = '#999999'
FONT = ('Bahnschrift Light', 14, 'normal')


class PasswordManager:
    """A simple representation of a password manager."""

    def __init__(self):
        """Initializes properties of a password manager."""
        self.letters = string.ascii_letters  # abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
        self.numbers = string.digits  # 0123456789
        self.symbols = "!#$%&'()*+,-./:;<=>?@[]^_`{|}~"

        self.EnDeCrypt = EnDeCrypt()

        self.top = tk.Toplevel()
        self.top.withdraw()  # Hides top window from screen.
        self.top.title('Password Manager')
        self.top.config(bg=BG_COLOR, padx=25, pady=10)
        self.top.resizable(width=False, height=False)
        self.lock_icon = tk.PhotoImage(file="assets/img/lock_icon.png")
        self.top.iconphoto(False, self.lock_icon)

        # Settings Window
        self.topSettings_hiddenStatus = True
        self.topSettings = tk.Toplevel(
            master=self.top, bg=BG_COLOR, padx=20, pady=20)
        self._toggle_settngs()
        self.topSettings.title(string='Password Settings')
        setting_icon = tk.PhotoImage(file="assets/img/setting_icon.png")
        self.topSettings.iconphoto(False, setting_icon)
        self.topSettings.resizable(width=False, height=False)
        self.topSettings.protocol(
            "WM_DELETE_WINDOW", func=self._toggle_settngs)

        #### Frame 1 (Letters) ####
        letters_lf = tk.LabelFrame(master=self.topSettings, text='Letters', font=FONT, bg=BG_COLOR,
                                   fg='white', padx=15, pady=15)
        letters_lf.grid(column=0, row=0, sticky='NSEW', padx=(0, 10))

        # numLetters
        numLetters_l = tk.Label(master=letters_lf, text='Characters: ',
                                font=('Bahnschrift Light', 12, 'normal'),
                                bg=BG_COLOR, fg='white')
        numLetters_l.grid(column=0, row=0)
        self.numLetters_e = tk.Entry(master=letters_lf, font=('Bahnschrift Light', 12, 'normal'),
                                     width=3)
        self.numLetters_e.insert(0, '5')
        self.numLetters_e.grid(column=1, row=0, sticky='W')
        self.numLetters = int(self.numLetters_e.get())

        # Lowercase Checkbutton
        self.lowercaseVar = tk.IntVar(value=1)
        lowercase_cb = tk.Checkbutton(master=letters_lf, text='Lowercase',
                                      variable=self.lowercaseVar, onvalue=1, offvalue=0,
                                      bg=BG_COLOR, fg='white', font=(
                                          'Bahnschrift Light', 12, 'normal'),
                                      activebackground=BG_COLOR, activeforeground='white',
                                      selectcolor=BG_COLOR, command=self._lowercase)
        lowercase_cb.grid(
            column=0, row=1, pady=(5, 0), columnspan=2, sticky='W')

        # Uppercase Checkbutton
        self.uppercaseVar = tk.IntVar(value=1)
        uppercase_cb = tk.Checkbutton(master=letters_lf, text='Uppercase',
                                      variable=self.uppercaseVar, onvalue=1, offvalue=0,
                                      bg=BG_COLOR, fg='white', font=(
                                          'Bahnschrift Light', 12, 'normal'),
                                      activebackground=BG_COLOR, activeforeground='white',
                                      selectcolor=BG_COLOR, command=self._uppercase)
        uppercase_cb.grid(column=0, row=2, pady=(5, 0),
                          columnspan=2, sticky='W')

        #### Frame 2 (Numbers) ####
        numbers_lf = tk.LabelFrame(master=self.topSettings, text='Numbers', font=FONT, bg=BG_COLOR,
                                   fg='white', width=200, height=200, padx=15, pady=15)
        numbers_lf.grid(column=1, row=0, sticky='NSEW', padx=(10, 0))

        # numNumbers
        numNumbers_l = tk.Label(master=numbers_lf, text='Characters: ',
                                font=('Bahnschrift Light', 12, 'normal'),
                                bg=BG_COLOR, fg='white')
        numNumbers_l.grid(column=0, row=0)
        self.numNumbers_e = tk.Entry(master=numbers_lf, font=('Bahnschrift Light', 12, 'normal'),
                                     width=3)
        self.numNumbers_e.insert(0, '5')
        self.numNumbers_e.grid(column=1, row=0, sticky='W')
        self.numNumbers = int(self.numNumbers_e.get())

        #### Frame 3 (Symbols) ####
        symbols_lf = tk.LabelFrame(master=self.topSettings, text='Symbols', font=FONT, bg=BG_COLOR,
                                   fg='white', width=200, height=200, padx=15, pady=15)
        symbols_lf.grid(column=0, row=2, columnspan=2,
                        sticky='NSEW', pady=(5, 0))

        # numSymbols
        numSymbols_l = tk.Label(master=symbols_lf, text='Characters: ',
                                font=('Bahnschrift Light', 12, 'normal'),
                                bg=BG_COLOR, fg='white')
        numSymbols_l.grid(column=0, row=0)
        self.numSymbols_e = tk.Entry(master=symbols_lf, font=('Bahnschrift Light', 12, 'normal'),
                                     width=3)
        self.numSymbols_e.insert(0, '5')
        self.numSymbols_e.grid(column=1, row=0, columnspan=2, sticky='W')
        self.numSymbols = int(self.numSymbols_e.get())

        # ListBox (Include Symbols)
        include_l = tk.Label(master=symbols_lf, text='Include', font=(
            'Bahnschrift Light', 12, 'normal'),
            bg=BG_COLOR, fg='white', justify='center')
        include_l.grid(column=0, row=1, pady=(5, 0), padx=(10, 0))
        self.listBox_in = tk.Listbox(master=symbols_lf, justify='center',
                                     font=('Bahnschrift Light', 12, 'normal'), width=10, height=8,
                                     selectmode='extended', selectbackground=LIGHT_GRAY, selectforeground='white')
        self.listBox_in.grid(column=0, row=2, rowspan=2,
                             sticky='E', padx=(10, 0))

        for symbol in self.symbols:
            self.listBox_in.insert(END, symbol)

        include_scrollbar = tk.Scrollbar(master=symbols_lf)
        include_scrollbar.grid(column=1, row=2, rowspan=2, sticky='NSW')
        self.listBox_in.config(yscrollcommand=include_scrollbar.set)
        include_scrollbar.config(command=self.listBox_in.yview)

        # >> Button
        excludeButton = tk.Button(master=symbols_lf, text='>>', font=(
            'Bahnschrift Light', 12, 'normal'), bg=BUTTON_COLOR, fg='white',
            borderwidth=0, activebackground=GOLD_COLOR, command=self._exclude_symbol)
        excludeButton.grid(column=2, row=2, ipadx=10, padx=10)
        excludeButton.bind('<Enter>', self.pointerEnter)
        excludeButton.bind('<Leave>', self.pointerLeave)
        # << Button
        includeButton = tk.Button(master=symbols_lf, text='<<', font=(
            'Bahnschrift Light', 12, 'normal'), bg=BUTTON_COLOR, fg='white',
            borderwidth=0, activebackground=GOLD_COLOR, command=self._include_symbol)
        includeButton.grid(column=2, row=3, ipadx=10, padx=10)
        includeButton.bind('<Enter>', self.pointerEnter)
        includeButton.bind('<Leave>', self.pointerLeave)

        # ListBox (Exclude Symbols)
        exclude_l = tk.Label(master=symbols_lf, text='Exclude', font=(
            'Bahnschrift Light', 12, 'normal'),
            bg=BG_COLOR, fg='white', justify='center')
        exclude_l.grid(column=3, row=1, pady=(5, 0))
        self.listBox_ex = tk.Listbox(master=symbols_lf, justify='center',
                                     font=('Bahnschrift Light', 12, 'normal'), width=10, height=8,
                                     selectmode='extended', selectbackground=LIGHT_GRAY, selectforeground='white')
        self.listBox_ex.grid(column=3, row=2, rowspan=2, sticky='E')

        exclude_scrollbar = tk.Scrollbar(master=symbols_lf)
        exclude_scrollbar.grid(column=4, row=2, rowspan=2, sticky='NSW')
        self.listBox_ex.config(yscrollcommand=exclude_scrollbar.set)
        exclude_scrollbar.config(command=self.listBox_ex.yview)

        # Always Top Checkbutton
        self.alwaysTopVar = tk.IntVar()
        self.always_top_cb = tk.Checkbutton(self.top, text='Always on top',
                                            variable=self.alwaysTopVar, onvalue=1, offvalue=0,
                                            bg=BG_COLOR, fg='white', font=(
                                                'Bahnschrift Light', 10, 'normal'),
                                            activebackground=BG_COLOR, activeforeground='white',
                                            selectcolor=BG_COLOR, command=self.always_top)
        self.always_top_cb.grid(
            column=0, row=0, columnspan=2, sticky='NW', pady=(10, 0))

        # Lock Image Button
        self.lock_img = tk.PhotoImage(file='assets/img/lock_button.png')
        self.lockButton = tk.Button(master=self.top, image=self.lock_img, bg=BG_COLOR,
                                    activebackground=BG_COLOR, borderwidth=0, command=lambda: self.open_database(self.top))
        self.lockButton.grid(column=2, row=0, pady=(20, 10))

        # Website Label & Entry
        self.websiteLabel = tk.Label(master=self.top, text='Website:', bg=BG_COLOR,
                                     fg='white', font=FONT)
        self.websiteLabel.grid(column=1, row=1, sticky='E')
        self.websiteEntry = tk.Entry(master=self.top, width=30, font=FONT)
        self.websiteEntry.grid(column=2, row=1, padx=5, pady=4)
        self.websiteEntry.focus()

        # Username/Email Label & Entry
        self.userLabel = tk.Label(master=self.top, text='Username/Email:', bg=BG_COLOR,
                                  fg='white', font=FONT)
        self.userLabel.grid(column=1, row=2, sticky='E')
        self.userEntry = tk.Entry(master=self.top, width=30, font=FONT)
        self.userEntry.grid(column=2, row=2, padx=5, pady=4)

        # Password Label & Entry
        self.passLabel = tk.Label(master=self.top, text='Password:', bg=BG_COLOR,
                                  fg='white', font=FONT)
        self.passLabel.grid(column=1, row=3, sticky='E')
        self.passEntry = tk.Entry(
            master=self.top, width=30, font=FONT, show='*')
        self.passEntry.grid(column=2, row=3, padx=5, pady=4)

        # Search Button
        self.search_img = Image.open(fp='assets/img/search.png')
        self.search_resized_img = self.search_img.resize((25, 25))
        self.new_search_img = ImageTk.PhotoImage(self.search_resized_img)
        self.searchButton = tk.Button(master=self.top, image=self.new_search_img, bg=BG_COLOR,
                                      activebackground=BG_COLOR, borderwidth=0,
                                      command=lambda: self.search_login(event=None))
        self.searchButton.grid(column=3, row=1, padx=5)

        # Dice Button
        self.dice_img = Image.open(fp='assets/img/dice.png')
        self.dice_resized_img = self.dice_img.resize((25, 25))
        self.new_dice_img = ImageTk.PhotoImage(self.dice_resized_img)
        self.diceButton = tk.Button(master=self.top, image=self.new_dice_img, bg=BG_COLOR,
                                    activebackground=BG_COLOR, borderwidth=0,
                                    command=self.generate_random_password)
        self.diceButton.grid(column=3, row=3, padx=5)

        # Settings Button
        self.setting_img = Image.open(fp='assets/img/setting.png')
        self.setting_resized_img = self.setting_img.resize((25, 25))
        self.new_setting_img = ImageTk.PhotoImage(self.setting_resized_img)
        self.settingButton = tk.Button(master=self.top, image=self.new_setting_img, bg=BG_COLOR,
                                       activebackground=BG_COLOR, borderwidth=0,
                                       command=self._toggle_settngs)
        self.settingButton.grid(
            column=0, row=3, columnspan=2, sticky='E', padx=(0, 100))

        # Add Button
        self.addButton = tk.Button(master=self.top, text='Add', bg=BUTTON_COLOR,
                                   fg='white', font=('Bahnschrift Light', 12, 'normal'),
                                   borderwidth=0, width=33, activebackground=GOLD_COLOR,
                                   command=lambda: self.save_login_info(event=None))
        self.addButton.grid(column=2, row=4, pady=(4, 20))

        # Eye button
        eye_img = Image.open(fp='assets/img/eye.png')
        eye_resized_img = eye_img.resize((25, 25))
        self.new_eye_img = ImageTk.PhotoImage(eye_resized_img)
        self.eyeButton = tk.Button(master=self.top, image=self.new_eye_img, bg=BG_COLOR,
                                   activebackground=BG_COLOR, borderwidth=0)
        self.eyeButton.grid(column=3, row=4, sticky='N', pady=(5, 0))
        self.eyeButton.bind('<ButtonPress-1>', self._show_password)
        self.eyeButton.bind('<ButtonRelease-1>', self._hide_password)

        # Center top window to screen
        self.top.update_idletasks()
        win_width = self.top.winfo_reqwidth()
        win_height = self.top.winfo_reqheight()
        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        x = int(screen_width/2 - win_width/2)
        y = int(screen_height/2 - win_height/2)
        self.top.geometry(f"{win_width}x{win_height}+{x}+{y}")
        self.top.deiconify()  # Makes top window visible again.
        self.websiteEntry.focus()

        self.topSettings.bind('<Escape>', self.hide_settings)
        self.top.bind('<Return>', func=self.search_login)
        self.top.bind('<Shift-Return>', func=self.save_login_info)
        self.top.bind('<Delete>', func=self._clear_all)
        self.addButton.bind('<Enter>', self.pointerEnter)
        self.addButton.bind('<Leave>', self.pointerLeave)

        self._update_topWindow_entries()
        # Exit after 600 seconds (10 minutes)
        self.seconds = 600
        self._pwmCountdown(seconds=self.seconds)

    def open_database(self, top):
        """Open login database TopLevel window."""
        try:
            self.db = DataBase(root=top)
        except KeyError:
            messagebox.showerror(parent=self.top, title='Key Missing',
                                 message="Key is missing in 'data.json'. Use Authenticator to setup PIN/Phrase and reset key.")
        except FileNotFoundError:
            messagebox.showerror(parent=self.top, title='File Missing',
                                 message="The file 'data.json' is missing. Use Authenticator to setup PIN/Phrase.")

    def _exclude_symbol(self):
        """Add selected symbol to Exclude listbox."""
        to_exclude = self.listBox_in.curselection()
        for line_number in to_exclude:
            symbol = self.listBox_in.get(line_number)
            self.listBox_ex.insert(END, symbol)

        rev_to_exclude = reversed(to_exclude)
        for line_number in rev_to_exclude:
            self.listBox_in.delete(line_number)

        self.symbols = ''
        updated_to_include = self.listBox_in.get(0, END)
        for symbol in updated_to_include:
            self.symbols += symbol

    def _include_symbol(self):
        """Add selected symbol to Include listbox."""
        to_include = self.listBox_ex.curselection()
        for line_number in to_include:
            symbol = self.listBox_ex.get(line_number)
            self.listBox_in.insert(END, symbol)

        rev_to_include = reversed(to_include)
        for line_number in rev_to_include:
            self.listBox_ex.delete(line_number)

        self.symbols = ''
        updated_to_include = self.listBox_in.get(0, END)
        for symbol in updated_to_include:
            self.symbols += symbol

    def always_top(self):
        """top window always display on top."""
        if self.alwaysTopVar.get() == 1:
            self.top.attributes('-topmost', 1)
        elif self.alwaysTopVar.get() == 0:
            self.top.attributes('-topmost', 0)

    def generate_random_password(self):
        """Generates a random password."""
        rand_pass_list = []
        try:
            [rand_pass_list.append(random.choice(self.letters))
             for _ in range(self.numLetters)]
        except:
            pass

        try:
            [rand_pass_list.append(random.choice(self.numbers))
             for _ in range(self.numNumbers)]
        except:
            pass

        try:
            [rand_pass_list.append(random.choice(self.symbols))
             for _ in range(self.numSymbols)]
        except:
            pass

        random.shuffle(rand_pass_list)
        rand_pass = "".join(rand_pass_list)
        self.passEntry.delete(0, END)
        self.passEntry.insert(0, rand_pass)
        self.passEntry.clipboard_clear()
        self.passEntry.clipboard_append(rand_pass)

    def _show_password(self, event):
        """Show password in the password entry field."""
        self.passEntry.config(show='')

    def _hide_password(self, event):
        """Hide password in the password entry field."""
        self.passEntry.config(show='*')

    def save_login_info(self, event):
        """Writes login info to data.json."""
        website = self.websiteEntry.get().lower().strip()
        username = self.userEntry.get().strip()
        password = self.passEntry.get().strip()

        enWebsite = self.EnDeCrypt.encrypt(website)
        enUsername = self.EnDeCrypt.encrypt(username)
        enPassword = self.EnDeCrypt.encrypt(password)

        loginInfo = {
            enWebsite: {
                'username': enUsername,
                'password': enPassword,
            }
        }

        try:
            with open('.data/data.json', 'r') as f:
                data = json.load(f)
                if not website or not username or not password:
                    messagebox.showwarning(parent=self.top, title='Error',
                                           message='Please do not leave any fields empty.')
                    return
                elif enWebsite in data:
                    self.top.bell()
                    update_existing_info = messagebox.askyesno(
                        parent=self.top, title='Warning',
                        message=f"There is already a password saved for {website.title()}.\nWould you like to overwrite?")
                    if update_existing_info:
                        pass
                    else:
                        return

                data.update(loginInfo)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            if not website or not username or not password:
                messagebox.showwarning(parent=self.top, title='Error',
                                       message='Please do not leave any fields empty.')
                return

            data = loginInfo

        folder = '.data'
        programPath = os.path.dirname(__file__)
        folderAbsPath = os.path.join(programPath, folder)
        folderExist = os.path.exists(folderAbsPath)
        if not folderExist:
            os.mkdir(folderAbsPath)
            subprocess.call(["attrib", "+h", folderAbsPath]) # hidden directory

        with open('.data/data.json', 'w') as f:
            json.dump(obj=data, fp=f, indent=4)

        self._clear_all(event)

    def search_login(self, event):
        """Search website in database for login info."""
        website = self.websiteEntry.get().strip()
        enWebsite = self.EnDeCrypt.encrypt(website.lower())

        try:
            with open(file='.data/data.json', mode='r') as f:
                data = json.load(fp=f)
                if enWebsite in data:
                    self._show_login(data=data, website=enWebsite, event=event)
                elif not website:
                    messagebox.showwarning(parent=self.top, title='Error',
                                           message=f'Please enter a website to search.')
                    self._clear_all(event)
                else:
                    messagebox.showwarning(parent=self.top, title='Error',
                                           message=f'{website.title()} is not found in the database.')
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            messagebox.showwarning(parent=self.top, title='Error',
                                   message='No data found.')
            self._clear_all(event)

    def _show_login(self, data, website, event):
        """Display login info."""

        def _countdown(seconds):
            """Countdown timer to exit TopLevel window."""
            top.attributes('-topmost', 1)
            if seconds > 0:
                timerLabel.config(text=f'Closing in {seconds}')
                top.after(1000, _countdown, seconds-1)
            else:
                top.destroy()

        def _copy_username():
            """Copy username from TopLevel to clipboard."""
            topUsernameEntry.clipboard_clear()
            topUsernameEntry.clipboard_append(deUsername)

        def _copy_password():
            """Copy password from TopLevel to clipboard."""
            topPasswordEntry.clipboard_clear()
            topPasswordEntry.clipboard_append(dePassword)

        def _show_topPassword(event):
            """Show password in the password entry field."""
            topPasswordEntry.config(show='')

        def _hide_topPassword(event):
            """Hide password in the password entry field."""
            topPasswordEntry.config(show='*')

        def _escape(event):
            """Close 'Show Login' TopLevel window."""
            top.destroy()

        username = data[website]['username']
        password = data[website]['password']
        deUsername = self.EnDeCrypt.decrypt(username)
        dePassword = self.EnDeCrypt.decrypt(password)
        deWebsite = self.EnDeCrypt.decrypt(website)

        top = tk.Toplevel(master=self.top, bg=BG_COLOR, padx=20, pady=20)
        top.withdraw()  # Hides TopLevel window from screen.
        top.title(f'{deWebsite.title()}')
        top.iconphoto(False, self.lock_icon)
        top.attributes('-topmost', 1)
        top.grab_set()
        top.focus()
        top.resizable(width=False, height=False)
        self._clear_all(event)

        # TopLevel Website Label
        topWebsiteLabel = tk.Label(master=top, text=f'{deWebsite.title()} Account',
                                   font=('Bahnschrift Light', 18, 'normal'),
                                   bg=BG_COLOR, fg='white')
        topWebsiteLabel.grid(column=0, row=0, sticky='W',
                             columnspan=2, pady=(0, 20))

        # TopLevel Username Label
        topUsernameLabel = tk.Label(master=top, text='Username: ',
                                    font=('Bahnschrift Light', 14, 'normal'),
                                    bg=BG_COLOR, fg='white')
        topUsernameLabel.grid(column=0, row=1, sticky='E', pady=(0, 10))

        # TopLevel Username Entry
        topUsernameEntry = tk.Entry(master=top, font=('Bahnschrift Light', 14, 'normal'),
                                    bg=BG_COLOR, fg='white')
        topUsernameEntry.grid(column=1, row=1, sticky='W', pady=(0, 10))
        topUsernameEntry.delete(0, END)
        topUsernameEntry.insert(index=0, string=deUsername)
        topUsernameEntry.config(state='disabled', disabledbackground=BG_COLOR,
                                disabledforeground=LIGHT_GRAY)

        # TopLevel Username Copy Button
        topUsernameCopyButton = tk.Button(master=top, text='Copy',
                                          font=('Bahnschrift Light',
                                                12, 'normal'),
                                          bg=BUTTON_COLOR, fg='white', borderwidth=0,
                                          activebackground=GOLD_COLOR, command=_copy_username)
        topUsernameCopyButton.grid(column=2, row=1, padx=(10, 0), pady=(0, 10))

        # TopLevel Password Label
        topPasswordLabel = tk.Label(master=top, text='Password: ',
                                    font=('Bahnschrift Light', 14, 'normal'),
                                    bg=BG_COLOR, fg='white')
        topPasswordLabel.grid(column=0, row=2, sticky='E')

        # TopLevel Password Entry
        topPasswordEntry = tk.Entry(master=top, font=('Bahnschrift Light', 14, 'normal'),
                                    bg=BG_COLOR, fg='white', show='*')
        topPasswordEntry.grid(column=1, row=2, sticky='W')
        topPasswordEntry.delete(0, END)
        topPasswordEntry.insert(index=0, string=dePassword)
        topPasswordEntry.config(state='disabled', disabledbackground=BG_COLOR,
                                disabledforeground=LIGHT_GRAY)

        # TopLevel Password Copy Button
        topPasswordCopyButton = tk.Button(master=top, text='Copy',
                                          font=('Bahnschrift Light',
                                                12, 'normal'),
                                          bg=BUTTON_COLOR, fg='white', borderwidth=0,
                                          activebackground=GOLD_COLOR, command=_copy_password)
        topPasswordCopyButton.grid(column=2, row=2, padx=(10, 0))

        # TopLevel Eye button
        topEyeButton = tk.Button(master=top, image=self.new_eye_img, bg=BG_COLOR,
                                 activebackground=BG_COLOR, borderwidth=0)
        topEyeButton.grid(column=2, row=3, pady=(20, 0))
        topEyeButton.bind('<ButtonPress-1>', _show_topPassword)
        topEyeButton.bind('<ButtonRelease-1>', _hide_topPassword)

        # TopLevel Timer Label
        seconds = 10
        timerLabel = tk.Label(master=top, text=f'Closing in {seconds}', bg=BG_COLOR,
                              fg='white', font=('Bahnschrift Light', 12, 'normal'))
        timerLabel.grid(column=0, row=3, columnspan=3, pady=(20, 0))

        # Center top window to screen
        top.update_idletasks()
        x = self.top.winfo_x()
        y = self.top.winfo_y()
        topWidth = self.top.winfo_reqwidth()
        topHeight = self.top.winfo_reqheight()
        topShowLoginWidth = top.winfo_reqwidth()
        topShowLoginHeight = top.winfo_reqheight()
        dx = int((topWidth/2) - (topShowLoginWidth/2))
        dy = int((topHeight/2) - (topShowLoginHeight/2))
        top.geometry('+%d+%d' % (x + dx, y + dy))
        top.deiconify()  # Makes TopLevel window visible again.

        top.bind('<Escape>', func=_escape)
        topUsernameCopyButton.bind('<Enter>', self.pointerEnter)
        topUsernameCopyButton.bind('<Leave>', self.pointerLeave)
        topPasswordCopyButton.bind('<Enter>', self.pointerEnter)
        topPasswordCopyButton.bind('<Leave>', self.pointerLeave)

        _countdown(seconds)

    def _clear_all(self, event):
        """Clear all entry fields and set focus to websiteEntry."""
        self.websiteEntry.delete(0, END)
        self.userEntry.delete(0, END)
        self.passEntry.delete(0, END)
        self.websiteEntry.focus()

    def _lowercase(self):
        """Allow lowercase letters for random password generator."""
        lowercase_letters = 'abcdefghijklmnopqrstuvwxyz'
        if self.lowercaseVar.get() == 1:
            for letter in lowercase_letters:
                if letter not in self.letters:
                    self.letters += letter
        elif self.lowercaseVar.get() == 0:
            for letter in lowercase_letters:
                if letter in self.letters:
                    self.letters = self.letters.replace(letter, '')

    def _uppercase(self):
        """Allow uppercase letters for random password generator."""
        uppercase_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if self.uppercaseVar.get() == 1:
            for letter in uppercase_letters:
                if letter not in self.letters:
                    self.letters += letter
        elif self.uppercaseVar.get() == 0:
            for letter in uppercase_letters:
                if letter in self.letters:
                    self.letters = self.letters.replace(letter, '')

    def _toggle_settngs(self):
        """Toogles TopLevel settings menu for random password generator."""
        if self.topSettings_hiddenStatus:
            self.topSettings.withdraw()
            self.topSettings_hiddenStatus = False
            self.top.lift()
            self.top.attributes('-disabled', 0)
            self.top.focus_force()

        else:
            # Center settings window to top screen
            self.topSettings.update_idletasks()
            x = self.top.winfo_x()
            y = self.top.winfo_y()
            topWidth = self.top.winfo_reqwidth()
            topHeight = self.top.winfo_reqheight()
            topSettingWidth = self.topSettings.winfo_reqwidth()
            topSettingHeight = self.topSettings.winfo_reqheight()
            dx = int((topWidth/2) - (topSettingWidth/2))
            dy = int((topHeight/2) - (topSettingHeight/2))
            self.topSettings.geometry('+%d+%d' % (x + dx, y + dy))

            self.topSettings_hiddenStatus = True
            self.top.attributes('-disabled', 1)
            self.topSettings.wm_transient(self.top)
            self.topSettings.attributes('-topmost', 1)
            self.topSettings.deiconify()

    def _update_topWindow_entries(self):
        """Recursively updates all settings for top window."""
        try:
            self.numLetters = int(self.numLetters_e.get())
        except:
            self.numLetters = 0

        try:
            self.numNumbers = int(self.numNumbers_e.get())
        except:
            self.numNumbers = 0

        try:
            self.numSymbols = int(self.numSymbols_e.get())
        except:
            self.numSymbols = 0

        self.top.after(50, self._update_topWindow_entries)

    def pointerEnter(self, event):
        """Highlight button on mouse hover."""
        event.widget['bg'] = DARK_GOLD_COLOR

    def pointerLeave(self, event):
        """Remove highlight from button when mouse leave button."""
        event.widget['bg'] = BUTTON_COLOR

    def _pwmCountdown(self, seconds):
        """Automatically closes Password Manager after # of seconds."""
        if seconds > 0:
            self.top.after(1000, self._pwmCountdown, seconds-1)
        else:
            try:
                self.db.destroy()
            except AttributeError:
                pass
            self.top.destroy()

    def hide_settings(self, event):
        """Press ESC to hide settings window."""
        if self.topSettings_hiddenStatus:
            self.topSettings.withdraw()
            self.topSettings_hiddenStatus = False
            self.top.lift()
            self.top.attributes('-disabled', 0)
            self.top.focus_force()


if __name__ == '__main__':
    pw = PasswordManager()
    pw.top.mainloop()
