import datetime as dt
import tkinter as tk
import pyperclip
from tkinter import END


FONT = ('Bahnschrift Light', 16, 'normal')
BG_COLOR = '#30323D'
FG_COLOR = 'white'
GOLD_COLOR = 'gold2'
DARK_GOLD_COLOR = '#8B7536'
BUTTON_BG_COLOR = '#4D5061'


class WrapUpDateCalculator():
    """Models a wrap up date calculator. Calculates next wrap up date."""

    def __init__(self):
        """Initializes WrapUpDateCalculator graphical user interface."""

        self.top = tk.Toplevel()
        self.top.withdraw()
        self.top.attributes('-topmost', 0)
        self.top.title('Wrap Up Date Calculator')
        self.top.config(bg=BG_COLOR,
                        padx=25,
                        pady=15)
        self.top.resizable(width=False, height=False)

        self.cal_calc_icon = tk.PhotoImage(file="assets/img/cal_calc.png")
        self.top.iconphoto(False, self.cal_calc_icon)

        # Checkbutton
        self.alwaysTopVar = tk.IntVar()
        self.always_top_check_button = tk.Checkbutton(self.top, text='Always on top',
                                                      variable=self.alwaysTopVar, onvalue=1, offvalue=0,
                                                      bg=BG_COLOR, fg=FG_COLOR, font=(
                                                          'Bahnschrift Light', 10, 'normal'),
                                                      activebackground=BG_COLOR, activeforeground=FG_COLOR,
                                                      selectcolor=BG_COLOR, command=self.always_top)
        self.always_top_check_button.grid(
            column=0, row=0, sticky='NW', pady=(0, 10))

        # Dispense Date Label & Entry
        self.dispense_date_label = tk.Label(self.top, text='Dispense Date:',
                                            bg=BG_COLOR,
                                            fg=FG_COLOR,
                                            font=FONT)
        self.dispense_date_label.grid(column=0, row=1, sticky='E')
        self.dispense_date_entry = tk.Entry(self.top, bg=FG_COLOR,
                                            fg=BG_COLOR,
                                            font=FONT,
                                            width=12)
        self.dispense_date_entry.grid(column=1, row=1,
                                      padx=10, pady=5)

        # Day Supply Label & Entry
        self.day_supply_label = tk.Label(self.top, text='Day Supply:',
                                         bg=BG_COLOR,
                                         fg=FG_COLOR,
                                         font=FONT)
        self.day_supply_label.grid(column=0, row=2, sticky='E')
        self.day_supply_entry = tk.Entry(self.top, bg=FG_COLOR,
                                         fg=BG_COLOR,
                                         font=FONT,
                                         width=12)
        self.day_supply_entry.grid(column=1, row=2, pady=10)

        # Custom wrap up date
        self.custom_canvas = tk.Canvas(
            self.top, bg=BG_COLOR, highlightbackground=BG_COLOR, highlightcolor=BG_COLOR)
        self.custom_canvas.grid(column=0, row=3, columnspan=2, pady=5)
        self.custom_wrapUpLabel = tk.Label(
            self.custom_canvas, text='Wrap up', font=FONT, bg=BG_COLOR, fg=FG_COLOR)
        self.custom_wrapUpLabel.grid(column=0, row=0)
        self.custom_wrapUpEntry = tk.Entry(
            self.custom_canvas, font=('Bahnschrift Light', 14, 'bold'), width=2, justify='center', bg=BUTTON_BG_COLOR, fg=FG_COLOR)
        self.custom_wrapUpEntry.grid(column=1, row=0, padx=4)
        self.custom_wrapUpEntry.insert(0, '7')
        self.custom_daysBeforeLabel = tk.Label(
            self.custom_canvas, text='days before', font=FONT, bg=BG_COLOR, fg=FG_COLOR)
        self.custom_daysBeforeLabel.grid(column=2, row=0)

        # self.v = tk.IntVar()
        # self.v.set(1)
        # self.seven_days = tk.Radiobutton(self.top, text='7 days before', variable=self.v, value=1,
        #                                  bg=BG_COLOR, fg=FG_COLOR, font=(
        #                                      'Bahnschrift Light', 11, 'normal'),
        #                                  activebackground=BG_COLOR, activeforeground=FG_COLOR,
        #                                  selectcolor=BG_COLOR)
        # self.seven_days.grid(column=0, row=3, pady=5)
        # self.nine_days = tk.Radiobutton(self.top, text='9 days before', variable=self.v, value=2,
        #                                 bg=BG_COLOR, fg=FG_COLOR, font=(
        #                                     'Bahnschrift Light', 11, 'normal'),
        #                                 activebackground=BG_COLOR, activeforeground=FG_COLOR,
        #                                 selectcolor=BG_COLOR)
        # self.nine_days.grid(column=1, row=3, pady=5)

        # Calculate Button
        self.calculate_button = tk.Button(self.top, text='Calculate',
                                          bg=BUTTON_BG_COLOR,
                                          fg=FG_COLOR,
                                          font=FONT,
                                          activebackground=GOLD_COLOR,
                                          borderwidth=0, command=self.calculate_wrap_up_date)
        self.calculate_button.grid(column=0, row=4,
                                   sticky='EW',
                                   columnspan=2,
                                   padx=5,
                                   pady=(10, 7))
        self.calculate_button.bind('<Enter>', self.pointerEnterCalculator)
        self.calculate_button.bind('<Leave>', self.pointerLeaveCalculator)

        # Wrap Up Date Label
        self.wrap_up_date_text = tk.Label(self.top, text='Wrap Up Date:',
                                          font=('Bahnschrift Light',
                                                18, 'normal'),
                                          bg=BG_COLOR,
                                          fg='gold')
        self.wrap_up_date_text.grid(column=0, row=6, pady=6)
        self.wrap_up_date = tk.Label(self.top, text='',
                                     font=('Bahnschrift Light', 18, 'normal'),
                                     bg=BG_COLOR,
                                     fg='gold')
        self.wrap_up_date.grid(column=1, row=6, pady=6)

        # Clear button
        self.clear_button = tk.Button(self.top, text='Clear',
                                      bg=BUTTON_BG_COLOR,
                                      fg=FG_COLOR,
                                      font=FONT,
                                      activebackground=GOLD_COLOR,
                                      borderwidth=0, command=self.clear)
        self.clear_button.grid(
            column=1, row=5, sticky='EW', padx=(7, 5), pady=(0, 10))
        self.clear_button.bind('<Enter>', self.pointerEnterClear)
        self.clear_button.bind('<Leave>', self.pointerLeaveClear)

        # Exit button
        self.exit_button = tk.Button(self.top, text='Exit',
                                     bg=BUTTON_BG_COLOR,
                                     fg=FG_COLOR,
                                     font=FONT,
                                     activebackground='firebrick3', activeforeground='white',
                                     borderwidth=0, command=self.top.destroy)
        self.exit_button.grid(column=0, row=5, sticky='EW',
                              padx=(5, 0), pady=(0, 10))
        self.exit_button.bind('<Enter>', self.pointerEnterExit)
        self.exit_button.bind('<Leave>', self.pointerLeaveExit)

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
        self.dispense_date_entry.focus()

        self.top.bind('<Return>', self.calculate_wrap_up_date)
        self.top.bind('<Delete>', self.clear)
        self.custom_wrapUpEntry.bind('<FocusIn>', self.highlight_text)

    def press_enter_calculate_wrap_up_date(self, event):
        self.calculate_wrap_up_date()

    def press_enter_clear(self, event):
        self.clear()

    def clear(self, event=None):
        """Clear all entries."""
        self.dispense_date_entry.delete(0, END)
        self.day_supply_entry.delete(0, END)
        self.wrap_up_date.config(text='')
        self.dispense_date_entry.focus()

    def always_top(self):
        """Window always display on top."""
        if self.alwaysTopVar.get() == 1:
            self.top.attributes('-topmost', 1)
        elif self.alwaysTopVar.get() == 0:
            self.top.attributes('-topmost', 0)

    def calculate_wrap_up_date(self, event=None):
        """Calculate the next wrap up date."""
        # Separate month, day, and year into a list.
        try:
            entered_dispense_date = self.dispense_date_entry.get()
            if '/' in entered_dispense_date:
                dispense_date_split = entered_dispense_date.split('/')
            elif '-' in entered_dispense_date:
                dispense_date_split = entered_dispense_date.split('-')

            # Check if user entered 4 digits year. If not, format it to YYYY.
            if len(entered_dispense_date) <= 5:
                if len(dispense_date_split) == 3:
                    # if only 1 digit in the year
                    if len(dispense_date_split[2]) == 1:
                        self.wrap_up_date.config(text='INVALID')
                        return
                else:
                    dispense_year = dt.datetime.now().year
            else:
                dispense_year = dispense_date_split[2]
                if len(dispense_year) == 2:
                    dispense_year = '20' + dispense_year

            dispense_month = int(dispense_date_split[0])
            dispense_day = int(dispense_date_split[1])
            dispense_year = int(dispense_year)

            day_supply = int(self.day_supply_entry.get())
            dispense_date = dt.datetime(
                month=dispense_month, day=dispense_day, year=dispense_year)

            days_before = int(self.custom_wrapUpEntry.get())

            wrap_up_date = dispense_date + \
                dt.timedelta(days=day_supply-days_before)
            # Avoid weekends
            if dt.datetime(wrap_up_date.year, wrap_up_date.month, wrap_up_date.day).weekday() == 5:
                wrap_up_date = dispense_date + \
                    dt.timedelta(days=day_supply-days_before-1)
            if dt.datetime(wrap_up_date.year, wrap_up_date.month, wrap_up_date.day).weekday() == 6:
                wrap_up_date = dispense_date + \
                    dt.timedelta(days=day_supply-days_before-2)

            # Make sure wrap up date is not in the past.

            if wrap_up_date < dt.datetime.today() and len(entered_dispense_date) < 10:
                self.wrap_up_date.config(text='INVALID')
                return

            formatted_wrap_up_date = wrap_up_date.strftime('%m/%d/%Y')
            self.wrap_up_date.config(text=f'{formatted_wrap_up_date}')
            pyperclip.copy(formatted_wrap_up_date)
        except:
            self.wrap_up_date.config(text='INVALID')

    def pointerEnterCalculator(self, event):
        """Change Calculate button color on mouse hover."""
        self.calculate_button['bg'] = DARK_GOLD_COLOR

    def pointerLeaveCalculator(self, event):
        """Change Calculate button color back to normal when mouse leave button."""
        self.calculate_button['bg'] = BUTTON_BG_COLOR

    def pointerEnterClear(self, event):
        """Change Clear button color on mouse hover."""
        self.clear_button['bg'] = DARK_GOLD_COLOR

    def pointerLeaveClear(self, event):
        """Change Clear button color back to normal when mouse leave button."""
        self.clear_button['bg'] = BUTTON_BG_COLOR

    def pointerEnterExit(self, event):
        """Change Exit button color on mouse hover."""
        self.exit_button['bg'] = 'coral4'

    def pointerLeaveExit(self, event):
        """Change Exit button color back to normal when mouse leave button."""
        self.exit_button['bg'] = BUTTON_BG_COLOR

    def highlight_text(self, event):
        """Highlight custom wrap up Entry box when clicked."""
        self.custom_wrapUpEntry.selection_range(0, END)


if __name__ == '__main__':
    root = tk.Tk()
    wudc = WrapUpDateCalculator()

    root.mainloop()
