import datetime as dt
import tkinter as tk
import ttkbootstrap as tkb

from win32 import win32clipboard
from tkinter import WORD
from tkinter.ttk import Style
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip

from dropship import DropShipLookUp


class Refill(tkb.Frame):
    """Refill Coordination form template."""

    def __init__(self, root, master, wrapup, settings, refill_mode=False):
        """Initialize string variables, style, radio button states, and widgets."""
        super().__init__(master)
        self.pack(side=LEFT, fill=BOTH, expand=YES, pady=(10, 0))
        style = Style()
        style.configure('TLabelframe.Label', font=('', 11, 'bold'))
        style.configure('TButton', font=('', 9, ''))
        style.configure('Roundtoggle.Toolbutton', font=('', 11, ''))  # broken
        style.configure('TNotebook.Tab', font=('', 9, ''))

        # Wrap Up object
        self.wrapup = wrapup
        # Settings object
        self.settings = settings

        # Initialize win32clipboard
        self.cf_rtf = win32clipboard.RegisterClipboardFormat('Rich Text Format')

        # Initialize string variables for solid toolbuttons (radiobuttons)
        refill_str_var_list = [
            'medication_name', 'days_on_hand', 'inj_cyc_btn',
            'inj_cyc_start_date', 'dispense_method_btn', 'dispense_date',
            'time_location', 'sig_required_btn', 'dispense_comments',
            'medication_efficacy_btn', 'spoke_with'
        ]

        self.refill_str_vars = {
            str_var: tkb.StringVar() for str_var in refill_str_var_list
        }

        # Initialize Radio Button states to manage selecting/unselecting of
        # solid toolbuttons (radiobuttons)
        self.solid_tool_btn_states = {
            'inj_cyc_btn': {
                'Injection': 0,
                'Cycle': 0,
            },
            'dispense_method_btn': {
                'DCS': 0,
                'FedEx': 0,
                'Pick Up': 0,
                'Walk Over': 0,
            },
            'sig_required_btn': {
                'Yes': 0,
                'No': 0,
            },
            'medication_efficacy_btn': {
                'A lot': 0,
                'A little': 0,
                'Can\'t tell': 0,
            }
        }

        # Initialize integer varaibles for toolbuttons (checkbuttons)
        intervention_int_var_list = [
            'dose_direction_btn', 'medication_profile_btn', 'new_allergies_btn',
            'medical_condition_btn', 'other_changes_btn', 'other_side_effects_btn',
            'injection_site_rxn_btn', 'hospitalized_er_btn'
        ]

        self.intervention_int_vars = {
            int_var: tkb.IntVar() for int_var in intervention_int_var_list
        }

        # Initialize lists to track any changes or symptoms reported
        self.changes = []
        self.symptoms = []

        # Register validation callback
        date_func = root.register(self._validate_date)

        # # Side panel frame
        # side_panel_frame = tkb.Frame(self)
        # side_panel_frame.grid(row=0, column=0, sticky=NSEW)

        # # Side panel buttons
        # refill_btn = self.create_side_panel_btn(side_panel_frame, 'Refill')

        # Main display frame
        main_display_frame = tkb.Frame(self)
        main_display_frame.grid(row=0, column=1, sticky=NSEW, pady=(15, 0))

        # ===== TOOL BUTTONS ===== #

        # Toggle intervention button
        self.intervention_toggle_state = tkb.IntVar()
        intervention_toggle_btn = tkb.Checkbutton(
            master=main_display_frame,
            bootstyle='round-toggle',
            text='Intervention',
            variable=self.intervention_toggle_state,
            command=self.toggle_intervention,
            style='Roundtoggle.Toolbutton'
        )
        intervention_toggle_btn.grid(
            row=0, column=0, padx=(15, 0), pady=(0, 15), sticky='w'
        )
        ToolTip(
            widget=intervention_toggle_btn,
            text='Toggle Intervention',
            delay=500
        )

        # Toggle Reassessment button
        self.reassessment_toggle_state = tkb.IntVar()
        reassessment_toggle_btn = tkb.Checkbutton(
            master=main_display_frame,
            bootstyle='round-toggle',
            text='Reassessment',
            variable=self.reassessment_toggle_state,
            command=None,
            style='Roundtoggle.Toolbutton'
        )
        reassessment_toggle_btn.grid(
            row=0, column=1, padx=(0, 0), pady=(0, 15), sticky='w'
        )

        # Clear button
        clear_btn = tkb.Button(
            master=main_display_frame,
            text='Clear',
            command=self.clear_entries,
            style='TButton',
            width=7
        )
        clear_btn.grid(
            row=0, column=1, rowspan=2, padx=(200, 0), pady=(0, 655)
        )
        ToolTip(clear_btn, 'Clear entries and clipboard', delay=500)

        # ===== NOTEBOOK ===== #

        # Notebook
        self.notebook = tkb.Notebook(main_display_frame, style='TNotebook.Tab')
        self.notebook.grid(row=1, column=0, columnspan=3)
        clear_btn.lift()

        # ========================== REFILL ===================================#

        # Refill display frame (tab)
        self.refill_display_frame = tkb.Frame(
            master=self.notebook,
            padding=20,
        )
        self.refill_display_frame.pack()
        self.notebook.add(self.refill_display_frame, text='Refill')

        # ===== REFILL QUESTIONS ===== #

        # Labelframes
        refill_questions_frame = tkb.Frame(self.refill_display_frame)
        refill_questions_frame.pack(side=TOP)

        medication_labelframe = self.create_labelframe(
            refill_questions_frame, 'Medication', 0
        )
        medication_on_hand_labelframe = self.create_labelframe(
            refill_questions_frame, 'Medication On Hand', 1
        )
        dispense_date_labelframe = self.create_labelframe(
            refill_questions_frame, 'Dispense Date', 2
        )
        medication_efficacy_labelframe = self.create_labelframe(
            refill_questions_frame, 'Medication Efficacy', 3
        )
        spoke_with_labelframe = self.create_labelframe(
            refill_questions_frame, 'Spoke with', 4, sticky='w', padding=False
        )

        self.copy_template_btn = tkb.Button(
            master=refill_questions_frame,
            text='Copy Template',
            command=self.copy_formatted_template_notes,
            state='disabled'
        )
        self.copy_template_btn.grid(
            row=4, column=0, padx=(251, 0), pady=(10, 0), ipady=5
        )
        ToolTip(
            widget=self.copy_template_btn,
            text='Copy Refill Coordination template to clipboard',
            delay=500
        )

        # Medication

        # Row 1
        medication_row_1 = self.create_inner_frame(medication_labelframe)

        self.medication_entry = tkb.Entry(
            master=medication_row_1,
            textvariable=self.refill_str_vars['medication_name']
        )
        self.medication_entry.pack(fill=BOTH)
        ToolTip(
            widget=self.medication_entry,
            text='Enter medication name',
            delay=500
        )

        # Medication on hand

        # Row 1
        medication_on_hand_row_1 = self.create_inner_frame(
            master=medication_on_hand_labelframe,
        )

        self.medication_on_hand_entry = self.create_short_entry(
            master=medication_on_hand_row_1,
            padding=False,
            text_var=self.refill_str_vars['days_on_hand'],
            tooltip='Enter day supply on hand'
        )

        medication_on_hand_days_label = self.create_label(
            master=medication_on_hand_row_1,
            text='day(s)'
        )

        # Row 2
        medication_on_hand_row_2 = self.create_inner_frame(
            master=medication_on_hand_labelframe,
        )

        self.medication_on_hand_injection_btn = self.create_solid_tool_btn(
            master=medication_on_hand_row_2,
            text='Injection',
            variable=self.refill_str_vars['inj_cyc_btn'],
            value='Injection is due',
            command=lambda: self.click_injection_cycle_btn(
                'inj_cyc_btn', 'Injection', 'is due'
            ),
            padding=False,
            tooltip='Enter when the next injection is due'
        )

        self.medication_on_hand_cycle_btn = self.create_solid_tool_btn(
            master=medication_on_hand_row_2,
            text='Cycle',
            variable=self.refill_str_vars['inj_cyc_btn'],
            value='Next cycle starts',
            command=lambda: self.click_injection_cycle_btn(
                'inj_cyc_btn', 'Cycle', 'starts'
            ),
            tooltip='Enter when the next cycle starts'
        )

        self.medication_on_hand_due_start_label = self.create_label(
            master=medication_on_hand_row_2,
            text='',
            width=5
        )

        self.medication_on_hand_due_start_entry = self.create_short_entry(
            master=medication_on_hand_row_2,
            text_var=self.refill_str_vars['inj_cyc_start_date'],
            tooltip='Enter the next injection or cycle date'
        )
        self.medication_on_hand_due_start_entry.pack_forget()

        # Dispense date

        # Row 1
        dispense_date_row_1 = self.create_inner_frame(
            master=dispense_date_labelframe,
            grid=True
        )
        dispense_date_row_1.grid(row=0, column=0, sticky='w', pady=(10, 0))

        dispense_date_dcs_btn = self.create_solid_tool_btn(
            master=dispense_date_row_1,
            text='DCS',
            padding=False,
            variable=self.refill_str_vars['dispense_method_btn'],
            value='DCS',
            command=lambda: self.click_dispense_method_btn(
                'dispense_method_btn', 'DCS', 'Shipping out on'
            ),
            tooltip='DCS\nSame day delivery. Reserved strictly for Orange County.'
        )
        dispense_date_fedex_btn = self.create_solid_tool_btn(
            master=dispense_date_row_1,
            text='FedEx',
            variable=self.refill_str_vars['dispense_method_btn'],
            value='FedEx',
            command=lambda: self.click_dispense_method_btn(
                'dispense_method_btn', 'FedEx', 'Shipping out on', 'for 4/12 delivery'
            ),
            tooltip='FedEx\nNext day delivery. No fridge shipments on Thursdays.'
        )
        dispense_date_pickup_btn = self.create_solid_tool_btn(
            master=dispense_date_row_1,
            text='Pick Up',
            variable=self.refill_str_vars['dispense_method_btn'],
            value='Pick up',
            command=lambda: self.click_dispense_method_btn(
                'dispense_method_btn', 'Pick Up', 'Picking up on', 'Time:'
            ),
            tooltip='Pick Up'
        )
        dispense_date_walkover_btn = self.create_solid_tool_btn(
            master=dispense_date_row_1,
            text='Walk Over',
            variable=self.refill_str_vars['dispense_method_btn'],
            value='Walk over',
            command=lambda: self.click_dispense_method_btn(
                'dispense_method_btn', 'Walk Over', 'Walking over on', '  to'
            ),
            tooltip='Clinic delivery\n(i.e. PAV 1, PAV 3, Inpatient)'
        )

        # Row 2
        dispense_date_row_2 = self.create_inner_frame(
            master=dispense_date_labelframe,
            grid=True
        )
        dispense_date_row_2.grid(row=1, column=0, sticky='w', pady=(10, 0))

        self.dispense_date_method_label = self.create_label(
            master=dispense_date_row_2,
            text='Dispense Date:',
            width=15,
            grid=True
        )
        self.dispense_date_method_label.grid(row=0, column=0)

        self.dispense_date_calendar = tkb.DateEntry(
            master=dispense_date_row_2,
        )
        self.dispense_date_calendar.grid(row=0, column=1, padx=(3, 0))
        self.dispense_date_calendar.entry.config(
            textvariable=self.refill_str_vars['dispense_date'],
            width=10,
            state='disabled',
            validate='all',
            validatecommand=(date_func, '%P')
        )
        ToolTip(
            widget=self.dispense_date_calendar.entry,
            text='Select dispense date',
            delay=500
        )
        self.dispense_date_calendar.button.config(
            state='disabled',
            command=self.custom_calendar_entry_btn_method
        )
        ToolTip(
            widget=self.dispense_date_calendar.button,
            text='Select dispense date',
            delay=500
        )

        self.dispense_date_time_to_label = self.create_label(
            master=dispense_date_row_2,
            text='',
            grid=True
        )
        self.dispense_date_time_to_label.grid(
            row=0, column=2, sticky='w', padx=(3, 0)
        )

        self.dispense_date_time_location_entry = self.create_short_entry(
            master=dispense_date_row_2,
            text_var=self.refill_str_vars['time_location'],
            grid=True,
            tooltip='Pick Up: Enter pick up time\nWalk Over: Enter walk over location'
        )
        self.dispense_date_time_location_entry.grid(
            row=0, column=3, padx=(3, 0)
        )
        dispense_date_row_2.columnconfigure(2, minsize=148)
        self.dispense_date_time_location_entry.grid_forget()

        # Row 3
        dispense_date_row_3 = self.create_inner_frame(
            master=dispense_date_labelframe,
            grid=True
        )
        dispense_date_row_3.grid(row=2, column=0, sticky='w', pady=(10, 0))

        dispense_date_signature_required_label = self.create_label(
            master=dispense_date_row_3,
            text='Signature required?',
            padding=False
        )

        self.dispense_date_yes_btn = self.create_solid_tool_btn(
            master=dispense_date_row_3,
            text='Yes',
            variable=self.refill_str_vars['sig_required_btn'],
            value='sig required',
            command=lambda: self.click_sig_required_btn(
                'sig_required_btn', 'Yes'
            ),
            state='disabled',
            tooltip='Signature required\n(Required for Medicare Part B and Humana Part D)'
        )

        self.dispense_date_no_btn = self.create_solid_tool_btn(
            master=dispense_date_row_3,
            text='No',
            variable=self.refill_str_vars['sig_required_btn'],
            value='no sig',
            command=lambda: self.click_sig_required_btn(
                'sig_required_btn', 'No'
            ),
            state='disabled',
            tooltip='No signature required'
        )

        self.copy_wam_notes_btn = tkb.Button(
            master=dispense_date_labelframe,
            text='Copy WAM\n    Notes',
            command=self.copy_formatted_wam_notes,
            state='disabled'
        )
        self.copy_wam_notes_btn.grid(
            row=2, column=0, rowspan=2, padx=(278, 0), pady=(30, 0), ipady=1
        )
        ToolTip(
            widget=self.copy_wam_notes_btn,
            text='Copy WAM dispense notes to clipboard',
            delay=500
        )

        # Row 4
        dispense_date_row_4 = self.create_inner_frame(
            master=dispense_date_labelframe,
            grid=True
        )
        dispense_date_row_4.grid(row=3, column=0, sticky='w', pady=(10, 0))

        dispense_date_comments_label = self.create_label(
            master=dispense_date_row_4,
            text='Comments:',
            padding=False
        )

        self.dispense_date_comments_entry = self.create_short_entry(
            master=dispense_date_row_4,
            width=30,
            text_var=self.refill_str_vars['dispense_comments'],
            tooltip='Enter any dispense, pick up, or delivery comments',
            state='disabled'
        )

        # Medication Efficacy

        # Row 1
        medication_efficacy_row_1 = self.create_inner_frame(
            master=medication_efficacy_labelframe
        )

        medication_efficacy_is_working_label = self.create_label(
            master=medication_efficacy_row_1,
            text='Is medication working?',
            padding=False
        )

        medication_efficacy_a_lot_btn = self.create_solid_tool_btn(
            master=medication_efficacy_row_1,
            text='A lot',
            variable=self.refill_str_vars['medication_efficacy_btn'],
            value='Yes, it\'s working a lot.',
            command=lambda: self.click_medication_efficacy_btn(
                'medication_efficacy_btn', 'A lot'
            ),
            tooltip='Medication is working a lot'
        )

        medication_efficacy_a_little_btn = self.create_solid_tool_btn(
            master=medication_efficacy_row_1,
            text='A little',
            variable=self.refill_str_vars['medication_efficacy_btn'],
            value='Yes, it\'s working a little.',
            command=lambda: self.click_medication_efficacy_btn(
                'medication_efficacy_btn', 'A little'
            ),
            tooltip='Medication is working a little'
        )

        medication_efficacy_cant_tell_btn = self.create_solid_tool_btn(
            master=medication_efficacy_row_1,
            text='Can\'t tell',
            variable=self.refill_str_vars['medication_efficacy_btn'],
            value='No, I don\'t feel a difference.',
            command=lambda: self.click_medication_efficacy_btn(
                'medication_efficacy_btn', 'Can\'t tell'
            ),
            tooltip='Can\'t tell if medication is working'
        )

        # Spoke with

        # Row 1
        spoke_with_row_1 = self.create_inner_frame(
            master=spoke_with_labelframe
        )

        spoke_with_entry = self.create_short_entry(
            master=spoke_with_row_1,
            padding=False,
            width=35,
            text_var=self.refill_str_vars['spoke_with'],
            tooltip='Name of the person you spoke with'
        )

        # ========================= INTERVENTION ==============================#

        # Intervention display frame (tab)
        intervention_display_frame = tkb.Frame(
            master=self.notebook,
            padding=20,
        )
        intervention_display_frame.pack()
        self.notebook.add(intervention_display_frame, text='Intervention')

        # ===== INTERVENTION QUESTIONS ===== #

        # Labelframes
        intervention_questions_frame = tkb.Frame(intervention_display_frame)
        intervention_questions_frame.pack(side=LEFT)

        changes_labelframe = self.create_labelframe(
            intervention_questions_frame, 'Changes', 0
        )

        side_effects_labelframe = self.create_labelframe(
            intervention_questions_frame, 'Side Effects', 1
        )

        adherence_labelframe = self.create_labelframe(
            intervention_questions_frame, 'Adherence', 2
        )

        additional_notes_labelframe = self.create_labelframe(
            intervention_questions_frame, 'Additional Notes', 3, padding=False
        )

        # Changes

        # Row 1
        changes_row_1 = self.create_inner_frame(changes_labelframe)

        self.changes_dose_direction_btn = self.create_tool_btn(
            master=changes_row_1,
            text='Dose/Direction',
            variable=self.intervention_int_vars['dose_direction_btn'],
            command=lambda: self.click_intervention_tool_btns(
                btn_clicked='dose_direction_btn',
                list=self.changes,
                value='Change to dose/directions of current medication'
            ),
            padding=False,
            tooltip='Changes to dose or direction of current medication'
        )

        self.changes_medication_profile_btn = self.create_tool_btn(
            master=changes_row_1,
            text='Medication Profile',
            variable=self.intervention_int_vars['medication_profile_btn'],
            command=lambda: self.click_intervention_tool_btns(
                btn_clicked='medication_profile_btn',
                list=self.changes,
                value='Change to medication profile',
            ),
            tooltip='Change to medication profile'
        )

        self.changes_new_allergies_btn = self.create_tool_btn(
            master=changes_row_1,
            text='New Allergies',
            variable=self.intervention_int_vars['new_allergies_btn'],
            command=lambda: self.click_intervention_tool_btns(
                btn_clicked='new_allergies_btn',
                list=self.changes,
                value='Changes in allergies'
            ),
            tooltip='Changes in allergies'
        )

        # Row 2
        changes_row_2 = self.create_inner_frame(changes_labelframe)

        self.changes_medical_condition_btn = self.create_tool_btn(
            master=changes_row_2,
            text='Medical Conditions',
            variable=self.intervention_int_vars['medical_condition_btn'],
            command=lambda: self.click_intervention_tool_btns(
                btn_clicked='medical_condition_btn',
                list=self.changes,
                value='New Medication Condition(s)'
            ),
            padding=False,
            tooltip='Patient has new medical condition(s)'
        )

        self.changes_other_btn = self.create_tool_btn(
            master=changes_row_2,
            text='Other',
            variable=self.intervention_int_vars['other_changes_btn'],
            command=lambda: self.click_intervention_tool_btns(
                btn_clicked='other_changes_btn',
                list=self.changes,
                value='Other'
            ),
            tooltip='Patient has other changes.\nAdd details in the text box below.'
        )

        # Row 3
        changes_row_3 = self.create_inner_frame(changes_labelframe)

        self.changes_textbox = self.create_text_box(master=changes_row_3)

        # Side effects

        # Row 1
        side_effects_row_1 = self.create_inner_frame(side_effects_labelframe)

        self.side_effects_other_btn = self.create_tool_btn(
            master=side_effects_row_1,
            text='Other',
            variable=self.intervention_int_vars['other_side_effects_btn'],
            command=lambda: self.click_intervention_tool_btns(
                btn_clicked='other_side_effects_btn',
                list=self.symptoms,
                value='Other'
            ),
            padding=False,
            tooltip='Patient has other symptoms or side effects'
        )

        self.side_effects_injection_site_rxn_btn = self.create_tool_btn(
            master=side_effects_row_1,
            text='Injection site reaction',
            variable=self.intervention_int_vars['injection_site_rxn_btn'],
            command=lambda: self.click_intervention_tool_btns(
                btn_clicked='injection_site_rxn_btn',
                list=self.symptoms,
                value='Injection site reaction'
            ),
            tooltip='Patient has injection site reaction'
        )

        self.side_effects_hospitalized_er_btn = self.create_tool_btn(
            master=side_effects_row_1,
            text='Hospitalized/ER',
            variable=self.intervention_int_vars['hospitalized_er_btn'],
            command=lambda: self.click_intervention_tool_btns(
                btn_clicked='hospitalized_er_btn',
                list=self.symptoms,
                value='Hospitalized/ER visit'
            ),
            tooltip='Patient was hospitalized or had an ER visit'
        )

        # Row 2
        side_effects_row_2 = self.create_inner_frame(side_effects_labelframe)

        self.side_effects_textbox = self.create_text_box(side_effects_row_2)

        # Adherence

        # Row 1
        adherence_row_1 = self.create_inner_frame(adherence_labelframe)

        self.adherence_textbox = self.create_text_box(adherence_row_1)

        # Additional notes

        # Row 1
        additional_notes_row_1 = self.create_inner_frame(
            additional_notes_labelframe
        )

        self.additional_notes_textbox = self.create_text_box(
            additional_notes_row_1
        )

        # ========================== DROP SHIP ================================#

        # Drop ship display frame (tab)
        dropship_display_frame = tkb.Frame(master=self.notebook)
        dropship_display_frame.pack()
        self.notebook.add(dropship_display_frame, text='Drop Ship Look Up')

        if refill_mode == False:
            DropShipLookUp(master=dropship_display_frame, root=master)
        else:
            DropShipLookUp(master=dropship_display_frame, root=root)

    # Events and binds
        self.dispense_date_calendar.bind(
            '<FocusIn>', self._check_if_fedex_selected
        )

        self.dispense_date_calendar.entry.bind(
            '<Button>', self._open_calendar
        )

    # Recursive loop to check the state of copy buttons
        self.after(ms=50, func=self._check_copy_btns_state)

    # Widget Creation Methods

    def create_side_panel_btn(self, master, text):
        """Create side panel buttons."""
        btn = tkb.Button(
            master=master,
            text=text,
            compound=TOP,
            bootstyle=INFO
        )
        btn.pack(side=TOP, fill=BOTH, ipadx=10, ipady=10)
        return btn

    def create_labelframe(self, master, text, row, col=0, sticky='we', padding=True):
        """Create a label frame."""
        labelframe = tkb.Labelframe(
            master=master,
            text=text,
            style='TLabelframe.Label',
            padding=10,
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

    def create_label(self, master, text, anchor='e',  width=DEFAULT, padding=True, grid=False):
        """Create a label."""
        label = tkb.Label(
            master=master,
            text=text,
            width=width,
            anchor=anchor,
            font=('', 10, '')
        )
        if not grid:
            label.pack(side=LEFT, padx=(3, 0))
            if not padding:
                label.pack_configure(padx=0)

        return label

    def create_short_entry(self, master, width=15, padding=True, text_var=None, state='normal', grid=False, tooltip=''):
        """Create an entry field."""
        entry = tkb.Entry(
            master=master,
            width=width,
            textvariable=text_var,
            state=state
        )
        if not grid:
            entry.pack(side=LEFT, padx=(3, 0))
            if not padding:
                entry.pack_configure(padx=0)

        ToolTip(widget=entry, text=tooltip, delay=500)
        return entry

    def create_solid_tool_btn(
            self, master, text, variable, value, command, padding=True, state='normal', tooltip=''
    ):
        """Create a rectangular solid toolbutton (Radiobutton)."""
        solid_tool_btn = tkb.Radiobutton(
            master=master,
            bootstyle='toolbutton',
            text=text,
            variable=variable,
            value=value,
            command=command,
            state=state
        )
        solid_tool_btn.pack(side=LEFT, padx=(2, 0))
        if not padding:
            solid_tool_btn.pack_configure(padx=0)

        ToolTip(solid_tool_btn, text=tooltip, delay=500)
        return solid_tool_btn

    def create_tool_btn(
            self, master, text, variable, command, padding=True, state='disabled', tooltip=''
    ):
        """Create a rectangular toolbutton (Checkbutton)."""
        tool_btn = tkb.Checkbutton(
            master=master,
            bootstyle='toolbutton',
            text=text,
            variable=variable,
            command=command,
            state=state
        )
        tool_btn.pack(side=LEFT, padx=(2, 0))
        if not padding:
            tool_btn.pack_configure(padx=0)

        ToolTip(tool_btn, text=tooltip, delay=500)
        return tool_btn

    def create_text_box(self, master, state='disabled'):
        """Create a Tk text box."""
        textbox = tk.Text(
            master=master,
            wrap=WORD,
            height=3,
            width=60,
            state=state
        )
        textbox.pack(side=LEFT, fill=BOTH)
        return textbox

    # Various methods for button commands

    def _clear_intervention_text_boxes(self):
        """
        (Helper method)
        Clear all the contents of Intervention text boxes.
        """
        text_boxes = [
            self.changes_textbox, self.side_effects_textbox,
            self.adherence_textbox, self.additional_notes_textbox
        ]
        for text_box in text_boxes:
            text_box.config(state='normal')
            text_box.delete(1.0, END)
            text_box.config(state='disabled')

    def _disable_intervention_toolbuttons(self):
        """
        (Helper method)
        Disable all intervention toolbuttons.
        """
        intervention_widgets = [
            self.changes_dose_direction_btn, self.changes_medication_profile_btn,
            self.changes_new_allergies_btn, self.changes_medical_condition_btn,
            self.changes_other_btn, self.changes_textbox,
            self.side_effects_other_btn, self.side_effects_injection_site_rxn_btn,
            self.side_effects_hospitalized_er_btn, self.side_effects_textbox,
            self.adherence_textbox, self.additional_notes_textbox
        ]
        for widget in intervention_widgets:
            widget.config(state='disabled')

    def clear_intervention_tab(self):
        """Clear all entires in the intervention tab."""
        for int_var in self.intervention_int_vars:
            self.intervention_int_vars[int_var].set(0)

        self.changes.clear()
        self.symptoms.clear()
        self._clear_intervention_text_boxes()
        self._disable_intervention_toolbuttons()
        self.intervention_toggle_state.set(0)

    def clear_entries(self):
        """Clear all entries from Refill and Intervention forms."""
        self.medication_on_hand_due_start_label.config(text='')
        self.medication_on_hand_due_start_entry.pack_forget()
        self.dispense_date_method_label.config(text='Dispense Date:')
        self.dispense_date_time_to_label.config(text='')
        self.dispense_date_time_location_entry.grid_forget()
        self._enable_disable_dispense_widgets('disabled')
        for str_var in self.refill_str_vars:
            self.refill_str_vars[str_var].set('')

        for btn_group in self.solid_tool_btn_states.values():
            for btn_state in btn_group:
                btn_group[btn_state] = 0

        self.clear_intervention_tab()
        self.reassessment_toggle_state.set(0)

        win32clipboard.OpenClipboard(0)
        win32clipboard.EmptyClipboard()
        win32clipboard.CloseClipboard()
        self.notebook.select(self.refill_display_frame)
        self.medication_entry.focus()

    def _update_radio_btn_states(self, btn_group, btn_clicked):
        """
        (Helper method)
        Update the state of all radio buttons in a particular radio button group.
        """
        for btn in self.solid_tool_btn_states[btn_group]:
            if btn == btn_clicked:
                self.solid_tool_btn_states[btn_group][btn] = 1
            else:
                self.solid_tool_btn_states[btn_group][btn] = 0

    def _select_injection_cycle_btn(self, btn_group, btn_clicked, label):
        """
        (Helper method)
        Update label text and radio button states. Display entry field.
        """
        if self.medication_on_hand_entry.get() == '':
            self.medication_on_hand_entry.insert(0, '0')
        self.medication_on_hand_due_start_label.config(text=label)
        self._update_radio_btn_states(btn_group, btn_clicked)
        self.medication_on_hand_due_start_entry.pack(side=LEFT, padx=(3, 0))

    def _unselect_injection_cycle_btn(self, btn_group, btn_clicked):
        """
        (Helper method)
        Remove label text and entry. Set radio button state to off.
        """
        self.refill_str_vars[btn_group].set(None)
        self.medication_on_hand_due_start_label.config(text='')
        self.solid_tool_btn_states[btn_group][btn_clicked] = 0
        self.medication_on_hand_due_start_entry.pack_forget()

    def click_injection_cycle_btn(self, btn_group: str, btn_clicked: str, label: str):
        """Toggle label text and entry for the next injection/therapy cycle."""
        if self.solid_tool_btn_states[btn_group][btn_clicked] == 0:
            self._select_injection_cycle_btn(btn_group, btn_clicked, label)
        else:
            self._unselect_injection_cycle_btn(btn_group, btn_clicked)

    def _enable_disable_dispense_widgets(self, state: str):
        """
        Enable/disable dispense widgets once a dispense method button is selected/unselected.
        """
        widgets = [
            self.dispense_date_calendar.entry, self.dispense_date_calendar.button,
            self.dispense_date_yes_btn, self.dispense_date_no_btn,
            self.dispense_date_comments_entry
        ]
        for widget in widgets:
            widget.config(state=state)

    def _select_dispense_method_btn(self, btn_group, btn_clicked, label1, label2=None):
        """
        (Helper method)
        Update label text and radio button states. Display entry field.
        """
        self._update_radio_btn_states(btn_group, btn_clicked)
        self._enable_disable_dispense_widgets(state='normal')
        if btn_clicked == 'DCS':
            self.dispense_date_method_label.config(text=label1)
            self.dispense_date_time_to_label.config(text='')
            self.dispense_date_time_location_entry.grid_forget()
        elif btn_clicked == 'FedEx':
            self.dispense_date_method_label.config(text=label1)
            self._update_fedex_delivery_label()
            self.dispense_date_time_location_entry.grid_forget()
        elif btn_clicked == 'Pick Up' or btn_clicked == 'Walk Over':
            self.dispense_date_method_label.config(text=label1)
            self.dispense_date_time_to_label.config(text=label2)
            self.dispense_date_time_location_entry.delete(0, END)
            self.dispense_date_time_location_entry.grid(
                row=0, column=2, columnspan=2, padx=(35, 0)
            )
            self.refill_str_vars['sig_required_btn'].set('')
            self.dispense_date_yes_btn.config(state='disabled')
            self.dispense_date_no_btn.config(state='disabled')
        else:
            self.dispense_date_time_to_label.config(text='')

    def _unselect_dispense_method_btn(self, btn_group, btn_clicked):
        """
        (Helper method)
        Update label text and radio button states. Display entry field.
        """
        self.refill_str_vars[btn_group].set(None)
        self.refill_str_vars['sig_required_btn'].set(None)
        self.solid_tool_btn_states[btn_group][btn_clicked] = 0
        self.dispense_date_method_label.config(text='Dispense Date:')
        self.dispense_date_time_to_label.config(text='')
        self.dispense_date_calendar.entry.delete(0, END)
        self.dispense_date_time_location_entry.grid_forget()
        self._enable_disable_dispense_widgets(state='disabled')

    def click_dispense_method_btn(self, btn_group: str, btn_clicked: str, label1: str, label2: str = None):
        """Toggle label texts, date entry, and time/location entry for dispensing."""
        if self.solid_tool_btn_states[btn_group][btn_clicked] == 0:
            self._select_dispense_method_btn(
                btn_group, btn_clicked, label1, label2
            )
        else:
            self._unselect_dispense_method_btn(btn_group, btn_clicked)

    def get_fedex_delivery_date(self) -> str:
        """Calculate and return FedEx delivery date."""
        ship_date = self.dispense_date_calendar.entry.get().strip()
        if ship_date:
            try:
                ship_date_dt = dt.datetime.strptime(ship_date, '%m/%d/%Y')
                delivery_date = ship_date_dt + dt.timedelta(days=1)
                return f'{delivery_date.month}/{delivery_date.day}'
            except:
                return ''
        else:
            return ''

    def _update_fedex_delivery_label(self):
        delivery_date = self.get_fedex_delivery_date().strip()
        if delivery_date:
            self.dispense_date_time_to_label.config(
                text=f'for {delivery_date} delivery'
            )
        else:
            self.dispense_date_time_to_label.config(text='')

    def click_sig_required_btn(self, btn_group: str, btn_clicked: str):
        """Toggle the 'Yes' and 'No' buttons on or off if signature is required."""
        if self.solid_tool_btn_states[btn_group][btn_clicked] == 0:
            self._update_radio_btn_states(btn_group, btn_clicked)
        else:
            self.solid_tool_btn_states[btn_group][btn_clicked] = 0
            self.refill_str_vars[btn_group].set('')

    def click_medication_efficacy_btn(self, btn_group: str, btn_clicked: str):
        """Toggle `A lot`, `A little` and `Can't tell` buttons on or off."""
        if self.solid_tool_btn_states[btn_group][btn_clicked] == 0:
            self._update_radio_btn_states(btn_group, btn_clicked)
        else:
            self.solid_tool_btn_states[btn_group][btn_clicked] = 0
            self.refill_str_vars[btn_group].set('')

    def click_intervention_tool_btns(self, btn_clicked: str, list: list, value: str):
        """Append or remove values from changes or symptoms list."""
        if self.intervention_int_vars[btn_clicked].get() == 1:
            list.append(value)
        else:
            list.remove(value)

    def toggle_intervention(self):
        """
        Enable or disable the intervention tab when clicking on the Intervention toggle button.
        """
        intervention_widgets = [
            self.changes_dose_direction_btn, self.changes_medication_profile_btn,
            self.changes_new_allergies_btn, self.changes_medical_condition_btn,
            self.changes_other_btn, self.changes_textbox,
            self.side_effects_other_btn, self.side_effects_injection_site_rxn_btn,
            self.side_effects_hospitalized_er_btn, self.side_effects_textbox,
            self.adherence_textbox, self.additional_notes_textbox
        ]
        for widget in intervention_widgets:
            if self.intervention_toggle_state.get() == 1:
                widget.config(state='normal')
            else:
                widget.config(state='disabled')

    def custom_calendar_entry_btn_method(self):
        """Custom method to update Wrap Up date entry with the selected date."""
        if self.wrapup:
            self.dispense_date_calendar._on_date_ask()
            self.wrapup.dispense_date_entry.entry.delete(0, END)
            self.wrapup.dispense_date_entry.entry.insert(END, self.dispense_date_calendar.entry.get())
        else:
            self.dispense_date_calendar._on_date_ask()


    # Event bind callbacks

    def _check_if_fedex_selected(self, e):
        """Update FedEx delivery date label."""
        if self.solid_tool_btn_states['dispense_method_btn']['FedEx'] == 1:
            self._update_fedex_delivery_label()

    def _open_calendar(self, e):
        """Open DateEntry popup calendar."""
        self.dispense_date_calendar.button.invoke()

    # Validation methods

    def _validate_date(self, value_if_allowed):
        """Ensure DateEntry is not selected before present."""
        try:
            selected_datetime = dt.datetime.strptime(
                value_if_allowed, '%m/%d/%Y'
            )
            selected_date = selected_datetime.date()
            if selected_date >= dt.date.today():
                return True
        except:
            pass

        if value_if_allowed == '':
            return True

        return False

    def _check_wam_copy_btn_conditions(self) -> bool:
        """Return True if Copy WAM Notes button conditions are met."""
        dispense_method = self.refill_str_vars['dispense_method_btn'].get(
        ).strip()
        dispense_date = self.refill_str_vars['dispense_date'].get().strip()
        sig_required = self.refill_str_vars['sig_required_btn'].get().strip()
        time_location = self.refill_str_vars['time_location'].get().strip()
        if dispense_method in ('DCS', 'FedEx'):
            if dispense_date and sig_required:
                return True
            else:
                return False
        elif dispense_method in ('Pick up', 'Walk over'):
            if dispense_date and time_location:
                return True
            else:
                return False
        else:
            return False

    def _check_template_copy_btn_conditions(self) -> bool:
        """Return True if Copy Template button conditions are met."""
        if self.refill_str_vars['medication_name'].get().strip()\
                and self.refill_str_vars['days_on_hand'].get().strip()\
                and self.refill_str_vars['medication_efficacy_btn'].get()\
                and self.refill_str_vars['spoke_with'].get().strip():
            return True
        else:
            return False

    def _check_copy_btns_state(self):
        """Enable or disable the copy buttons if the conditions are met."""
        if self._check_wam_copy_btn_conditions():
            self.copy_wam_notes_btn.config(state='normal')
            dispense_date_satisfied = True
        else:
            self.copy_wam_notes_btn.config(state='disabled')
            dispense_date_satisfied = False

        if dispense_date_satisfied and self._check_template_copy_btn_conditions():
            self.copy_template_btn.config(state='normal')
        else:
            self.copy_template_btn.config(state='disabled')

        self.after(ms=50, func=self._check_copy_btns_state)

# Methods for copying notes to clipboard

    def copy_rtf_to_clipboard(self, formatted_text: str):
        """Copy formatted rich text to clipboard."""
        rtf = bytearray(
            fr'{{\rtf1\ansi\deff0 {{\fonttbl {{\f0 Arial;}}}}{{\colortbl;\red0\green0\blue0;\red255\green0\blue0;\red255\green255\blue0;}} {formatted_text}}}', 'utf8'
        )
        win32clipboard.OpenClipboard(0)
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(self.cf_rtf, rtf)
        win32clipboard.CloseClipboard()

    def copy_plaintext_to_clipboard(self, formatted_text: str):
        """Copy formatted plain text to clipboard."""
        win32clipboard.OpenClipboard(0)
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(formatted_text, win32clipboard.CF_TEXT)
        win32clipboard.CloseClipboard()

    def get_formatted_dispense_date(self) -> str:
        """Get formatted dispense date from datetime object."""
        dispense_date = self.refill_str_vars['dispense_date'].get().strip()
        try:
            disp_date_dt_obj = dt.datetime.strptime(dispense_date, '%m/%d/%Y')
        except:
            return ''

        return f'{disp_date_dt_obj.month}/{disp_date_dt_obj.day}'

    def format_wam_notes(self, format='plain') -> str:
        """Format WAM notes with plain or rich text."""
        dispense_method = self.refill_str_vars['dispense_method_btn'].get()
        signature = self.refill_str_vars['sig_required_btn'].get()
        time_location = self.refill_str_vars['time_location'].get().strip()
        dispense_comments = self.refill_str_vars['dispense_comments'].get().capitalize()
        if format == 'plain':
            wam_notes = f'{dispense_method} {self.get_formatted_dispense_date()}' 
            if dispense_method == 'DCS':
                wam_notes += f', {signature}'
                if dispense_comments:
                    wam_notes += f'\n{dispense_comments}'
                    
            elif dispense_method == 'FedEx':
                wam_notes += f' for {self.get_fedex_delivery_date()} delivery, {signature}'       
                if dispense_comments:
                    wam_notes += f'\n{dispense_comments}'

            elif dispense_method == 'Pick up':
                pickup_time = time_location
                if pickup_time[0].isdigit():
                    wam_notes += f' at'
                
                wam_notes += f' {pickup_time}'
                if dispense_comments:
                    wam_notes += f'\n{dispense_comments}'
            else:
                wam_notes += f' to {time_location.upper()}'
                if dispense_comments:
                    wam_notes += f'\n{dispense_comments}'
                    
        elif format == 'rich':
            wam_notes = fr'{{{dispense_method}}} {{{self.get_formatted_dispense_date()}}}' 
            if dispense_method == 'DCS':
                wam_notes += fr', {{{signature}}}'
                if dispense_comments:
                    wam_notes += fr'\line{{{dispense_comments}}}'
                
            elif dispense_method == 'FedEx':
                wam_notes += fr' for {{{self.get_fedex_delivery_date()}}} delivery, {{{signature}}}'     
                if dispense_comments:
                    wam_notes += fr'\line{{{dispense_comments}}}'

            elif dispense_method == 'Pick up':
                pickup_time = time_location
                if pickup_time[0].isdigit():
                    wam_notes += fr' at'
                    
                wam_notes += fr' {{{pickup_time}}}'
                if dispense_comments:
                    wam_notes += fr'\line{{{dispense_comments}}}'

            else:
                wam_notes += fr' to {{{time_location.upper()}}}'
                if dispense_comments:
                    wam_notes += fr'\line{{{dispense_comments}}}'
                
        return wam_notes
    
    def get_notes_from_text_box(self, text_widget: tk.Text) -> str:
        """Retrieve contents of Changes Text widget."""
        contents =  text_widget.get(1.0, 'end').strip()
        if contents == 'Notes':
            contents = ''
        elif contents:
            contents = contents[0].capitalize() + contents[1:]
            if contents[-1] != '.':
                contents += '.'
      
        return contents
    
    def format_template_notes(self) -> str:
        """Format Template notes with rich text."""
        medication = self.medication_entry.get().strip().capitalize()
        dispense_method = self.refill_str_vars['dispense_method_btn'].get().strip()


        if dispense_method == 'Pick up':
            hipaa_verification = 'Name, DOB, Drug Prescribed'
        else:
            hipaa_verification = 'Name, DOB, Address, Drug Prescribed'
        
        ready_to_fill = 'Yes, refill initiated in WAM.'
        days_supply = self.refill_str_vars['days_on_hand'].get().strip()
        injection_cycle = self.refill_str_vars['inj_cyc_btn'].get()
        injection_cycle_date = self.refill_str_vars['inj_cyc_start_date'].get().strip()
        if injection_cycle_date:
            next_injection_cycle_due = f' {injection_cycle} {injection_cycle_date}'
        else:
            next_injection_cycle_due = ''

        delivery_pickup = dispense_method
        if delivery_pickup == 'Walk over':
            delivery_pickup = 'Clinic delivery'

        dispense_date = self.format_wam_notes(format='rich')
        allergies_reviewed = 'Yes'
        medication_review = 'Yes,'
        spoke_with = self.refill_str_vars['spoke_with'].get().strip()
        if spoke_with.lower() in ('patient', 'the patient', 'pt', 'pateint', 'thepatient', 'patients'):
            medication_review_confirmation = 'patient confirmation.'
        else:
            medication_review_confirmation = fr'other.\
Confirmed with {spoke_with}'
  
        medical_conditions_review = 'Yes'
        continuation_therapy = 'Yes'
        med_working = self.refill_str_vars['medication_efficacy_btn'].get()
        goal = 'Yes' 

        first = self.settings.current_settings['user']['first_name']
        last = self.settings.current_settings['user']['last_name']
        user = f'{first} {last}'

        # Intervention variables
        changes = 'None' 
        new_allergies = 'No' 
        new_medications = 'No'
        medical_condition_changes = 'None'
        review_symptoms = 'N/A'
        intervention_necessary = 'No'
        adherence = 'ADHERENT'
        embedded_adherence_notes = ''
        speak_to_rph = 'No'

        if self.intervention_toggle_state.get():
            speak_to_rph = 'Yes, intervention necessary.'
            if self.changes:
                number_of_different_changes = len(self.changes)
                # Move 'Other' to the end of list
                if 'Other' in self.changes and number_of_different_changes > 1:
                    self.changes.append(self.changes.pop(self.changes.index('Other')))
                changes = ''
                if number_of_different_changes == 1:
                    changes = self.changes[0]
                elif number_of_different_changes == 2:
                    changes = f'{self.changes[0]} and {self.changes[1]}'
                else:
                    for _change in self.changes:
                        if _change == self.changes[-1]:
                            changes += ', and '
                        else:
                            changes += ', '
                        changes += _change
                    changes = changes[2:]
                
                changes_notes = self.get_notes_from_text_box(self.changes_textbox)
                if changes_notes:
                    changes += f'\line\line\t {changes_notes}'

            if self.intervention_int_vars['new_allergies_btn'].get():
                new_allergies = 'Yes - updated new allergies'
            if self.intervention_int_vars['medication_profile_btn'].get():
                new_medications = 'Yes'
            if self.intervention_int_vars['medical_condition_btn'].get():
                medical_condition_changes = 'Yes - Noted new additions of medical conditions and appropriately documented.'
            else:
                medical_condition_changes = 'No'
            if self.symptoms:
                number_of_different_symptoms = len(self.symptoms)
                # Move 'Other' to the end of the list
                if 'Other' in self.symptoms and number_of_different_symptoms > 1:
                    self.symptoms.append(self.symptoms.pop(self.symptoms.index('Other')))
                review_symptoms = fr''
                if number_of_different_symptoms == 1:
                    review_symptoms = self.symptoms[0]
                elif number_of_different_symptoms == 2:
                    review_symptoms = fr'{{{self.symptoms[0]}}} and {{{self.symptoms[1]}}}'
                else:
                    for _symptom in self.symptoms:
                        if _symptom == self.symptoms[-1]:
                            review_symptoms += ', and '
                        else:
                            review_symptoms += ', '
                        review_symptoms += _symptom
                    review_symptoms = review_symptoms[2:]
                
                symptom_notes = self.get_notes_from_text_box(self.side_effects_textbox)
                if symptom_notes:
                    review_symptoms += fr'\line\tab {symptom_notes}'
                review_symptoms += fr'\line\line\tab If side-effect reported, documented by tech. If documented by tech, triage to RPh? Yes.\line'
                intervention_necessary = 'Yes. Routed to RPH.'

            adherence_notes = self.get_notes_from_text_box(self.adherence_textbox)
            if adherence_notes:
                adherence = 'NOT ADHERENT'
                embedded_adherence_notes = fr'\line\line\tab {adherence_notes}'

        # Reassessment conditions
        if not self.reassessment_toggle_state.get():
            template_title ='Refill Reminder'
            ready_to_fill_question = fr'\line Is patient ready to fill? {{{ready_to_fill}}}\line'
            dur_check = ''
            continuation_therapy_question = fr'\line \b\fs26 Is continuation of therapy appropriate: \b0\fs24 {{{continuation_therapy}}}\line'
            therapeutic_benefit_question = ''
            disease_assessment = ''
        else:
            template_title ='Specialty Pharmacy - Clinical Reassessment'
            ready_to_fill_question = ''
            dur_check = r'\line Was a drug utilization review (DUR) conducted?  \{YES/NO:12979\}\line\tab If yes, Medications can been screened for drug-drug interactions through \{micromedex, lexicomp, other:28109\} and drug-drug interactions were \{found, not found:28110\}\line'
            continuation_therapy_question = ''
            therapeutic_benefit_question = fr'\b\fs26\line Is the patient receiving therapeutic benefit from the medication:\b0\fs24  Yes\line'
            disease_assessment = fr'\b\fs26\line Complete disease assessment?\b0\fs24  No - patient does not have time\line'

        template =fr'\b\fs26{template_title}\b0\fs24\
\
Medication: {{{medication}}}\
\
Methods of HIPAA Verification: {{{hipaa_verification}}}\
\
Changes Since Last Visit: {{{changes}}}\
{{{ready_to_fill_question}}}\
Patient has {{{days_supply}}} days of medication on hand.{{{next_injection_cycle_due}}}\
Please select the following: {{{delivery_pickup}}}\
Ready to dispense date: {{{dispense_date}}}\
\
\b\fs26 Allergies Review \b0\fs24\
Were allergies to medications reviewed: {{{allergies_reviewed}}}\
Were there any new allergies: {{{new_allergies}}}\
\
\b\fs26 Medication Review \b0\fs24\
Medication review was performed: {{{medication_review}}} through {{{medication_review_confirmation}}}\
\
Is patient taking any new medications, OTCs, or herbal supplements? {{{new_medications}}}\
{{{dur_check}}}\
\b\fs26 Medical Conditions Review \b0\fs24\
Medical conditions review was performed: {{{medical_conditions_review}}}\
Were there changes to the medical condition? {{{medical_condition_changes}}}\
{{{continuation_therapy_question}}}\
\b\fs26 Do you feel like this medication is working for you:\b0\fs24  {{{med_working}}}\
{{{therapeutic_benefit_question}}}\
Has the patient reported experiencing any of the following? {{{review_symptoms}}}\
Is intervention necessary (if yes for any above): {{{intervention_necessary}}}\
\
Patient is {{{adherence}}} to therapy.{{{embedded_adherence_notes}}}\
\
***\
\
GOAL: Is patient meeting goal? {{{goal}}}\
{{{disease_assessment}}}\
Does patient need to speak to a pharmacist? {{{speak_to_rph}}}\
\
{{{user}}}\
Specialty Pharmacy'

        if self.intervention_toggle_state.get():
            additional_notes = self.get_notes_from_text_box(self.additional_notes_textbox)
            if additional_notes:
                template = fr'{{{additional_notes}}}\line\line{{{template}}}'

        return template

    def copy_formatted_wam_notes(self):
        """Copy formatted WAM notes to clipboard."""
        wam_notes = self.format_wam_notes(format='plain')
        self.copy_plaintext_to_clipboard(wam_notes)

    def copy_formatted_template_notes(self):
        """Copy formatted Template notes to clipboard."""
        template = self.format_template_notes()
        self.copy_rtf_to_clipboard(template)


if __name__ == '__main__':
    app = tkb.Window(
        'Refill Coordination', 'cosmo', resizable=(False, False)
    )
    Refill(app, app, None, None)
    app.place_window_center()
    app.mainloop()
