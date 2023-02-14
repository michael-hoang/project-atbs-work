import tkinter as tk
from tkinter import messagebox
import json
from encryption import EnDeCrypt
from functools import partial


BG_COLOR = '#30323D'
GRAY_COLOR = '#4D5061'
GOLD_COLOR = 'gold2'
DARK_RED_COLOR = '#460000'
FONT = ('Bahnschrift Light', 12, 'normal')


class DataBase(tk.Toplevel):
    """Represents a database that stores all login information."""

    def __init__(self, root):
        """Initialize DataBase attributes."""
        super().__init__()
        self.withdraw()
        self.title('Account Database')
        lock_img = tk.PhotoImage(file='assets/img/lock_icon.png')
        self.iconphoto(False, lock_img)

        self.createCanvas()
        self.resizable(width=False, height=True)

        # Center settings window to root screen
        self.update_idletasks()
        x = root.winfo_x()
        y = root.winfo_y()
        rootWidth = root.winfo_reqwidth()
        rootHeight = root.winfo_reqheight()
        topWidth = self.winfo_reqwidth()
        topHeight = self.winfo_reqheight()
        dx = int((rootWidth/2) - (topWidth/2))
        dy = int((rootHeight/2) - (topHeight/2))
        self.geometry('+%d+%d' % (x + dx, y + dy))

        root.attributes('-disabled', 1)
        self.grab_set()
        self.wm_transient(root)
        self.deiconify()
        self.focus_force()

        self.bind('<Escape>', lambda event: self.exit_window(event, root))
        self.protocol('WM_DELETE_WINDOW', lambda: self.on_closing(root))

    def on_closing(self, root):
        """Enable root window on closing DataBase TopLevel window."""
        root.attributes('-disabled', 0)
        self.destroy()

    def createCanvas(self):
        """Create canvas on TopLevel DataBase window to display login info."""
        self.canvas = tk.Canvas(
            self, width=645, height=228, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(side='left', fill='both', expand=True)

        self.scrollbar = tk.Scrollbar(
            self, orient='vertical', command=self.canvas.yview, bg=BG_COLOR)
        self.scrollbar.pack(side='right', fill='y')

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.bind("<Configure>", lambda event: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))

        self.headerFrame = tk.Frame(self.canvas, bg=BG_COLOR)
        self.canvas.create_window(0, 0, window=self.headerFrame, anchor='nw')

        index = tk.Entry(master=self.headerFrame, width=2,
                         disabledbackground=BG_COLOR, disabledforeground=GOLD_COLOR)
        index.grid(column=0, row=0)
        index.insert(0, '#')
        index.config(state='disabled', font=FONT, width=2, justify='center')

        website = tk.Entry(master=self.headerFrame, width=18,
                           disabledbackground=BG_COLOR, disabledforeground=GOLD_COLOR)
        website.grid(column=1, row=0)
        website.insert(0, 'Website')
        website.config(state='disabled', font=FONT)

        username = tk.Entry(master=self.headerFrame, width=25,
                            disabledbackground=BG_COLOR, disabledforeground=GOLD_COLOR)
        username.grid(column=2, row=0)
        username.insert(0, 'Username')
        username.config(state='disabled', font=FONT)

        password = tk.Entry(master=self.headerFrame,
                            disabledbackground=BG_COLOR, disabledforeground=GOLD_COLOR)
        password.grid(column=3, row=0)
        password.insert(0, 'Password')
        password.config(state='disabled', font=FONT)

        blank = tk.Entry(master=self.headerFrame,
                         disabledbackground=BG_COLOR, disabledforeground=GOLD_COLOR)
        blank.grid(column=4, row=0)
        blank.insert(0, '   --')
        blank.config(state='disabled', font=FONT)

        self.edc = EnDeCrypt()
        self.rowDict = {}
        self.display_login_info()

    def delete(self, key):
        """Delete entire row from database."""
        deWebsite = self.edc.decrypt(key)
        self.bell()
        confirmDelete = messagebox.askyesno(parent=self, title='Delete Confirmation',
                                            message=f'Are you sure you want to delete login information for {deWebsite.title()}?')
        if confirmDelete:
            pass
        else:
            return

        with open(file='.data/data.json', mode='r') as f:
            data = json.load(f)
            del data[key]

        with open(file='.data/data.json', mode='w') as f:
            json.dump(data, f, indent=4)

        # self.headerFrame.destroy()
        self.canvas.destroy()
        self.scrollbar.destroy()
        self.update
        self.createCanvas()

    def display_login_info(self):
        """Display login info from database."""
        with open(file='.data/data.json', mode='r') as f:
            data = json.load(f)

            number = 1
            entryRow = 1
            x = 0
            y = 23
            removeKey = data.pop('key')
            for k, v in data.items():
                scrollableframe = tk.Frame(
                    self.canvas, bg=BG_COLOR, highlightthickness=0)
                self.canvas.create_window(
                    x, y, window=scrollableframe, anchor='nw')

                deWebsite = self.edc.decrypt(k).title()
                deUsername = self.edc.decrypt(v['username'])
                dePassword = self.edc.decrypt(v['password'])

                index_entry = tk.Entry(
                    master=scrollableframe, disabledbackground=GRAY_COLOR, disabledforeground=GOLD_COLOR)
                index_entry.grid(column=0, row=entryRow)
                index_entry.insert(0, str(number))
                index_entry.config(state='disabled', font=FONT,
                                   width=2, justify='center')

                website_entry = tk.Entry(
                    master=scrollableframe, disabledbackground=GRAY_COLOR, disabledforeground='white')
                website_entry.grid(column=1, row=entryRow)
                website_entry.insert(0, deWebsite)
                website_entry.config(state='disabled', font=FONT, width=18)

                username_entry = tk.Entry(
                    master=scrollableframe, disabledbackground=GRAY_COLOR, disabledforeground='white')
                username_entry.grid(column=2, row=entryRow)
                username_entry.insert(0, deUsername)
                username_entry.config(state='disabled', font=FONT, width=25)

                password_entry = tk.Entry(
                    master=scrollableframe, disabledbackground=GRAY_COLOR, disabledforeground='white')
                password_entry.grid(column=3, row=entryRow)
                password_entry.insert(0, dePassword)
                password_entry.config(state='disabled', show='*', font=FONT)

                delete_button = tk.Button(
                    master=scrollableframe, text='Delete', command=partial(self.delete, key=k), bg=DARK_RED_COLOR, fg='white', activebackground='red', activeforeground='white')
                delete_button.grid(column=4, row=entryRow)
                delete_button.bind('<Enter>', self.pointerEnter)
                delete_button.bind('<Leave>', self.pointerLeave)

                scrollableframe.bind("<Configure>", lambda event: self.canvas.configure(
                    scrollregion=self.canvas.bbox("all")))
                self.rowDict[k] = scrollableframe
                number += 1
                entryRow += 1
                y += 23

    def pointerEnter(self, event):
        """Highlight button on mouse hover."""
        event.widget['bg'] = 'darkred'

    def pointerLeave(self, event):
        """Remove highlight when mouse not on button."""
        event.widget['bg'] = DARK_RED_COLOR

    def exit_window(self, event, root):
        """Exit Database window when ESC is pressed."""
        root.attributes('-disabled', 0)
        self.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    db = DataBase(root=root)

    root.mainloop()
