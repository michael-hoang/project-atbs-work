import pandas as pd
import ttkbootstrap as tkb

from ttkbootstrap.constants import *
from tkinter.ttk import Style


FONT = ('', 9, '')
EXCEL_PATH = './.data/drug_db.xlsx'


class DropShipLookUp(tkb.Frame):
    """GUI for searching if a drug is ordered through drop ship."""

    def __init__(self, master, root):
        super().__init__(master=master, padding=25)
        self.pack()
        self.root = root
        style = Style()
        style.configure('TButton', font=FONT)

        self.ndc_str_var = tkb.StringVar()

        # Load Excel
        self.excel_data_df = self.load_excel_data(EXCEL_PATH)

        # GUI
        ndc_format_label = tkb.Label(
            master=self,
            text='Enter 11-digit raw NDC',
            font=FONT
        )
        ndc_format_label.pack(side=TOP)

        ndc_input_container = tkb.Frame(master=self)
        ndc_input_container.pack(side=TOP, fill=BOTH, pady=(15, 0))

        ndc_label = tkb.Label(
            master=ndc_input_container,
            text='NDC:',

        )
        ndc_label.pack(side=LEFT)

        self.ndc_entry = tkb.Entry(
            master=ndc_input_container,
            width=16,
            font=FONT,
            textvariable=self.ndc_str_var,
            justify=CENTER
        )
        self.ndc_entry.pack(side=LEFT, padx=(10, 0))

        self.check_btn = tkb.Button(
            master=ndc_input_container,
            text='Check',
            style='TButton',
            command=self.check_if_dropship,
            width=7,
            state='disabled'
        )
        self.check_btn.pack(side=LEFT, padx=(15, 0))

        drug_name_container = tkb.Frame(master=self)
        drug_name_container.pack(side=TOP, fill=BOTH, pady=(15, 0))

        drug_name_label = tkb.Label(
            master=drug_name_container,
            text='Drug:',
            font=FONT
        )
        drug_name_label.pack(side=LEFT)

        self.drug_name = tkb.Text(
            master=drug_name_container,
            font=FONT,
            height=3,
            width=28,
            state='disabled'
        )
        self.drug_name.pack(side=LEFT, padx=(10, 0))

        status_container = tkb.Frame(master=self)
        status_container.pack(side=TOP, fill=BOTH, pady=(15, 0))

        status_label = tkb.Label(
            master=status_container,
            text='Status:',
            font=FONT
        )
        status_label.pack(side=LEFT)

        self.status = tkb.Label(
            master=status_container,
            text='',
            font=FONT
        )
        self.status.pack(side=LEFT, padx=(10, 0))

        # Key binds
        self.ndc_entry.bind('<FocusIn>', self._on_click_select)
        self.root.bind('<Return>', self._on_enter_check_if_dropship)
        self.root.bind('<Delete>', self._on_delete_clear)

        # Register validation callback
        digit_func = self.root.register(self._validate_digit)

        # Validate 11 digits entry
        self.ndc_entry.config(
            validate='key', validatecommand=(digit_func, '%P')
        )

        # After recursion
        self.after(50, self._check_length)

    def _on_click_select(self, event):
        self.ndc_entry.select_range(0, END)

    def _on_enter_check_if_dropship(self, event):
        if len(self.ndc_str_var.get()) == 11:
            self.check_if_dropship()
            self._on_click_select(event=None)

    def _on_delete_clear(self, event):
        self.ndc_entry.delete(0, END)
        self.ndc_entry.focus()

    def _validate_digit(self, ndc) -> bool:
        if ndc.isdigit():
            return True
        elif ndc == '':
            return True
        else:
            return False

    def _check_length(self):
        if len(self.ndc_str_var.get()) == 11:
            self.check_btn.config(state='normal')
        else:
            self.check_btn.config(state='disabled')

        self.after(50, self._check_length)

    def load_excel_data(self, excel_path) -> pd:
        df = pd.read_excel(excel_path, dtype={'NDC': str})
        return df

    def iterate_excel_data(self, ndc) -> tuple:
        item = ''
        for index, row in self.excel_data_df.iterrows():
            for column_name, value in row.items():
                if column_name == 'NDC':
                    if value == ndc:
                        continue
                    else:
                        break
                elif column_name == 'Item':
                    item = value
                elif column_name == 'Drop Ship':
                    if value == True:
                        return (item, True)
                    else:
                        return (item, False)

        return (None, None)

    def check_if_dropship(self):
        ndc = self.ndc_str_var.get()
        item, dropship = self.iterate_excel_data(ndc)
        self.drug_name.config(state='normal')
        self.drug_name.delete(1.0, END)
        if dropship:
            self.drug_name.insert(1.0, item)
            self.status.config(text='DROP SHIP', foreground='magenta2')
        elif dropship == False:
            self.drug_name.insert(1.0, item)
            self.status.config(text='NOT DROP SHIP', foreground='green3')
        else:
            self.drug_name.insert(1.0, 'NDC not in database')
            self.status.config(text='N/A', foreground='')

        self.drug_name.config(state='disabled')
        self.ndc_entry.focus()


if __name__ == '__main__':
    app = tkb.Window(
        title='Drop Ship Look Up',
        themename='superhero',
        resizable=(False, False)
    )
    app.withdraw()
    ds = DropShipLookUp(app, app)
    app.place_window_center()
    app.deiconify()
    ds.ndc_entry.focus()

    app.mainloop()
