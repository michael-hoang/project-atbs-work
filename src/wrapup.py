import datetime as dt
import tkinter as tk
import ttkbootstrap as tkb

from win32 import win32clipboard
from tkinter import WORD
from tkinter.ttk import Style
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip


class WrapUp(tkb.Frame):
    """Wrap up date calculator."""

    def __init__(self, master):
        """Initialize."""
        super().__init__(master, padding=20)
        self.pack(side=LEFT, fill=BOTH, expand=YES)
        style = Style()
        style.configure('TButton', font=('', 9, ''))
        self.next_wrap_up_date = ''

        # GUI
        row_1 = self.create_inner_frame(self)
        dispense_date_label = self.create_label(
            master=row_1,
            text='Dispense Date:',
            anchor='e',
            padding=False,
        )
        self.dispense_date_entry = tkb.DateEntry(
            master=row_1,
        )
        self.dispense_date_entry.entry.config(font=('', 9, ''), width=11)
        self.dispense_date_entry.entry.delete(0, END)
        self.dispense_date_entry.pack(side=LEFT, fill=BOTH, padx=10)

        row_2 = self.create_inner_frame(self)
        day_supply_label = self.create_label(
            master=row_2,
            text='Day Supply:',
            anchor='e',
            padding=False,
        )
        self.day_supply_entry = self.create_short_entry(
            master=row_2,
            width=12
        )
        self.day_supply_entry.pack_configure(expand=YES, padx=10)

        row_3 = self.create_inner_frame(self)
        wrap_up_label = self.create_label(
            master=row_3,
            text='Wrap up',
            padding=False,
        )
        self.days_entry = self.create_short_entry(
            master=row_3,
            width=3,
            justify=CENTER
        )
        self.days_entry.insert(END, 7)
        days_before_label = self.create_label(
            master=row_3,
            text='days before',
            anchor='w',
        )

        row_4 = self.create_inner_frame(self)
        self.next_wrap_up_label = self.create_label(
            master=row_4,
            text='Next Wrap Up Date:',
            anchor='w',
            padding=False,
        )

        row_5 = self.create_inner_frame(self)
        copy_btn = tkb.Button(
            master=row_5,
            text='Copy',
            command=self.copy_plaintext_to_clipboard,
            width=10,
            padding=5
        )
        copy_btn.pack(side=LEFT, padx=(15, 0))

        clear_btn = tkb.Button(
            master=row_5,
            text='Clear',
            command=self.clear,
            width=10,
            padding=5,
            style='TButton.secondary'
        )
        clear_btn.pack(side=RIGHT, padx=(0, 15))

        self.after(ms=50, func=self.calculate_wrap_up_date)

        self.day_supply_entry.bind('<FocusIn>', self.highlight_day_supply_entry_text)
        self.days_entry.bind('<FocusIn>', self.highlight_days_entry_text)

    def highlight_day_supply_entry_text(self, event):
        """Highlight custom wrap up Entry box when clicked."""
        self.day_supply_entry.selection_range(0, END)

    def highlight_days_entry_text(self, event):
        """Highlight custom wrap up Entry box when clicked."""
        self.days_entry.selection_range(0, END)

    def copy_plaintext_to_clipboard(self):
        """Copy formatted plain text to clipboard."""
        win32clipboard.OpenClipboard(0)
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(self.next_wrap_up_date, win32clipboard.CF_TEXT)
        win32clipboard.CloseClipboard()

    def clear(self):
        """Clear all entries."""
        self.dispense_date_entry.entry.delete(0, END)
        self.day_supply_entry.delete(0, END)
        self.next_wrap_up_label.config(text='Next Wrap Up Date:')
        self.dispense_date_entry.focus()

    def calculate_wrap_up_date(self):
        """Calculate the next wrap up date."""
        # Separate month, day, and year into a list.
        self.after(ms=50, func=self.calculate_wrap_up_date)
        try:
            entered_dispense_date = self.dispense_date_entry.entry.get()
            if '/' in entered_dispense_date:
                dispense_date_split = entered_dispense_date.split('/')
            elif '-' in entered_dispense_date:
                dispense_date_split = entered_dispense_date.split('-')

            # Check if user entered 4 digits year. If not, format it to YYYY.
            if len(entered_dispense_date) <= 5:
                if len(dispense_date_split) == 3:
                    # if only 1 digit in the year
                    if len(dispense_date_split[2]) == 1:
                        self.next_wrap_up_label.config(text=f'Next Wrap Up Date:')
                        self.next_wrap_up_date = ''
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

            days_before = int(self.days_entry.get())

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
                self.next_wrap_up_label.config(text='Next Wrap Up Date:')
                self.next_wrap_up_date = ''
                return

            formatted_wrap_up_date = wrap_up_date.strftime('%m/%d/%Y')
            self.next_wrap_up_label.config(text=f'Next Wrap Up Date:    {formatted_wrap_up_date}')
            self.next_wrap_up_date = formatted_wrap_up_date
        except:
            self.next_wrap_up_label.config(text='Next Wrap Up Date:')
            self.next_wrap_up_date = ''

    # Widget creation methods

    def create_inner_frame(self, master, grid=False):
        """Create an inner frame."""
        frame = tkb.Frame(master)
        if not grid:
            frame.pack(anchor='w', fill=BOTH, pady=7)

        return frame

    def create_label(self, master, text, anchor='e',  width=DEFAULT, padding=True, grid=False):
        """Create a label."""
        label = tkb.Label(
            master=master,
            text=text,
            width=width,
            anchor=anchor,
            font=('', 9, '')
        )
        if not grid:
            label.pack(side=LEFT, fill=BOTH, expand=YES, padx=(3, 0))
            if not padding:
                label.pack_configure(padx=0)

        return label

    def create_short_entry(self, master, width=15, padding=True, text_var=None, state='normal', justify=None, grid=False, tooltip=''):
        """Create an entry field."""
        entry = tkb.Entry(
            master=master,
            width=width,
            textvariable=text_var,
            state=state,
            font=('', 9, ''),
            justify=justify,
        )
        if not grid:
            entry.pack(side=LEFT, fill=BOTH, padx=(3, 0))
            if not padding:
                entry.pack_configure(padx=0)

        return entry


if __name__ == '__main__':
    app = tkb.Window(
        'Wrap Up', 'superhero', resizable=(False, False)
    )
    WrapUp(app)
    app.place_window_center()
    app.mainloop()
