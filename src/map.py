import tkinter as tk
from tkinter import END
import webbrowser


BG_COLOR = '#30323D'
FG_COLOR = 'white'
BG_COLOR3 = '#5C80BC'
BUTTON_BG_COLOR = '#4D5061'
FONT = ('Bahnschrift Light', 16, 'normal')
GOLD_COLOR = 'gold2'
DARK_GOLD_COLOR = '#8B7536'


class Map:
    """Represents Maps search from UCI MC to destination."""

    def __init__(self):
        """Initializes Map Search GUI."""
        self.top = tk.Toplevel()
        self.top.withdraw()
        self.top.title('Search Maps')
        self.top.config(bg=BG_COLOR, padx=20, pady=20)
        self.top.resizable(width=False, height=False)
        self.map_icon = tk.PhotoImage(file="assets/img/map_icon.png")
        self.top.iconphoto(False, self.map_icon)

        # Checkbutton
        self.alwaysTopVar = tk.IntVar()
        self.always_top_cb = tk.Checkbutton(self.top, text='Always on top',
                                            variable=self.alwaysTopVar, onvalue=1, offvalue=0,
                                            bg=BG_COLOR, fg=FG_COLOR, font=(
                                                'Bahnschrift Light', 10, 'normal'),
                                            activebackground=BG_COLOR, activeforeground=FG_COLOR,
                                            selectcolor=BG_COLOR, command=self.always_top)
        self.always_top_cb.grid(column=0, row=0, sticky='E')

        # Address Label & Text
        self.address_l = tk.Label(self.top, text='Address:', bg=BG_COLOR, fg='gold',
                                  font=('Bahnschrift Light', 20, 'normal'))
        self.address_l.grid(column=0, row=0, sticky='W')
        self.address_t = tk.Text(self.top, bg=FG_COLOR, fg=BG_COLOR,
                                 font=FONT, width=25, height=3)
        self.address_t.grid(column=0, row=1, pady=(13, 20))

        # Get Direction Button
        self.calculate_b = tk.Button(self.top, text='Search', bg=BUTTON_BG_COLOR,
                                     fg=FG_COLOR, font=FONT, activebackground=GOLD_COLOR,
                                     borderwidth=0, command=self.get_direction, width=12, pady=2)
        self.calculate_b.grid(column=0, row=2, columnspan=2)

        self.top.bind('<Shift-Return>', self.get_direction)
        self.top.bind('<Delete>', self.clear)

        # Center window to screen
        self.top.update_idletasks()
        win_width = self.top.winfo_reqwidth()
        win_height = self.top.winfo_reqheight()
        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        x = int(screen_width/2 - win_width/2)
        y = int(screen_height/2 - win_height/2)
        self.top.geometry(f"{win_width}x{win_height}+{x}+{y}")
        self.top.deiconify()
        self.address_t.focus_set()

        # URL
        self.mapUrl = 'https://www.google.com/maps/dir/'
        self.address = 'Disneyland/'
        self.destination = ''

        self.calculate_b.bind('<Enter>', self.pointerEnter)
        self.calculate_b.bind('<Leave>', self.pointerLeave)

    def get_direction(self, even=None):
        """Get destination from user."""
        destination = self.address_t.get(index1='1.0', index2=END)
        destination_split = destination.split()
        for text in destination_split:
            self.destination += text
            self.destination += '+'
        url = self.mapUrl + self.address + self.destination
        webbrowser.open(url=url, new=2, autoraise=True)
        self.destination = ''

    def press_enter_get_direction(self, event):
        self.get_direction()

    def clear(self, event):
        """Clear text box."""
        self.address_t.delete(index1='1.0', index2=END)

    def always_top(self):
        """Window always display on top."""
        if self.alwaysTopVar.get() == 1:
            self.top.attributes('-topmost', 1)
        elif self.alwaysTopVar.get() == 0:
            self.top.attributes('-topmost', 0)

    def pointerEnter(self, e):
        """Change button color on mouse hover."""
        e.widget['bg'] = DARK_GOLD_COLOR

    def pointerLeave(self, e):
        """Change button color back to normal on mouse hover."""
        e.widget['bg'] = BUTTON_BG_COLOR


if __name__ == '__main__':
    root = tk.Tk()
    gm = Map()
    root.mainloop()
