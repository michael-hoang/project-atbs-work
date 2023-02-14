"""This module contains a class that represents a card payment form GUI."""

from tkinter import *
from tkinter import messagebox
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime
from PIL import Image, ImageTk
import os
import subprocess
import sys
import re
import datetime as dt
from calendar import monthrange
import time


LABEL_BG = '#EAEEF3'
WINDOW_BG = '#EAEEF3'
ENTRY_BG = '#F8FAFC'
BUTTON_BG = '#484B5B'
FONT = ('Helvetica', 11, 'normal')
ENTRY_FONT = ('Helvetica', 10, 'normal')
NOTES_FONT = ('Courier', 13, 'normal')


class CardPayment:
    """
    Models card payment interface to enter information and then outputs payment 
    form in PDF.
    """

    def __init__(self):
        self.fields = {
            'Date': datetime.today().strftime('%m-%d-%Y'),
            'Visa': '',
            'MasterCard': '',
            'Discover': '',
            'AMEX': '',
            'Credit Card No': '',
            'Exp': '',
            'Security No': '',
            'Cardholder Name': '',
            'MRN': '',
            'Medication Names 1': '',
            'Medication Names 2': '',
            'Medication Names 3': '',
            'Medication Names 4': '',
            'Medication Names 5': '',
            'Cost': '',
            'Cost 2': '',
            'Cost 3': '',
            'Cost 4': '',
            'Cost 5': '',
            'Total': '',
            'Notes': '',
        }

        self.top = Toplevel()
        self.top.withdraw()
        self.top.attributes('-topmost', 0)
        self.top.config(padx=20, pady=20, bg=WINDOW_BG)
        self.top.resizable(width=False, height=False)
        self.top.title("Card Payment Form")
        self.top.after(ms=50, func=self.update_fields)
        self.remove_files()
        self.top.after(ms=3_600_000, func=self.remove_files) # after 1 hour

        self.cc_icon = PhotoImage(file="assets/img/cc_icon.png")
        self.top.iconphoto(False, self.cc_icon)

        # Always on top Checkbutton
        self.alwaysTopVar = IntVar()
        self.always_top_check_button = Checkbutton(self.top, text='Always on top', font=('Helvetica', 9, 'normal'),
                                                   variable=self.alwaysTopVar, onvalue=1, offvalue=0,
                                                   command=self.always_top, bg=LABEL_BG, activebackground=LABEL_BG)
        self.always_top_check_button.grid(
            column=0, row=0, columnspan=3, sticky='NW')

        # Add Notes button
        self.notes_button = Button(self.top, text='Add Notes', font=FONT, bg=WINDOW_BG, relief=GROOVE, command=lambda: self.toggle_notes_window(event=None))
        self.notes_button.grid(column=4, row=0, columnspan=2, sticky='E', pady=(0, 12))

        # Add Notes Window
        self.notes_window = Toplevel(self.top, bg=WINDOW_BG, padx=5, pady=5)
        self.notes_window.title('Add Notes')
        self.notes_window.resizable(width=False, height=False)
        self.notes_isHidden = True
        self.toggle_notes_window(event=None)
        self.notes_window.protocol('WM_DELETE_WINDOW', func=lambda: self.toggle_notes_window(event=None))

        self.notes_text = Text(self.notes_window, height=5, width=26, font=NOTES_FONT, wrap=WORD)
        self.notes_text.grid(column=0, row=0, columnspan=2, padx=10, pady=10)

        self.notes_ok_button = Button(self.notes_window, text='OK', font=FONT, width=6, command=lambda: self.toggle_notes_window(event=None))
        self.notes_ok_button.grid(column=0, row=1, sticky='E', padx=(0, 10), pady=(0, 5))
        self.notes_clear_button = Button(self.notes_window, text='Clear', font=FONT, width=6, command=lambda: self.clear_notes(event=None))
        self.notes_clear_button.grid(column=1, row=1, sticky='W', padx=(10, 0), pady=(0, 5))

        self.notes_window.bind('<Escape>', self.toggle_notes_window)
        self.notes_window.bind('<Delete>', self.clear_notes)

        # Card Button image
        self.image_paths = [
            "assets/img/generic_card.png",
            "assets/img/amex.png",
            "assets/img/discover.png",
            "assets/img/mastercard.png",
            "assets/img/visa.png"
        ]

        self.tk_images = {}

        for image_path in self.image_paths:
            with Image.open(fp=f"{image_path}") as i:
                img = i.resize(size=(75, 50))
                img_value = ImageTk.PhotoImage(img)
            key = image_path.split("/")[-1]
            image_key = key.split(".")[0]
            self.tk_images[image_key] = img_value

        self.card_button = Button(
            self.top, image=self.tk_images["generic_card"], borderwidth=0, command=self.open_directory)
        self.card_button.grid(
            column=1, row=1, columnspan=2, rowspan=4, sticky="w")

        self.date_text_label = Label(
            self.top, text="Date:", bg=LABEL_BG, font=FONT)
        self.date_text_label.grid(column=2, row=1, columnspan=2, sticky="E")
        self.date_num_label = Label(
            self.top, text=datetime.today().strftime('%m-%d-%Y'), bg=LABEL_BG, font=FONT)
        self.date_num_label.grid(column=4, row=1, sticky="W")

        self.cc_label = Label(
            self.top, text="Credit Card No.", bg=LABEL_BG, font=FONT)
        self.cc_label.grid(column=2, row=2, columnspan=2, sticky="E")
        self.cc_entry = Entry(self.top, relief='flat',
                              bg=ENTRY_BG, font=ENTRY_FONT)
        self.cc_entry.grid(column=4, row=2)

        self.exp_label = Label(self.top, text="Exp:", bg=LABEL_BG, font=FONT)
        self.exp_label.grid(column=2, row=3, columnspan=2, sticky="E")
        self.exp_entry = Entry(self.top, relief='flat',
                               bg=ENTRY_BG, font=ENTRY_FONT)
        self.exp_entry.grid(column=4, row=3)

        self.cvv_label = Label(
            self.top, text="Security No.", bg=LABEL_BG, font=FONT)
        self.cvv_label.grid(column=2, row=4, columnspan=2, sticky="E")
        self.cvv_entry = Entry(self.top, relief='flat',
                               bg=ENTRY_BG, font=ENTRY_FONT)
        self.cvv_entry.grid(column=4, row=4)

        self.cardholder_label = Label(
            self.top, text="Cardholder Name:", bg=LABEL_BG, font=FONT)
        self.cardholder_label.grid(column=2, row=5, columnspan=2, sticky="E")
        self.cardholder_entry = Entry(
            self.top, relief='flat', bg=ENTRY_BG, font=ENTRY_FONT)
        self.cardholder_entry.grid(column=4, row=5)

        self.mrn_label = Label(self.top, text="MRN:", bg=LABEL_BG, font=FONT)
        self.mrn_label.grid(column=2, row=6, columnspan=2, sticky="E")
        self.mrn_entry = Entry(self.top, relief='flat',
                               bg=ENTRY_BG, font=ENTRY_FONT)
        self.mrn_entry.grid(column=4, row=6)

        self.index_label1 = Label(self.top, text="1.", bg=LABEL_BG, font=FONT)
        self.index_label1.grid(column=1, row=8, sticky="E")
        self.index_label2 = Label(self.top, text="2.", bg=LABEL_BG, font=FONT)
        self.index_label2.grid(column=1, row=9, sticky="E")
        self.index_label3 = Label(self.top, text="3.", bg=LABEL_BG, font=FONT)
        self.index_label3.grid(column=1, row=10, sticky="E")
        self.index_label4 = Label(self.top, text="4.", bg=LABEL_BG, font=FONT)
        self.index_label4.grid(column=1, row=11, sticky="E")
        self.index_label5 = Label(self.top, text="5.", bg=LABEL_BG, font=FONT)
        self.index_label5.grid(column=1, row=12, sticky="E")

        self.medication_label = Label(
            self.top, text="Medication Name(s)", bg=LABEL_BG, font=FONT)
        self.medication_label.grid(column=2, row=7, sticky="EW", pady=(15, 0))

        self.amount_label = Label(
            self.top, text="Price", bg=LABEL_BG, font=FONT)
        self.amount_label.grid(column=4, row=7, sticky="EW", pady=(15, 0))

        self.med_entry1 = Entry(self.top, relief='flat',
                                bg=ENTRY_BG, font=ENTRY_FONT)
        self.med_entry1.grid(column=2, row=8)
        self.dollar_label1 = Label(self.top, text="$", bg=LABEL_BG, font=FONT)
        self.dollar_label1.grid(column=3, row=8, padx=5, sticky="E")
        self.dollar_entry1 = Entry(
            self.top, relief='flat', bg=ENTRY_BG, font=ENTRY_FONT)
        self.dollar_entry1.grid(column=4, row=8)

        self.med_entry2 = Entry(self.top, relief='flat',
                                bg=ENTRY_BG, font=ENTRY_FONT)
        self.med_entry2.grid(column=2, row=9)
        self.dollar_label2 = Label(self.top, text="$", bg=LABEL_BG, font=FONT)
        self.dollar_label2.grid(column=3, row=9, padx=5, sticky="E")
        self.dollar_entry2 = Entry(
            self.top, relief='flat', bg=ENTRY_BG, font=ENTRY_FONT)
        self.dollar_entry2.grid(column=4, row=9)

        self.med_entry3 = Entry(self.top, relief='flat',
                                bg=ENTRY_BG, font=ENTRY_FONT)
        self.med_entry3.grid(column=2, row=10)
        self.dollar_label3 = Label(self.top, text="$", bg=LABEL_BG, font=FONT)
        self.dollar_label3.grid(column=3, row=10, padx=5, sticky="E")
        self.dollar_entry3 = Entry(
            self.top, relief='flat', bg=ENTRY_BG, font=ENTRY_FONT)
        self.dollar_entry3.grid(column=4, row=10)

        self.med_entry4 = Entry(self.top, relief='flat',
                                bg=ENTRY_BG, font=ENTRY_FONT)
        self.med_entry4.grid(column=2, row=11)
        self.dollar_label4 = Label(self.top, text="$", bg=LABEL_BG, font=FONT)
        self.dollar_label4.grid(column=3, row=11, padx=5, sticky="E")
        self.dollar_entry4 = Entry(
            self.top, relief='flat', bg=ENTRY_BG, font=ENTRY_FONT)
        self.dollar_entry4.grid(column=4, row=11)

        self.med_entry5 = Entry(self.top, relief='flat',
                                bg=ENTRY_BG, font=ENTRY_FONT)
        self.med_entry5.grid(column=2, row=12)
        self.dollar_label5 = Label(self.top, text="$", bg=LABEL_BG, font=FONT)
        self.dollar_label5.grid(column=3, row=12, padx=5, sticky="E")
        self.dollar_entry5 = Entry(
            self.top, relief='flat', bg=ENTRY_BG, font=ENTRY_FONT)
        self.dollar_entry5.grid(column=4, row=12)

        self.total_text_label = Label(
            self.top, text="Total", bg=LABEL_BG, font=('Helvetica', 11, 'bold'))
        self.total_text_label.grid(column=3, row=13, sticky="E", pady=(8, 0))
        self.total_num_label = Label(
            self.top, text="", bg=LABEL_BG, font=('Helvetica', 11, 'bold'))
        self.total_num_label.grid(column=4, row=13, sticky="", pady=(8, 0))

        self.done_button = Button(
            self.top, text="Done", command=lambda: self.message_box(event=None),
            borderwidth=0, bg=BUTTON_BG, fg='white', width=22, height=1,
            font=('Helvetica', 12, 'normal'), activebackground='#363945', activeforeground='white')
        self.done_button.grid(
            column=1, row=14, columnspan=4, pady=(15, 0))
        self.done_button.bind('<Enter>', self.pointerEnter)
        self.done_button.bind('<Leave>', self.pointerLeave)

        # Center window to screen
        self.top.update_idletasks()
        win_width = self.top.winfo_reqwidth()
        win_height = self.top.winfo_reqheight()
        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        x = int(screen_width/2 - win_width/2)
        y = int(screen_height/2 - win_width/2)
        self.top.geometry(f"{win_width}x{win_height}+{x}+{y}")
        self.top.deiconify()
        self.cc_entry.focus_set()

        self.top.bind('<Control-Return>', self.message_box)
        self.top.bind('<Control-n>', self.toggle_notes_window)

    def pointerEnter(self, e):
        """Highlight button on mouse hover."""
        e.widget['bg'] = '#5F6275'

    def pointerLeave(self, e):
        """Remove highlight from button when mouse leave."""
        e.widget['bg'] = BUTTON_BG

    def always_top(self):
        """Window always display on top."""
        if self.alwaysTopVar.get() == 1:
            self.top.attributes('-topmost', 1)
        elif self.alwaysTopVar.get() == 0:
            self.top.attributes('-topmost', 0)

    def cc_length_check(self):
        """Check length of credit card number to ensure correct number of digits are entered."""
        entered_cc_num = re.sub(r'[^0-9]', '', self.cc_entry.get())
        cc_length = len(entered_cc_num)
        try:
            if cc_length == 0:
                self.cc_label.config(fg='black')
            elif entered_cc_num[0] == '3':
                if cc_length == 15:
                    self.cc_label.config(fg='black')
                else:
                    self.cc_label.config(fg='red')
            else:
                if cc_length == 16:
                    self.cc_label.config(fg='black')
                else:
                    self.cc_label.config(fg='red')
        except IndexError:
            pass

    def cvv_length_check(self):
        """Check length of cvv to ensure correct number of digits are entered."""
        # Replace all characters except (^) 0 through 9 with ''
        entered_cc_num = re.sub(r'[^0-9]', '', self.cc_entry.get())
        entered_cvv_num = re.sub(r'[^0-9]', '', self.cvv_entry.get())
        cvv_length = len(entered_cvv_num)
        try:
            if cvv_length == 0:
                self.cvv_label.config(fg='black')
            elif entered_cc_num[0] == '3':
                if cvv_length == 4:
                    self.cvv_label.config(fg='black')
                else:
                    self.cvv_label.config(fg='red')
            else:
                if cvv_length == 3:
                    self.cvv_label.config(fg='black')
                else:
                    self.cvv_label.config(fg='red')
        except IndexError:
            pass

    def expiration_check(self):
        """Check expiration date of payment card."""
        # Replace all characters except (^) 0 through 9, /, and - with ''
        entered_exp_date = re.sub(r'[^0-9/-]', '', self.exp_entry.get())
        split_exp_date = re.split('[-/]', entered_exp_date)
        exp_date_length = len(split_exp_date)
        try:
            if exp_date_length == 2:  # Only month and year
                month = int(split_exp_date[0])
                year = int(split_exp_date[1])
                if len(str(year)) == 2:
                    year = 2000 + year

                day = monthrange(year, month)[1]
                exp_date = dt.datetime(year, month, day)

            elif exp_date_length == 3:  # Month, day, and year
                month = int(split_exp_date[0])
                day = int(split_exp_date[1])
                year = int(split_exp_date[2])
                if len(str(year)) == 2:
                    year = 2000 + year

                exp_date = dt.datetime(year, month, day)

            today = dt.datetime.now()

            if self.exp_entry.get() == '':
                self.exp_label.config(fg='black')
            elif exp_date < today:
                self.exp_label.config(fg='red')
            else:
                self.exp_label.config(fg='black')
        except (UnboundLocalError, ValueError):
            self.exp_label.config(fg='red')

    def update_fields(self):
        """ 
        Update self.fields attribute with information entered by user in the
        payment form entry.
        """

        self.fields |= {
            'Date': datetime.today().strftime('%m-%d-%Y'),
            'Credit Card No': self.cc_entry.get().lstrip(),
            'Exp': self.exp_entry.get(),
            'Security No': self.cvv_entry.get(),
            'Cardholder Name': self.cardholder_entry.get().lstrip(),
            'MRN': self.mrn_entry.get(),
            'Medication Names 1': self.med_entry1.get(),
            'Medication Names 2': self.med_entry2.get(),
            'Medication Names 3': self.med_entry3.get(),
            'Medication Names 4': self.med_entry4.get(),
            'Medication Names 5': self.med_entry5.get(),
        }

        if len(self.notes_text.get(1.0, 'end-1c').lstrip()) != 0:
            self.fields |= {'Notes': f'*** NOTE: ***\n' + self.notes_text.get(1.0, END)}
        else:
            self.fields |= {'Notes': ''}

        self.date_num_label.config(text=datetime.today().strftime('%m-%d-%Y'))

        if self.fields['Medication Names 1'] == "":
            cost_1 = 0
            self.fields['Cost'] = ""
        else:
            try:
                cost_1 = float(self.dollar_entry1.get())
            except ValueError:
                cost_1 = 0
                self.fields['Cost'] = ""
            else:
                self.fields['Cost'] = "${:,.2f}".format(cost_1)

        if self.fields['Medication Names 2'] == "":
            cost_2 = 0
            self.fields['Cost 2'] = ""
        else:
            try:
                cost_2 = float(self.dollar_entry2.get())
            except ValueError:
                cost_2 = 0
                self.fields['Cost 2'] = ""
            else:
                self.fields['Cost 2'] = "${:,.2f}".format(cost_2)

        if self.fields['Medication Names 3'] == "":
            cost_3 = 0
            self.fields['Cost 3'] = ""
        else:
            try:
                cost_3 = float(self.dollar_entry3.get())
            except ValueError:
                cost_3 = 0
                self.fields['Cost 3'] = ""
            else:
                self.fields['Cost 3'] = "${:,.2f}".format(cost_3)

        if self.fields['Medication Names 4'] == "":
            cost_4 = 0
            self.fields['Cost 4'] = ""
        else:
            try:
                cost_4 = float(self.dollar_entry4.get())
            except ValueError:
                cost_4 = 0
                self.fields['Cost 4'] = ""
            else:
                self.fields['Cost 4'] = "${:,.2f}".format(cost_4)

        if self.fields['Medication Names 5'] == "":
            cost_5 = 0
            self.fields['Cost 5'] = ""
        else:
            try:
                cost_5 = float(self.dollar_entry5.get())
            except ValueError:
                cost_5 = 0
                self.fields['Cost 5'] = ""
            else:
                self.fields['Cost 5'] = "${:,.2f}".format(cost_5)

        total = cost_1 + cost_2 + cost_3 + cost_4 + cost_5
        self.total_num_label.config(text="${:,.2f}".format(total))
        self.fields['Total'] = "${:.2f}".format(total)

        try:
            if self.fields['Credit Card No'][0] == '3':
                amex_img = self.tk_images["amex"]
                self.card_button.config(image=amex_img)
                self.fields |= {
                'Visa': '',
                'MasterCard': '',
                'Discover': '',
                'AMEX': 'X',
                }
            elif self.fields['Credit Card No'][0] == '4':
                visa_img = self.tk_images["visa"]
                self.card_button.config(image=visa_img)
                self.fields |= {
                'Visa': 'X',
                'MasterCard': '',
                'Discover': '',
                'AMEX': '',
                }
            elif self.fields['Credit Card No'][0] == '5':
                mastercard_img = self.tk_images["mastercard"]
                self.card_button.config(image=mastercard_img)
                self.fields |= {
                'Visa': '',
                'MasterCard': 'X',
                'Discover': '',
                'AMEX': '',
                }
            elif self.fields['Credit Card No'][0] == '6':
                discover_img = self.tk_images["discover"]
                self.card_button.config(image=discover_img)
                self.fields |= {
                'Visa': '',
                'MasterCard': '',
                'Discover': 'X',
                'AMEX': '',
                }
        except IndexError:
            generic_card_img = self.tk_images["generic_card"]
            self.card_button.config(image=generic_card_img)
            self.fields |= {
                'Visa': '',
                'MasterCard': '',
                'Discover': '',
                'AMEX': '',
            }

        self.cc_length_check()
        self.cvv_length_check()
        self.expiration_check()
        self.highlight_add_notes_button()

        self.top.after(ms=50, func=self.update_fields)

    def export_pdf(self):
        """Outputs payment information into a PDF form."""

        name_list = self.fields['Cardholder Name'].split()
        formatted_name = ""
        for name in name_list:
            formatted_name += name.lower()
            formatted_name += "_"
        formatted_name += self.fields['MRN']
        formatted_file_name = f"{formatted_name}.pdf"

        if getattr(sys, 'frozen', False):
            app_path = os.path.dirname(sys.executable)
        else:
            app_path = os.path.dirname(os.path.abspath(__file__))

        abs_path = f"{app_path}\.tmp"
        check_folder = os.path.isdir(abs_path)
        if not check_folder:
            os.makedirs(abs_path)
            subprocess.call(["attrib", "+h", abs_path]) # hidden directory

        reader = PdfReader("assets/form/cardpayment.pdf")
        writer = PdfWriter()
        page = reader.pages[0]
        writer.add_page(page)
        writer.update_page_form_field_values(writer.pages[0], self.fields)
        with open(f".tmp\{formatted_file_name}", "wb") as output_stream:
            writer.write(output_stream)

        self.clear_entries()
        os.startfile(f"{app_path}\.tmp\{formatted_file_name}", "print")

    def clear_entries(self):
        """Clear all entries."""

        self.cc_entry.delete(0, END)
        self.exp_entry.delete(0, END)
        self.cvv_entry.delete(0, END)
        self.cardholder_entry.delete(0, END)
        self.mrn_entry.delete(0, END)
        self.med_entry1.delete(0, END)
        self.med_entry2.delete(0, END)
        self.med_entry3.delete(0, END)
        self.med_entry4.delete(0, END)
        self.med_entry5.delete(0, END)
        self.dollar_entry1.delete(0, END)
        self.dollar_entry2.delete(0, END)
        self.dollar_entry3.delete(0, END)
        self.dollar_entry4.delete(0, END)
        self.dollar_entry5.delete(0, END)
        self.notes_text.delete(1.0, END)

    def message_box(self, event):
        """Prompt user for confirmation when 'Done' button is clicked."""

        answer = messagebox.askyesno(
            title="Confirm", message="Are you sure?", parent=self.top)

        if answer:
            self.export_pdf()
            self.cc_entry.focus_set()
            self.clear_entries()

    def open_directory(self):
        """Opens directory containing exported credit card forms."""

        if getattr(sys, 'frozen', False):
            app_path = os.path.dirname(sys.executable)
        else:
            app_path = os.path.dirname(os.path.abspath(__file__))

        abs_path = f"{app_path}\.tmp"
        check_folder = os.path.isdir(abs_path)
        if not check_folder:
            os.makedirs(abs_path)
            subprocess.call(["attrib", "+h", abs_path]) # hidden directory

        subprocess.Popen(f'explorer "{abs_path}"')

    def remove_files(self):
        """Remove files in .tmp older than 7 days."""
        
        current_time = time.time()

        if getattr(sys, 'frozen', False):
            app_path = os.path.dirname(sys.executable)
        else:
            app_path = os.path.dirname(os.path.abspath(__file__))

        abs_path = f"{app_path}\.tmp"
        check_folder = os.path.isdir(abs_path)
        if not check_folder:
            os.makedirs(abs_path)
            subprocess.call(["attrib", "+h", abs_path]) # hidden directory

        for f in os.listdir(path=abs_path):
            file_path = os.path.join(abs_path, f)
            creation_time = os.path.getctime(file_path)
            if (current_time - creation_time) // (24 * 3600) >= 7:
                os.unlink(file_path)

        self.top.after(ms=3_600_000, func=self.remove_files) # after 1 hour

    def toggle_notes_window(self, event):
        """Toggles Note window for CardPayment Form."""

        if self.notes_isHidden:
            self.notes_window.withdraw()
            self.notes_isHidden = False
            self.top.lift()
            self.top.attributes('-disabled', 0)
            self.top.focus_force()
        else:
            # Center Notes window to Top window
            top_x = self.top.winfo_x()
            top_y = self.top.winfo_y()
            top_width = self.top.winfo_reqwidth()
            top_height = self.top.winfo_reqheight()
            notes_width = self.notes_window.winfo_reqwidth()
            notes_height = self.notes_window.winfo_reqheight()
            dx = int((top_width / 2) - (notes_width / 2))
            dy = int((top_height / 2) - (notes_height / 2))
            self.notes_window.geometry('+%d+%d' % (top_x + dx, top_y + dy))

            self.notes_isHidden = True
            self.top.attributes('-disabled', 1)
            self.notes_window.wm_transient(self.top)
            self.notes_window.attributes('-topmost', 1)
            self.notes_window.deiconify()
            self.notes_text.focus()

    def clear_notes(self, event):
        """Clear all text inside Notes text box."""
        self.notes_text.delete(1.0, END)

    def highlight_add_notes_button(self):
        """Highlight Add Notes button if there are notes in text box."""
        if len(self.notes_text.get(1.0, 'end-1c').lstrip()) == 0:
            self.notes_button.config(bg=WINDOW_BG, activebackground=WINDOW_BG)
        else:
            self.notes_button.config(bg='lemon chiffon', activebackground='lemon chiffon')


if __name__ == '__main__':
    root = Tk()
    cp = CardPayment()

    root.mainloop()
