"""This module contains a class that represents an authenticator."""

import tkinter as tk
from tkinter import messagebox, END
from PIL import Image, ImageTk
import random
import json
import os
import sys
from encryption import EnDeCrypt
import subprocess


FONT = ('Bahnschrift Light', 12, 'normal')
BG_COLOR = '#30323D'
GOLD_COLOR = 'gold2'
DARK_GOLD_COLOR = '#8B7536'
BUTTON_COLOR = '#4D5061'
LIGHT_GRAY = '#999999'


class Authenticator:
    """This class provides verification for users to access various apps."""

    def __init__(self):
        """Initialize encryption, GUI, and check credentials."""
        self.endecrypt = EnDeCrypt()
        self.top = tk.Toplevel(bg=BG_COLOR, padx=25, pady=20)
        self.top.title('Authentication')
        self.top.withdraw()
        self.top.resizable(width=False, height=False)
        self.authentication_icon = tk.PhotoImage(
            file='assets/img/authentication_icon.png')
        self.top.iconphoto(False, self.authentication_icon)

        self.instructLabel = tk.Label(
            self.top, text='Enter your PIN/Phrase.', bg=BG_COLOR, fg='white', font=('Bahnschrift Light', 14, 'normal'))
        self.instructLabel.grid(column=0, row=0, columnspan=2, pady=(0, 10))
        self.keyEntry = tk.Entry(self.top, font=FONT, width=24, show='*')
        self.keyEntry.grid(column=0, row=2)
        self.okButton = tk.Button(
            self.top, text='OK', command=lambda: self.confirmation('event'), width=10, font=FONT, bg=BUTTON_COLOR, fg='white', borderwidth=0, activebackground=GOLD_COLOR)
        self.okButton.grid(column=0, row=3, pady=(15, 0))

        # Center window to screen
        self.top.update_idletasks()
        win_width = self.top.winfo_reqwidth()
        win_height = self.top.winfo_reqheight()
        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        x = int(screen_width/2 - win_width/2)
        y = int(screen_height/2 - win_width/2)
        self.top.geometry(f"{win_width}x{win_height}+{x}+{y}")

        self.secretKey = ''
        self.shiftNum = ''
        self.token = ''
        self.isVerified = False
        self.cred = ''
        self._authenticate()

        self.top.bind('<Return>', self.confirmation)
        self.top.bind('<Escape>', self.close_verification_window)
        self.okButton.bind('<Enter>', self.pointerEnter)
        self.okButton.bind('<Leave>', self.pointerLeave)

    def _authenticate(self):
        """Start authentication or prompt user to create secret key."""
        self.cred = self._check_for_existing_credential()
        if self.cred:
            self.top.deiconify()
            self.keyEntry.focus()
            self.top.attributes('-topmost', True)
        else:
            self._generate_token()
            self.shiftNum = #[code to generate random a random shift number]
            self._create_secretkey()

    def _check_for_existing_credential(self) -> bool:
        """Check for existing crendential (data.json and auth.key)."""
        try:
            with open('.cred/auth.key', 'r') as f:
                cred1 = f.read()
        except FileNotFoundError:
            cred1 = False

        try:
            with open('.data/data.json', 'r') as f:
                data = json.load(f)
                # if data.json found, check if key exists
                checkKey = data['key']

            with open('.data/data.json', 'r') as f:
                cred2 = f.read()

        except FileNotFoundError:
            cred2 = False

        except KeyError:
            messagebox.showerror(parent=self.top, title='Key Missing',
                                 message="Key is missing in 'data.json'. Set up"
                                 " a new PIN/Phrase to generate a new key. Any stored data will"
                                 " be overwritten. Proceed with caution!")
            return False

        # error handling for empty data.json or invalid data in data.json
        except (json.decoder.JSONDecodeError, TypeError):
            return False

        if cred1 and cred2:
            # check for corrupted key
            try:
                decryptedKey = self._decrypt_token()
            except ValueError:
                messagebox.showerror(parent=self.top, title='Corrupted Key', message="Key is corrupted "
                                     "in 'data.json' or 'auth.key'. Set up a new PIN/Phrase to generate a new key. All "
                                     "stored data will be overwritten. Proceed with caution!")
                return False

            return True
        elif cred1 and not cred2:
            message = "Path '.cred/auth.key' was detected, but path '.data/data.json' is missing."\
                "\n\nBoth paths are needed to access stored data. Setting up a new Pin/Phrase"\
                " will overwrite any existing data. Proceed with caution!"
            messagebox.showwarning(
                parent=self.top, title='Missing File', message=message)
            return False
        elif not cred1 and cred2:
            message = "Path '.data/data.json' was detected, but path '.cred/auth.key' is missing."\
                "\n\nBoth paths are needed to access stored data. Setting up a new Pin/Phrase"\
                " will overwrite any existing data. Proceed with caution!"
            messagebox.showwarning(
                parent=self.top, title='Missing File', message=message)
            return False
        else:
            return False

    def _generate_token(self, size=150):
        """Generate a random token of default size 100."""
        characters = #[available characters to create token]
        token = ''
        for _ in range(size):
            randChar = random.choice(characters)
            token += randChar

        self.token = token

    def _create_secretkey(self):
        """Prompt user to create a secret key."""

        def _verifySecretKey(event):
            """Verify if user re-enters secret key correctly."""
            key1 = keyEntry.get()
            key2 = verifyKeyEntry.get()
            if key1 == '' and key2 == '':
                messagebox.showerror(parent=createKeyWin, title='Error',
                                     message='Authentication is required to use Password Manager.')
            elif key1 == key2:
                self.secretKey = key1
                messagebox.showinfo(parent=createKeyWin, title='Success', message='Your PIN/Phrase has been'
                                    ' created. This will be your secret key to access Password Manager. Don\'t lose it!')
                encryptedToken = self._encrypt_token()
                self._export_token(token=encryptedToken)
                self._authenticate()
                createKeyWin.destroy()
            else:
                messagebox.showerror(parent=createKeyWin, title='Error', message='Your PIN/Phrase did not'
                                     ' match. Please try again.')
                verifyKeyEntry.focus()

        def showSecretKey(event):
            """Reveal PIN/Phrase to user."""
            keyEntry.config(show='')
            verifyKeyEntry.config(show='')

        def hideSecretKey(event):
            """Hide PIN/Phrase from user."""
            keyEntry.config(show='*')
            verifyKeyEntry.config(show='*')

        def clearEntry(event):
            """Delete all entries."""
            keyEntry.delete(0, END)
            verifyKeyEntry.delete(0, END)
            keyEntry.focus()

        warning_message = 'Create a PIN or phrase.\n\nWARNING: This will be'\
            ' your secret key. Keep it safe. You will not be able'\
            ' to recover your saved accounts and passwords if you lose'\
            ' it.'
        createKeyWin = tk.Toplevel(self.top, padx=20, pady=20, bg=BG_COLOR)
        createKeyWin.title('Setup PIN/Phrase')
        createKeyWin.withdraw()
        createKeyWin.resizable(width=False, height=False)
        createKeyWin.iconphoto(False, self.authentication_icon)
        # Pin/Phrase creation window jumps to the front.
        createKeyWin.lift()
        createKeyWin.attributes('-topmost', True)
        createKeyWin.attributes('-topmost', False)
        
        warningLabel = tk.Label(
            createKeyWin, text=warning_message, justify='left', font=FONT, wraplength=400, bg=BG_COLOR, fg='white')
        warningLabel.grid(column=0, row=0, columnspan=2,
                          sticky='EW', padx=10, pady=(0, 10))
        enterKeyLabel = tk.Label(
            createKeyWin, text='Enter PIN/Phrase: ', font=FONT, bg=BG_COLOR, fg='white')
        enterKeyLabel.grid(column=0, row=1, sticky='E', pady=(10))
        keyEntry = tk.Entry(createKeyWin, font=FONT, show='*')
        keyEntry.grid(column=1, row=1, pady=(10, 5))
        verifyKeyLabel = tk.Label(
            createKeyWin, text='Re-Enter PIN/Phrase: ', font=FONT, bg=BG_COLOR, fg='white')
        verifyKeyLabel.grid(column=0, row=2, sticky='E')
        verifyKeyEntry = tk.Entry(createKeyWin, font=FONT, show='*')
        verifyKeyEntry.grid(column=1, row=2, pady=(0, 10))
        okButton = tk.Button(createKeyWin, text='OK',
                             font=FONT, width=10, bg=BUTTON_COLOR, fg='white', borderwidth=0, activebackground=GOLD_COLOR, command=lambda: _verifySecretKey('event'))
        okButton.grid(column=1, row=3, pady=(10, 0))
        # Eye button
        createKeyWin.eyeImage_open = Image.open('assets/img/eye.png')
        createKeyWin.eyeImage_resized = createKeyWin.eyeImage_open.resize(
            (25, 25))
        createKeyWin.eyeImage = ImageTk.PhotoImage(
            createKeyWin.eyeImage_resized)
        eyeButton = tk.Button(createKeyWin, image=createKeyWin.eyeImage,
                              bg=BG_COLOR, activebackground=BG_COLOR, borderwidth=0)
        eyeButton.grid(column=2, row=1, rowspan=2)
        eyeButton.bind('<ButtonPress-1>', showSecretKey)
        eyeButton.bind('<ButtonRelease-1>', hideSecretKey)

        createKeyWin.bind('<Return>', _verifySecretKey)
        createKeyWin.bind('<Delete>', clearEntry)
        createKeyWin.protocol('WM_DELETE_WINDOW', self.top.destroy)
        # Center window to screen
        createKeyWin.update_idletasks()
        win_width = createKeyWin.winfo_reqwidth()
        win_height = createKeyWin.winfo_reqheight()
        screen_width = createKeyWin.winfo_screenwidth()
        screen_height = createKeyWin.winfo_screenheight()
        x = int(screen_width/2 - win_width/2)
        y = int(screen_height/2 - win_width/2)
        createKeyWin.geometry(f"{win_width}x{win_height}+{x}+{y}")
        createKeyWin.deiconify()
        keyEntry.focus()

        okButton.bind('<Enter>', self.pointerEnter)
        okButton.bind('<Leave>', self.pointerLeave)

    def _encrypt_token(self) -> str:
        """Encrypt and embed secret key inside token. Attach unencrypted shift number at the end of encrypted token."""
        encryptedKey = self.endecrypt.encrypt(
            message=self.secretKey, shiftNum=self.shiftNum)
        embeddedToken = #[code to embed token]
        encryptedKeyLen = len(encryptedKey)
        encryptedToken = self.endecrypt.encrypt(
            message=embeddedToken, shiftNum=self.shiftNum)
        return encryptedToken

    def _export_token(self, token: str):
        """Separate encrypted token into two parts and write each part to data.json and auth.key."""
        tokenPiece1 = token[:int(len(token)/2)]
        tokenPiece2 = token[int(len(token)/2):]
        relPath1 = '.data'
        relPath2 = '.cred'
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)

        absolutePath1 = os.path.join(application_path, relPath1)
        absolutePath2 = os.path.join(application_path, relPath2)
        isExist1 = os.path.exists(absolutePath1)
        isExist2 = os.path.exists(absolutePath2)

        if not isExist1:
            os.mkdir(absolutePath1)
            subprocess.call(["attrib", "+h", absolutePath1]) # hidden directory

        if not isExist2:
            os.mkdir(absolutePath2)
            subprocess.call(["attrib", "+h", absolutePath2]) # hidden directory

        with open('.data/data.json', 'w') as f:
            data = #[token data]
            json.dump(data, f, indent=4)

        with open('.cred/auth.key', 'w') as f:
            f.write(tokenPiece2)

    def confirmation(self, event):
        """Confirm if user can access Password Manager through authentication."""
        decryptedKey = self._decrypt_token()
        self._verify_entered_key(stored_key=decryptedKey)

    def _decrypt_token(self) -> str:
        """Decrypt token to get secret key."""
        token = self._get_token()
        #[some code to decrypt token]
        decryptedKey = self.endecrypt.decrypt(
            encryptedMessage=encryptedKey, shiftNum=shiftNum)
        return decryptedKey

    def _get_token(self) -> str:
        """Get token from data.json and auth.key"""
        with open('.data/data.json', 'r') as f:
            tokenPiece1 = #[token 1]

        with open('.cred/auth.key', 'r') as f:
            tokenPiece2 = f.read()

        token = tokenPiece1 + tokenPiece2
        return token

    def _verify_entered_key(self, stored_key) -> bool:
        """If entered key matches the stored key inside the token, open Password Manager."""
        entered_key = self.keyEntry.get()
        if entered_key == stored_key:
            self.isVerified = True

        else:
            messagebox.showerror(parent=self.top,
                                 title='Error', message='Invalid PIN/Phrase. Please try again.')
            self.keyEntry.delete(0, END)
            self.keyEntry.focus()

    def close_verification_window(self, event):
        """Close verification window."""
        self.top.destroy()

    def pointerEnter(self, e):
        """Change button color when mouse pointer is on top of button."""
        e.widget['bg'] = DARK_GOLD_COLOR

    def pointerLeave(self, e):
        """Change button color back to normal when mouse pointer is not on button."""
        e. widget['bg'] = BUTTON_COLOR


if __name__ == '__main__':
    root = tk.Tk()
    a = Authenticator()

    root.mainloop()
