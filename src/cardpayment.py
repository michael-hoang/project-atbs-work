"""This module contains a class that represents a card payment form GUI."""

import json
import os
import subprocess
import sys
import time
import datetime as dt
import tkinter as tk
import ttkbootstrap as tkb
import win32api

from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.tooltip import ToolTip
from tkinter.ttk import Style
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import BooleanObject, NameObject, NumberObject, IndirectObject
from settings import Settings
from dateutil.relativedelta import relativedelta

from refill import Refill
from wrapup import WrapUp
from encryption import MyEncryption
from reprint import Reprint


DAYS_EXPIRATION = 1
SECONDS_PER_DAY = 86400


class CardPayment(tkb.Labelframe):
    """
    Card Payment Form interface to automate printing of filled credit card forms.
    """

    def __init__(self,root, master):
        super().__init__(master, text='', padding=15)
        
        self.style = Style()
        self.style.configure('TButton', font=('', 9, ''))
        self.root = root
        self.encryption = MyEncryption()

        self.check_user_settings_json()

        # Form variables
        self.card_no = tkb.StringVar(value='')
        self.exp = tkb.StringVar(value='')
        self.security_no = tkb.StringVar(value='')
        self.address = tkb.StringVar(value='')
        self.zip = tkb.StringVar(value='')
        self.cardholder = tkb.StringVar(value='')
        self.mrn = tkb.StringVar(value='')
        self.med_1 = tkb.StringVar(value='')
        self.med_2 = tkb.StringVar(value='')
        self.med_3 = tkb.StringVar(value='')
        self.med_4 = tkb.StringVar(value='')
        self.med_5 = tkb.StringVar(value='')
        self.price_1 = tkb.StringVar(value='')
        self.price_2 = tkb.StringVar(value='')
        self.price_3 = tkb.StringVar(value='')
        self.price_4 = tkb.StringVar(value='')
        self.price_5 = tkb.StringVar(value='')
        
        # Trace
        self.price_1.trace('w', self.update_total)
        self.price_2.trace('w', self.update_total)
        self.price_3.trace('w', self.update_total)
        self.price_4.trace('w', self.update_total)
        self.price_5.trace('w', self.update_total)
        self.card_no.trace('w', self.limit_card_number_size)
        self.security_no.trace('w', self.limit_sec_code_len)

        # Images
        image_files = {
            'AMEX': './assets/img/ae.png',
            'Discover': './assets/img/di.png',
            'MasterCard': './assets/img/mc.png',
            'Visa': './assets/img/vi.png',
        }

        self.photoimages = []
        for key, val in image_files.items():
            self.photoimages.append(tkb.PhotoImage(name=key, file=val))

        # Form entries
        self.create_entries_column().pack(side=TOP, fill=X, expand=YES, pady=5)
        self.create_card_info_entries().pack(side=LEFT, fill=X, expand=YES, pady=5, padx=(18,0))

        # Buttons
        self.create_buttonbox().pack(side=LEFT, fill=Y, padx=(18, 0), pady=(0, 1))

        # Event bindings
        self.cardnumber.winfo_children()[1].bind('<BackSpace>', self._do_backspace)
        self.cardnumber.winfo_children()[1].bind('<Key>', self._check_card_number_format)
        self.cardnumber.winfo_children()[1].bind('<KeyRelease>', self._delete_non_numeric_char)
        self.security_ent.winfo_children()[1].bind('<KeyRelease>', self._delete_non_numeric_char_for_sec_code)
        root.bind('<Control-Return>', self.submit_message_box)
        # root.bind('<Control-s>', self.toggle_settings_window)
        root.bind('<Control-n>', self.toggle_notes_window)
        root.bind('<Control-s>', self.toggle_settings_window)
        root.bind('<Control-r>', self.toggle_reprint_window)
   
        # Register validation callbacks
        self.valid_card_func = root.register(self._validate_card_number)
        self.valid_digit_func = root.register(self._validate_only_digits)
        self.valid_exp_func = root.register(self._validate_exp_date)
        self.valid_sec_code_func = root.register(self._validate_security_code)

        # Validate numeric entries
        self.cardnumber.winfo_children()[1].configure(validate='focus', validatecommand=(self.valid_card_func, '%P'))
        self.exp_ent.winfo_children()[1].configure(validate='focus', validatecommand=(self.valid_exp_func, '%P'))
        self.zipcode.winfo_children()[1].configure(validate='key', validatecommand=(self.valid_digit_func, '%P'))
        self.mrn_ent.winfo_children()[1].configure(validate='key', validatecommand=(self.valid_digit_func, '%P'))
        self.security_ent.winfo_children()[1].configure(validate='focus', validatecommand=(self.valid_sec_code_func, '%P'))

        # Initialize Settings window
        self.settings = self.create_settings_window()
        self.settings._check_always_on_top()

        self.set_user_settings()

        # Notes window
        self.create_notes_window()

        # Reprint window
        self.create_reprint_window()

        self.refill_mode_instantiated = False
        if self.settings.current_settings['mode'] == 'Payment':
            self.grid(padx=5, pady=(0, 5))
        elif self.settings.current_settings['mode'] == 'Refill':
            self.set_refill_mode(self.root)
            self.refill_mode_instantiated = True

        # After method
        self._remove_files()
        self.after(ms=300_000, func=self._remove_files) # after 5 minutes

    def create_long_form_entry(self, master, label, variable):
        """Create a single long form entry."""
        container = tkb.Frame(master)
        lbl = tkb.Label(container, text=label, width=25, font=('', 9, ''))
        lbl.pack(side=TOP, anchor='w')
        ent = tkb.Entry(container, textvariable=variable, width=25, font=('', 9, ''))
        ent.pack(side=LEFT, fill=X, expand=YES)
        return container

    def create_short_form_entry(self, master, label, variable):
        """Create a single short form entry."""
        container = tkb.Frame(master)
        lbl = tkb.Label(container, text=label, width=13, font=('', 9, ''))
        lbl.pack(side=TOP, anchor='w')
        ent = tkb.Entry(container, textvariable=variable, width=8, font=('', 9, ''))
        ent.pack(side=LEFT, fill=X, expand=YES)
        return container

    def create_card_info_entries(self):
        """Create card payment information entries."""
        container = tkb.Frame(self)
        grid_para = {'pady': (4,0), 'sticky': 'w'}
        self.cardnumber = self.create_long_form_entry(container, 'Card Number', self.card_no)
        self.cardnumber.grid(column=0, row=0, columnspan=2, sticky='w')
        card_img = self.create_card_image(container)
        card_img.grid(column=1, row=0, sticky='e', padx=2, pady=(20,0))
        self.exp_ent = self.create_short_form_entry(container, 'Exp', self.exp)
        self.exp_ent.grid(column=0, row=1, **grid_para)
        self.security_ent = self.create_short_form_entry(container, 'Security Code', self.security_no)
        self.security_ent.grid(column=1, row=1, **grid_para)
        cardholder = self.create_long_form_entry(container, 'Cardholder Name', self.cardholder)
        cardholder.grid(column=0, row=2, columnspan=2, **grid_para)
        address = self.create_long_form_entry(container, 'Billing Address', self.address)
        address.grid(column=0, row=3, columnspan=2, **grid_para)
        self.zipcode = self.create_short_form_entry(container, 'Zip Code', self.zip)
        self.zipcode.grid(column=0, row=4, columnspan=2, **grid_para)
        self.mrn_ent = self.create_short_form_entry(container, 'MRN', self.mrn)
        self.mrn_ent.grid(column=1, row=4, columnspan=2, **grid_para)
        return container

    def create_list_entry(self, master, item_label, item_var, price_var):
        """Create a single item form entry."""
        container = tkb.Frame(master)
        container.pack(fill=X, expand=YES)
        item_lbl = tkb.Label(container, text=item_label, width=2, anchor='e', font=('', 9, ''))
        item_lbl.pack(side=LEFT, padx=(0,3))
        item_ent = tkb.Entry(container, textvariable=item_var, width=25, font=('', 9, ''))
        item_ent.pack(side=LEFT, fill=X, expand=YES)
        price_lbl = tkb.Label(container, text='$', width=2, anchor='e', font=('', 9, ''))
        price_lbl.pack(side=LEFT, padx=(0,3))
        price_ent = tkb.Entry(container, textvariable=price_var, width=10, font=('', 9, ''))
        price_ent.pack(side=LEFT, fill=X, expand=YES)

    def create_entries_column(self):
        """Create a list column of 5 entries."""
        container = tkb.Frame(self)
        self.create_list_header(container)
        self.create_list_entry(container, '1.', self.med_1, self.price_1)
        self.create_list_entry(container, '2.', self.med_2, self.price_2)
        self.create_list_entry(container, '3.', self.med_3, self.price_3)
        self.create_list_entry(container, '4.', self.med_4, self.price_4)
        self.create_list_entry(container, '5.', self.med_5, self.price_5)
        return container
    
    def create_list_header(self, master):
        """Create labels for the list header."""
        container = tkb.Frame(master)
        container.pack(fill=X, expand=YES)
        item_col_lbl = tkb.Label(container, text='Medication', font=('', 9, ''))
        item_col_lbl.pack(side=LEFT, padx=(70,0))
        price_col_lbl = tkb.Label(container, text='Price', font=('', 9, ''))
        price_col_lbl.pack(side=RIGHT, padx=(0,25))

    def create_card_image(self, master):
        """Create card network image."""
        container = tkb.Frame(master)
        self.image_lbl = tkb.Label(container, image='', border=0)
        self.image_lbl.pack()
        return container
    
    def create_buttonbox(self):
        """Create the application buttonbox."""
        container = tkb.Frame(self)
        self.total_lbl = tkb.Label(container, text='$0.00', width=12, anchor='center', font=('', 9, ''))
        self.total_lbl.pack(side=TOP)

        self.sub_btn = tkb.Button(
            master=container,
            text="Submit",
            command=lambda: self.submit_message_box(e=None),
            bootstyle='DEFAULT',
            width=9,
            style='TButton',
        )
        self.sub_btn.pack(side=BOTTOM, pady=(0,4))
        ToolTip(
            widget=self.sub_btn,
            text='<CTRL+ENTER>\nProduce a tangible copy of the payment form onto the designated printing apparatus.',
            delay=500
        )
        
        set_btn = tkb.Button(
            master=container,
            text="Settings",
            command=lambda: self.toggle_settings_window(e=None),
            bootstyle=SECONDARY,
            width=9,
            style='TButton.secondary'
        )
        set_btn.pack(side=BOTTOM, pady=(0,12))
        ToolTip(
            widget=set_btn,
            text='<CTRL+S>\nUnveil the configuration panel.',
            delay=500
        )

        self.reprint_btn = tkb.Button(
            master=container,
            text="Reprint",
            command=lambda: self.toggle_reprint_window(e=None),
            bootstyle=DARK,
            width=9,
            style='TButton.dark'
        )
        self.reprint_btn.pack(side=BOTTOM, pady=(0,12))
        ToolTip(
            widget=self.reprint_btn,
            text="<CTRL+R>\nReproduce the card payment document onto a selected printing apparataus of preference.",
            delay=500
        )

        notes_btn = tkb.Button(
            master=container,
            text="Notes",
            command=lambda: self.toggle_notes_window(e=None),
            bootstyle=DARK,
            width=9,
            style='TButton.dark'
        )
        notes_btn.pack(side=BOTTOM, pady=(0,12))
        ToolTip(
            widget=notes_btn,
            text="<CTRL+N>\nUnfurl the memorandum casement to inscribe thoughts concerning the intelligence of payment.",
            delay=500
        )

        clear_btn = tkb.Button(
            master=container,
            text='Clear',
            command=self.confirm_clear,
            bootstyle=DARK,
            width=9,
            style='TButton.dark'
        )
        clear_btn.pack(side=BOTTOM, pady=(0, 12))
        ToolTip(
            widget=clear_btn,
            text="Obliterate all the inscriptions in the fields of the card payment application.",
            delay=500
        )

        return container
    
    def get_total(self) -> float:
        """Calculate the total cost of medications."""
        prices = (self.price_1, self.price_2, self.price_3, self.price_4, self.price_5)
        total = 0
        for price in prices:
            try:
                total += float(price.get().replace(',', ''))
            except ValueError:
                continue
        
        return total
    
    def update_total(self, *args):
        """Update the total string variable."""
        self.total_lbl['text'] = "${:,.2f}".format(self.get_total())
    
    def _get_dict_fields(self) -> dict:
        """Get a Python dictionary of field names and text values for PdfWriter."""
        dict_fields = {
            'Date': dt.datetime.today().strftime('%m-%d-%Y'),
            'Visa': '',
            'MasterCard': '',
            'Discover': '',
            'AMEX': '',
            'Credit Card No': self.card_no.get(),
            'Exp': self.exp.get(),
            'Security No': self.security_no.get(),
            'Billing Address': self.address.get(),
            'Zip Code': self.zip.get(),
            'Cardholder Name': self.cardholder.get(),
            'MRN': self.mrn.get(),
            'Medication Names 1': self.med_1.get(),
            'Medication Names 2': self.med_2.get(),
            'Medication Names 3': self.med_3.get(),
            'Medication Names 4': self.med_4.get(),
            'Medication Names 5': self.med_5.get(),
            'Cost': self.price_1.get(),
            'Cost 2': self.price_2.get(),
            'Cost 3': self.price_3.get(),
            'Cost 4': self.price_4.get(),
            'Cost 5': self.price_5.get(),
            'Total': '${:.2f}'.format(self.get_total()),
            'Notes': self.notes_text_box.get(1.0, 'end-1c'), # -1c removes the added newline
        }
        try:
            cardnumber = dict_fields['Credit Card No'].replace(' ', '')
            if self.luhns_algo(cardnumber):
                dict_fields[self.get_credit_card_network(cardnumber)] = 'X'
        except:
            pass

        return dict_fields
    
    def confirm_clear(self):
        """Confirmation window for clearing all entries."""
        confirm = Messagebox.yesno(
            parent=self,
            title='Confirm Clear',
            message="Select 'Yes' to clear all entries."
        )

        if confirm == 'Yes':
            self.clear_all_entries()
            self.focus_force()
    
    def submit_message_box(self, e):
        """Prompt user for confirmation when 'Submit' button is pressed."""
        answer = Messagebox.yesno(
            parent=self,
            title='Confirm Submit',
            message='Are you sure you want to submit?'
        )
        if answer == 'Yes':
            data = self._create_data_structure()
            reference_id = list(data.keys())[0]
            fields = data[reference_id]['fields']
            self._export_to_json(data)
            pdf_file_path = self.write_pdf(reference_id, fields)
            self._print_default(pdf_file_path)
            self.clear_all_entries()
            self.sub_btn.config(text='Printing...')
            self.sub_btn.after(5000, lambda: self.sub_btn.config(text='Submit'))
            self.focus_force()

    def _get_epoch_creation_time(self) -> int:
        """Return the current epoch time."""
        epoch_current_time = int(time.time())
        return epoch_current_time
    
    def _format_epoch_time(self, epoch_time: int) -> str:
        """Format epoch time into 24H format without colons."""
        dt_obj = dt.datetime.fromtimestamp(epoch_time)
        time_str = dt_obj.strftime('%H%M%S')
        return time_str

    def _generate_reference_id(self, cardholder, mrn, ctime ) -> str:
        """Generate a reference ID for the card payment information."""
        fmt_ctime = self._format_epoch_time(ctime)
        cardholder_split = cardholder.split()
        try:
            reference_id = f'{fmt_ctime}-{mrn}-{cardholder_split[0].lower()}'
        except:
            reference_id = f'{fmt_ctime}-{mrn}'

        return reference_id

    def _create_data_structure(self) -> dict:
        """Create data structure to store information."""
        fields = self._get_dict_fields()
        cardholder = fields['Cardholder Name']
        mrn = fields['MRN']
        ctime = self._get_epoch_creation_time()
        reference_id = self._generate_reference_id(cardholder, mrn, ctime)

        data = {
            reference_id: {
                'epoch_ctime': ctime,
                'fields': fields
            }
        }

        return data
    
    def _encrypt_data(self, data) -> dict:
        """Encrypt data using MyEncryption."""
        encrypted_data = {}
        for ref_id in data:
            encrypted_ref_id = self.encryption.encrypt(ref_id)
            epoch_ctime = data[ref_id]['epoch_ctime']
            encrypted_data[encrypted_ref_id] = {
                'epoch_ctime': epoch_ctime,
                'fields': {}
            }
            fields = data[ref_id]['fields']
            for k, v in fields.items():
                encrypted_k = self.encryption.encrypt(k)
                encrypted_v = self.encryption.encrypt(v)
                encrypted_data[encrypted_ref_id]['fields'][encrypted_k] = encrypted_v

        return encrypted_data
              
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

    def _export_to_json(self, new_data):
        """Export data to json file."""
        data_dir_path = self._get_abs_path_to_data_directory()
        json_file_path = os.path.join(data_dir_path, 'data.json')
        encrypted_data = self._encrypt_data(new_data)
        # If json file exists
        if os.path.isfile(json_file_path):
            with open(json_file_path, 'r') as f:
                data = json.load(f) 
        
            data.update(encrypted_data)
            with open(json_file_path, 'w') as f:
                json.dump(data, f, indent=4)
        else:
            with open(json_file_path, 'w') as f:
                json.dump(encrypted_data, f, indent=4)
            
        
    def _set_need_appearances_writer(self, writer: PdfWriter):
        """
        Enables PDF filled form values to be visible on the final PDF results

        NOTE: See 12.7.2 and 7.7.2 for more information:
        http://www.adobe.com/content/dam/acom/en/devnet/acrobat/pdfs/PDF32000_2008.pdf
        """
        try:
            catalog = writer._root_object
            # get the AcroForm tree
            if "/AcroForm" not in catalog:
                writer._root_object.update({
                    NameObject("/AcroForm"): IndirectObject(len(writer._objects), 0, writer)
                })

            need_appearances = NameObject("/NeedAppearances")
            writer._root_object["/AcroForm"][need_appearances] = BooleanObject(True)
            return writer

        except Exception as e:
            print('set_need_appearances_writer() catch : ', repr(e))
            return writer

    def write_pdf(self, reference_id, fields) -> str:
        """
        Export payment information into a temporary PDF file and return the file path.
        """
        file_name = f'{reference_id}.pdf'
        if getattr(sys, 'frozen', False):
            app_path = os.path.dirname(sys.executable)
        else:
            app_path = os.path.dirname(os.path.abspath(__file__))

        abs_path = f"{app_path}\.tmp"
        check_folder = os.path.isdir(abs_path)
        if not check_folder:
            os.makedirs(abs_path)
            subprocess.call(["attrib", "+h", abs_path]) # hidden directory

        reader = PdfReader(open("assets/form/cardpayment-form.pdf", "rb"), strict=False)
        if "/AcroForm" in reader.trailer["/Root"]:
            reader.trailer["/Root"]["/AcroForm"].update(
                {NameObject("/NeedAppearances"): BooleanObject(True)}
            )
            
        writer = PdfWriter()
        self._set_need_appearances_writer(writer)
        if "/AcroForm" in writer._root_object:
            writer._root_object["/AcroForm"].update(
                {NameObject("/NeedAppearances"): BooleanObject(True)}
            )

        page = reader.pages[0]
        writer.add_page(page)
        writer.update_page_form_field_values(writer.pages[0], fields)

        # flatten pdf
        writer_page = writer.get_page(0)
        for annotation_index in range(0, len(writer_page["/Annots"])):
            writer_annot = writer_page["/Annots"][annotation_index].get_object()
            writer_annot.update({NameObject("/Ff"): NumberObject(1)})
            
        with open(f".tmp\{file_name}", "wb") as output_stream:
            writer.write(output_stream)

        return f"{app_path}\.tmp\{file_name}"

    def _print_default(self, file_path):
        """Print to the default printer."""
        os.startfile(file_path, "print")

    def _print_from_selected_printer(self, file_path):
        """Print file from the selected printer."""
        # default_printer = self.reprint._get_default_printer()
        selected_printer = self.reprint.selected_printer.get().strip()
        if selected_printer in self.reprint._get_printer_list():
            # win32print.SetDefaultPrinter(selected_printer)
            # os.startfile(file_path, "print")
            win32api.ShellExecute(0, 'printto', file_path, f'"{selected_printer}"', '.', 0)
            # win32print.SetDefaultPrinter(default_printer)

    def get_credit_card_network(self, numbers: str) -> str or bool:
        """Return AMEX, Discover, MasterCard, Visa, or False."""
        prefix = int(numbers[:2])
        length = len(numbers)
        if prefix > 50 and prefix < 56 and length == 16:
            return 'MasterCard'
        elif (prefix == 34 or prefix == 37) and length == 15:
            return 'AMEX'
        elif numbers[0] == '4' and (length == 13 or length == 16):
            return 'Visa'
        elif numbers[:4] == '6011':
            return 'Discover'
        else:
            return False

    def luhns_algo(self, numbers: str) -> bool:
        """Return True if credit card numbers pass Luhn's Algorithm."""
        sum1 = 0
        sum2 = 0
        for i in range(len(numbers)):
            index = -(i + 1)
            if (index % 2) == 0:
                digit_x2_int = int(numbers[index]) * 2
                digit_x2_str = str(digit_x2_int)
                if len(digit_x2_str) > 1:
                    sum2 += int(digit_x2_str[0]) + int(digit_x2_str[1])
                else:
                    sum2 += digit_x2_int
            else:
                sum1 += int(numbers[index])
        # if the total modulo 10 is congruent to 0
        if (sum1 + sum2) % 10 == 0:
            return True

        return False
    
    def _do_backspace(self, e):
        """Force backspace key to do backspace."""
        cardnumber = self.card_no.get()
        length = len(cardnumber)
        try:
            if cardnumber[-1] != ' ':
                self.cardnumber.winfo_children()[1].delete(length, 'end')
        except:
            pass
    
    def _delete_non_numeric_char(self, e):
        """Delete inputted characters that are non-numeric."""
        cardnumber = self.card_no.get()
        try:
            if not cardnumber[-1].isdigit():
                self.cardnumber.winfo_children()[1].delete(0, 'end')
                self.cardnumber.winfo_children()[1].insert('end', cardnumber[:-1])
        except:
            pass
    
    def _delete_non_numeric_char_for_sec_code(self, e):
        """Delete inputted characters that are non-numeric."""
        sec_code = self.security_no.get()
        try:
            if not sec_code[-1].isdigit():
                self.security_ent.winfo_children()[1].delete(0, 'end')
                self.security_ent.winfo_children()[1].insert('end', sec_code[:-1])
        except:
            pass
    
    def _check_card_number_format(self, e):
        """Format card numbers with spaces. (Ex. #### #### #### ####)"""
        cardnumber = self.card_no.get()
        length = len(cardnumber)
        try:
            if cardnumber[0] in ('4', '5', '6'):
                if length in (4, 9, 14):
                    self.cardnumber.winfo_children()[1].insert('end', ' ')
                if length > 19:
                    self.cardnumber.winfo_children()[1].set(cardnumber[:19])
            elif cardnumber[0] == '3':
                if length in (4, 11):
                    self.cardnumber.winfo_children()[1].insert('end', ' ')
                if length > 17:
                    self.cardnumber.winfo_children()[1].set(cardnumber[:17])
        except:
            pass
        
    def _validate_card_number(self, card_numbers: str) -> bool:
        """Validate that the input is a number and passes Luhn's algorithm."""
        raw_num = card_numbers.replace(' ', '')
        if raw_num.isdigit() and self.luhns_algo(raw_num):
            try:
                self.image_lbl.configure(image = self.get_credit_card_network(raw_num))
            except:
                pass
            return True
        elif card_numbers == '':
            self.image_lbl.configure(image = '')
            return True
        else:
            self.image_lbl.configure(image = '')
            return False
        
    def _validate_only_digits(self, P: str) -> bool:
        """Validate that the input is strictly a digit."""
        if str.isdigit(P) or P == "":
            return True
        else:
            return False
        
    def _validate_exp_date(self, P: str) -> bool:
        """Validate that the inputted date is not expired."""
        exp_str = P
        date_fmt = ('%m/%y', '%m-%y', '%m/%Y', '%m-%Y')
        for fmt in date_fmt:
            try:
                exp_date = dt.datetime.strptime(exp_str, fmt) + relativedelta(months=1) - relativedelta(days=1)
                if exp_date > dt.datetime.today():
                    return True
            except ValueError:
                pass

        if exp_str == '':
            return True
        else:
            return False
        
    def _validate_security_code(self, P: str) -> bool:
        """Validate that the data is strictly a digit, and is only 3 or 4 chars long."""
        sec_code = P
        try:
            first_digit = self.card_no.get()[0]
            sec_code_len = len(sec_code)
            for c in sec_code:
                if not c.isdigit():
                    return False
                
            if first_digit != '3':
                if sec_code_len == 3 or sec_code == '':
                    return True
                return False
            elif first_digit == '3':
                if sec_code_len == 4 or sec_code == '':
                    return True
                return False
        except:
            pass
        if sec_code == '':
            return True
        else:
            return False
        
    def limit_sec_code_len(self, *args):
        """Limit the number of characters depending on card network type"""
        try:
            first_digit = self.card_no.get()[0]
            sec_code = self.security_no.get()
            sec_code_len = len(sec_code)
            if first_digit != '3' and sec_code_len > 3:
                self.security_ent.winfo_children()[1].delete(0, 'end')
                self.security_ent.winfo_children()[1].insert('end', sec_code[:3])
            elif first_digit == '3' and sec_code_len > 4:
                self.security_ent.winfo_children()[1].delete(0, 'end')
                self.security_ent.winfo_children()[1].insert('end', sec_code[:4])
        except IndexError:
            pass
            
    def limit_card_number_size(self, *args):
        """Limit the number of characters depending on card network type"""
        cardnumber = self.card_no.get()
        length = len(cardnumber)
        try:
            if cardnumber[0] in ('4', '5', '6'):
                if length > 19:
                    self.cardnumber.winfo_children()[1].delete(0, 'end')
                    self.cardnumber.winfo_children()[1].insert('end', cardnumber[:19])
            elif cardnumber[0] == '3':
                if length > 17:
                    self.cardnumber.winfo_children()[1].delete(0, 'end')
                    self.cardnumber.winfo_children()[1].insert('end', cardnumber[:17])
            else:
                self.cardnumber.winfo_children()[1].delete(0, 'end')
        except:
            pass

    def _get_fields_from_json(self, reference_id) -> dict:
        """Return saved fields data from data.json."""
        data_dir_path = self._get_abs_path_to_data_directory()
        json_file_path = os.path.join(data_dir_path, 'data.json')
        with open(json_file_path, 'r') as f:
            data = json.load(f)

        decrypted_data = self._decrypt_data(data)
        fields = decrypted_data[reference_id]['fields']
        return fields
    
    def _delete_expired_items(self):
        """Recursively delete expired items from data.json."""
        if not self.reprint_isHidden:
            data_dir_path = self._get_abs_path_to_data_directory()
            json_file_path = os.path.join(data_dir_path, 'data.json')
            try:
                with open(json_file_path, 'r') as f:
                    data = json.load(f)

                decrypted_data = self._decrypt_data(data)
                current_epoch_time = time.time()
                to_be_deleted = []
                for ref_id in decrypted_data:
                    epoch_ctime = decrypted_data[ref_id]['epoch_ctime']
                    if (current_epoch_time - epoch_ctime) / SECONDS_PER_DAY >= DAYS_EXPIRATION:
                        to_be_deleted.append(ref_id)

                for ref_id in to_be_deleted:
                    del decrypted_data[ref_id]

                # Write updated data to json file
                encrypted_data = self._encrypt_data(decrypted_data)
                with open(json_file_path, 'w') as f:
                    json.dump(encrypted_data, f, indent=4)
            except:
                pass
            self.reprint._refresh_treeview()
            self.reprint_window.after(1000, self._delete_expired_items)

    def reprint_command(self):
        """Reprint the selected item from Treeview window."""
        try:
            reference_id = self.reprint._get_reference_id()
            if reference_id:
                fields = self._get_fields_from_json(reference_id)
                pdf_file_path = self.write_pdf(reference_id, fields)
                self._print_from_selected_printer(pdf_file_path)
                self.reprint.button.config(text='Printing...')
                self.reprint.button.after(
                    5000, lambda: self.reprint.button.config(text='Print')
                )
        except:
            pass

    def create_reprint_window(self):
        """Open Treeview window for reprinting."""
        self.reprint_window = tkb.Toplevel(
            title='Reprint',
            resizable=(False, False)
        )
        self.reprint_window.withdraw()
        self.reprint = Reprint(self.reprint_window, self.reprint_command)
        self.reprint_isHidden = True
        self.reprint_window.protocol(
            'WM_DELETE_WINDOW', lambda: self.toggle_reprint_window(e=None)
        )
        self.reprint_window.bind('<Escape>', self.toggle_reprint_window)

    def toggle_reprint_window(self, e):
        """Toggle Reprint window."""
        if not self.reprint_isHidden:
            self.reprint_isHidden = True
            self.lift()
            self.root.attributes('-disabled', 0)
            self.focus()
            self.reprint_window.withdraw()
        else:
            self.reprint_isHidden = False
            self._delete_expired_items()
            self.center_child_to_parent(self.reprint_window, self.root, 'reprint')
            self.root.attributes('-disabled', 1)
            self.reprint_window.attributes('-topmost', 1)
            self.reprint_window.deiconify()
            self.reprint_window.focus()

    def clear_all_entries(self):
        """Clear all entries on the form."""
        outer_containers = self.winfo_children()
        for outer_container in outer_containers:
            inner_containers = outer_container.winfo_children()
            for inner_container in inner_containers:
                if inner_container.winfo_class() == 'TFrame':
                    entry_widgets = inner_container.winfo_children()
                    for entry_widget in entry_widgets:
                        if entry_widget.winfo_class() == 'TEntry':
                            entry_widget.delete(0, 'end')
        self.notes_text_box.delete(1.0, END)
        self.cardnumber.winfo_children()[1].focus_force()
        self.exp_ent.winfo_children()[1].focus_force()
        self.security_ent.winfo_children()[1].focus_force()              

    def center_child_to_parent(self, child, parent, window_name):
        """Center child window to parent window."""
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_reqwidth()
        parent_height = parent.winfo_reqheight()
        child_width = child.winfo_reqwidth()
        child_height = child.winfo_reqwidth()
        if window_name == 'notes':
            dx = int((parent_width / 2)) - 120
            dy = int((parent_height / 2)) - 75
        elif window_name == 'settings':
            dx = int((parent_width / 2)) - child_width / 2
            dy = int((parent_height / 2)) - child_height / 2 - 160
        elif window_name == 'reprint':
            dx = int((parent_width / 2)) - child_width / 2
            dy = int((parent_height / 2)) - child_height / 2 + 100
        child.geometry('+%d+%d' % (parent_x + dx, parent_y + dy))

    def create_notes_window(self):
        """Create Notes window."""
        self.notes_window = tkb.Toplevel(self)
        self.notes_isHidden = True
        self.toggle_notes_window(e=None)
        self.notes_window.title('Notes')
        self.notes_window.geometry('240x150')
        self.notes_window.resizable(False, False)
        # self.notes_window.overrideredirect(True)
        self.notes_text_box = tk.Text(self.notes_window, font=('Sergoe UI', 14, 'normal'), wrap=WORD)
        self.notes_text_box.pack(expand=YES)
        
        self.notes_window.protocol('WM_DELETE_WINDOW', lambda: self.toggle_notes_window(e=None))
        self.notes_window.bind('<Escape>', self.toggle_notes_window)
        

    def toggle_notes_window(self, e):
        """Toggle Notes window."""
        if self.notes_isHidden:
            self.notes_isHidden = False
            self.lift()
            self.root.attributes('-disabled', 0)
            self.focus()
            self.notes_window.withdraw()
        else:
            self.center_child_to_parent(self.notes_window, self.root, 'notes')
            self.notes_isHidden = True
            self.root.attributes('-disabled', 1)
            self.notes_window.attributes('-topmost', 1)
            self.notes_window.deiconify()
            self.notes_text_box.focus()
            

    def create_settings_window(self):
        """"Create the settings window."""
        self.settings_window = tkb.Toplevel(self)
        self.settings_isHidden = True
        self.toggle_settings_window(e=None)
        self.settings_window.title('Settings')
        self.settings_window.resizable(False, False)
        # self.settings_window.overrideredirect(True)
        settings = Settings(self.settings_window, self)
        self.settings_window.protocol('WM_DELETE_WINDOW', func=lambda: self.toggle_settings_window(e=None))
        self.settings_window.bind('<Escape>', self.toggle_settings_window)
        return settings
    
    def toggle_settings_window(self, e):
        """Toggle Settings window."""
        if self.settings_isHidden:
            self.settings_isHidden = False
            self.lift()
            self.root.attributes('-disabled', 0)
            self.focus()
            self.settings_window.withdraw()
            # Revert any unsaved changes to settings
            try:
                self.set_user_settings()
            except AttributeError:
                pass

        else:
            # self.settings_window.place_window_center()
            self.center_child_to_parent(self.settings_window, self.root, 'settings')
            self.settings_isHidden = True
            self.root.attributes('-disabled', 1)
            self.settings_window.attributes('-topmost', 1)
            self.settings_window.deiconify()
            self.settings_window.focus()

    def _remove_files(self):
        """Remove files in .files older than 7 days."""
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
            os.unlink(file_path)

        self.after(ms=300_000, func=self._remove_files) # after 5 minutes
    
    # Settings methods

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
    
    def _check_data_directory_path(self):
        """Create '.data' hidden directory if it doesn't exist."""
        directory_abs_path = self._get_abs_path_to_data_directory()
        if not os.path.isdir(directory_abs_path):
            os.makedirs(directory_abs_path)
            # make directory hidden
            subprocess.call(["attrib", "+h", directory_abs_path])
    
    def _create_settings_json_file(self, file_path: str):
        """Create settings.json."""
        default_settings = {
            'always_on_top': 'no',
            'user': '',
            'mode': 'Payment',
            'theme': 'cosmo',
        }
        with open(file_path, 'w') as f:
            data = json.dumps(default_settings, indent=4)
            f.write(data)

    def _check_settings_json_path(self):
        """Create 'settings.json' file if it doesn't exist."""
        settings_json_path = self._get_settings_json_path()
        if not os.path.isfile(settings_json_path):
            self._create_settings_json_file(settings_json_path)

    def check_user_settings_json(self):
        """Ensures settings.json file exists."""
        self._check_data_directory_path()
        self._check_settings_json_path()

    def _read_settings_json_file(self) -> dict:
        """Read the 'settings.json' file."""
        settings_json_path = self._get_settings_json_path()
        with open(settings_json_path, 'r') as f:
            data = json.load(f)
        
        return data

    def _set_always_on_top_setting(self, user_settings: dict):
        """Configure always on top setting."""
        if user_settings['always_on_top'] == 'yes':
            self.root.attributes('-topmost', 1)
            self.settings.always_top_int_var.set(1)
            self.settings.current_settings['always_on_top'] = 'yes'
        else:
            self.root.attributes('-topmost', 0)
            self.settings.always_top_int_var.set(0)
            self.settings.current_settings['always_on_top'] = 'no'

    def _set_mode_setting(self, user_settings: dict):
        """Configure mode setting."""
        if user_settings['mode'] == 'Payment':
            self.settings.mode_str_var.set('Payment')
            self.settings.change_user_btn.config(state='disabled')
            self.settings.current_settings['mode'] = 'Payment'
        elif user_settings['mode'] == 'Refill':
            self.settings.mode_str_var.set('Refill')
            self.settings.change_user_btn.config(state='normal')
            self.settings.current_settings['mode'] = 'Refill'

    def _set_theme_setting(self, user_settings: dict):
        """Configure theme setting."""
        theme = user_settings['theme']
        self.root._style.instance.theme_use(theme)
        self.settings.current_settings['theme'] = theme
        self.settings.themes_combobox.set(theme)
        self.style.configure('TLabelframe.Label', font=('', 11, 'bold'))
        self.style.configure('TRadiobutton', font=('', 10, ''))
        self.style.configure('TButton', font=('', 9, ''))
        self.style.configure('Roundtoggle.Toolbutton', font=('', 11, ''))  # broken
        self.style.configure('TNotebook.Tab', font=('', 9, ''))

    def _set_change_user_btn(self, user_settings: dict):
        """Configure Change user button."""
        if self.settings.current_settings['user']:
            self.settings.change_user_btn.config(state='normal')
        
    def set_user_settings(self):
        """Set user settings from settings.json file."""
        user_settings = self._read_settings_json_file()
        self._set_always_on_top_setting(user_settings)
        self._set_mode_setting(user_settings)
        self._set_theme_setting(user_settings)
        self._set_change_user_btn(user_settings)

    # Mode methods

    def set_payment_mode(self):
        """Set the mode to Payment. Used by Settings."""
        try:
            self.refill_frame.grid_remove()
            self.wrapup_frame.grid_remove()
        except:
            pass

        self.root.config(padx=0, pady=0)
        self.config(text='')
        self.grid_configure(padx=5, pady=(0, 5))
        self.root.title('Card Payment Form')

    def set_refill_mode(self, root):
        """Set the mode to Refill."""
        if not self.refill_mode_instantiated:
            self.wrapup_frame = tkb.Labelframe(text='Wrap Up')
            self.wrapup_frame.grid(row=0, column=1, sticky='ew', padx=(20, 0))
            wrapup_inner_frame = tkb.Frame(self.wrapup_frame)
            wrapup_inner_frame.pack()
            self.wrapup = WrapUp(wrapup_inner_frame)
            
            self.refill_frame = tkb.Labelframe(root, text='Refill Coordination')
            self.refill_frame.grid(column=0, row=0, rowspan=2, sticky='')
            self.refill = Refill(root, self.refill_frame, self.wrapup, self.settings, refill_mode=True)

            self.refill_mode_instantiated = True
        else:
            self.refill_frame.grid()
            self.wrapup_frame.grid()

        self.config(text='Card Payment')
        self.grid_configure(row=1, column=1, padx=(20, 0), pady=(20, 0))

        root.config(padx=20, pady=20)
        first = self.settings.current_settings['user']['first_name']
        last = self.settings.current_settings['user']['last_name']
        full = f'{first} {last}'
        root.title(f'Refill Coordination - {full}')
        


if __name__ == '__main__':
    app = tkb.Window(
        'Card Payment Form', 'cosmo', resizable=(False, False)
    )

    cardpayment = CardPayment(app, app)
    app.place_window_center()
    
    # app._style.instance.theme_use('litera')
    app.mainloop()