""" This module contains a class that represents Refill Coordination form."""

import tkinter as tk
import datetime as dt
import os, sys, subprocess, json
from PIL import Image, ImageTk
from win32 import win32clipboard
from tkinter import WORD
from tkcalendar import DateEntry


class RefillTemplate:
    """This class represents a GUI template that handles refill questions and formatting."""

    def __init__(self):
        """Initialize variables, template GUI and refill questions."""

        # Initialize settings
        self.background_color = 'white'
            # Select buttons
        self.btn_font = ('Comic Sans MS', 11, 'normal')
        self.btn_text_color = 'white'
        self.btn_active_fg_color = 'white'
        self.btn_bg_color = 'RoyalBlue1'
        self.btn_active_bg_color = 'RoyalBlue1'
        self.select_btn_bg_color = 'RoyalBlue4'
        self.btn_borderwidth = 0
        self.btn_relief = 'sunken' # sunken, raised, groove, ridge
        self.btn_space_btwn = 5
        self.btn_disabled_fg_color = 'snow3'
        self.btn_disabled_bg_color = 'ghost white'
            # Label frames
        self.labelFrame_font = ('Comic Sans MS', 11, 'bold')
        self.labelFrame_space_btwn = 7
        self.label_font = ('Comic Sans MS', 11, 'normal')
        self.disabled_text_color = 'snow3'
        self.text_color = 'black'
            # Entry
        self.entry_font = ('Comic Sans MS', 11, 'normal')
        self.entry_bg_color = 'gray92'
        self.entry_relief = 'flat'
            # Canvas
        self.canvas_padx = 10
        self.canvas_pady = 10
            # Other buttons
        self.copy_btn_bg_color = 'ghost white'
        self.copy_btn_fg_color = 'medium sea green'
        self.copy_btn_active_bg_color = 'ghost white' # #ebfff3
        self.copy_btn_active_fg_color = 'medium sea green'
        self.copy_btn_disabled_fg_color = 'snow3'
            # Intervention placeholder text
        self.placeholder_text_color = 'lightgray'
        self.placeholder_text_font = ('Comic Sans MS', 18, 'normal')


    
        # Initialize Refill coordination GUI window
        self.top = tk.Toplevel()
        self.top.withdraw()
        self.top.title('Refill Coordination')
        self.top.config(bg=self.background_color, padx=20, pady=20)
        self.top.resizable(False, False)
        self.icon = tk.PhotoImage(file='./assets/img/rx_icon.png')
        self.top.iconphoto(True, self.icon)

        # Initialize Intervention GUI window
        self.intervention_window = tk.Toplevel(self.top)
        self.intervention_window.withdraw()
        self.intervention_window.title('Intervention')
        self.intervention_window.config(bg=self.background_color, padx=20, pady=20)
        self.intervention_window.resizable(False, False)
        
        # Initialize win32clipboard
        self.cf_rtf = win32clipboard.RegisterClipboardFormat('Rich Text Format')

        # Initialize variables
        self.user = self.get_existing_user()
        self.changes = []
        self.injection_cycle = ''
        self.dispense_method = ''
        self.signature_required = ''
        self.fedex_delivery_date = ''
        self.allergies_review = 'Yes'
        self.new_allergies = 'No'
        self.medication_review = 'Yes'
        self.spoke_with = ''
        self.new_medication = 'No'
        self.medical_condition_review = 'Yes'
        self.medical_conditions_changes = 'None'
        self.therapy_continuation = 'Yes'
        self.medication_working = ''
        self.symptoms_reported = []
        self.symptoms_intervention = 'No'
        self.goal_met = 'Yes'
        self.speak_rph = 'No'

        self.intervention = False

        # === Container for top buttons and label === #
        self.container_top_buttons_labels = tk.Canvas(
            self.top, bg=self.background_color, highlightthickness=0
            )
        self.container_top_buttons_labels.grid(column=0, row=0)

        # Intervention button
        self.intervention_btn = tk.Button(
            self.container_top_buttons_labels, text='Intervention',command=self.toggle_intervention_window,
            bg=self.copy_btn_bg_color, relief='raised', fg='black',
            font=('Comic Sans MS', 8, 'normal'), activebackground=self.copy_btn_bg_color,
            activeforeground='black'
            )
        self.intervention_btn.grid(column=0, row=0)
        # Refill coordination label
        self.refill_coordination_label = tk.Label(
            self.container_top_buttons_labels, text='Refill Coordination',
            bg=self.background_color, font=('Comic Sans MS', 14, 'normal'),
            )
        self.refill_coordination_label.grid(column=1, row=0, padx=(40, 90))

        # Top buttons inner container
        self.top_buttons_inner_container = tk.Frame(
            self.container_top_buttons_labels, bg=self.background_color
            )
        self.top_buttons_inner_container.grid(
            column=2, row=0, pady=(self.labelFrame_space_btwn, 0), sticky='we'
            )
        # Edit user button
        img_path = './assets/img/edit-user.png'
        img = Image.open(img_path)
        self.edit_user_img = ImageTk.PhotoImage(img)
        self.edit_user_btn = tk.Button(
            self.top_buttons_inner_container, image=self.edit_user_img, command=self.user_setup_window,
            bg=self.copy_btn_bg_color
            )
        self.edit_user_btn.grid(column=0, row=0)

        # === Container for Medication label frame and Clear button === #
        self.container_med_clear = tk.Canvas(
            self.top, bg=self.background_color, highlightthickness=0
            )
        self.container_med_clear.grid(column=0, row=1, sticky='w', pady=(self.labelFrame_space_btwn, 0))

        # === Medication label frame === #
        self.medication_labelFrame = tk.LabelFrame(
            self.container_med_clear, text='Medication', bg=self.background_color, font=self.labelFrame_font
            )
        self.medication_labelFrame.grid(column=0, row=0, sticky='w')
        #   Medication canvas
        self.medication_canvas = tk.Canvas(
            self.medication_labelFrame, bg=self.background_color, highlightthickness=0
            )
        self.medication_canvas.grid(column=0, row=0, sticky='w', padx=self.canvas_padx, pady=self.canvas_pady)
        # Medication entry
        self.medication_entry = tk.Entry(
            self.medication_canvas, font=self.entry_font, bg=self.entry_bg_color,
            relief=self.entry_relief, width=30
            )
        self.medication_entry.grid(column=1, row=0, sticky='w')
        
        # Clear button
        self.clear_btn = tk.Button(
            self.container_med_clear, text='Clear', command=self.clear, bg=self.copy_btn_bg_color, relief='raised',
            fg='black', font=self.btn_font, activebackground=self.copy_btn_bg_color,
            activeforeground='black', width=9
            )
        self.clear_btn.grid(column=1, row=0, padx=(20,0))

        # === Medication on hand label frame === #
        self.medication_on_hand_labelFrame = tk.LabelFrame(
            self.top, text='Medication On Hand', bg=self.background_color, font=self.labelFrame_font
            )
        self.medication_on_hand_labelFrame.grid(column=0, row=2, sticky='we', pady=(self.labelFrame_space_btwn, 0))
        #   Day supply canvas
        self.day_supply_canvas = tk.Canvas(
            self.medication_on_hand_labelFrame, bg=self.background_color, highlightthickness=0
            )
        self.day_supply_canvas.grid(column=0, row=0, sticky='w', padx=self.canvas_padx, pady=self.canvas_pady)
        # Day supply entry
        self.day_supply_entry = tk.Entry(self.day_supply_canvas, font=self.entry_font, bg=self.entry_bg_color, relief=self.entry_relief)
        self.day_supply_entry.grid(column=0, row=0)
        # Day supply label
        self.day_supply_label = tk.Label(
            self.day_supply_canvas, text='day(s)', bg=self.background_color, font=self.label_font
            )
        self.day_supply_label.grid(column=1, row=0)
        #   Injection/cycle canvas
        self.injection_cycle_canvas = tk.Canvas(
            self.medication_on_hand_labelFrame, bg=self.background_color, highlightthickness=0
            )
        self.injection_cycle_canvas.grid(column=0, row=1, sticky='w', padx=self.canvas_padx, pady=self.canvas_pady)
        self.injection_btn = tk.Button(
            self.injection_cycle_canvas, text='Injection', command=self.select_injection,
            bg=self.btn_bg_color, borderwidth=self.btn_borderwidth,
            relief=self.btn_relief, fg=self.btn_text_color, font=self.btn_font,
            activebackground=self.btn_active_bg_color, activeforeground=self.btn_active_fg_color
            )
        self.injection_btn.grid(column=0, row=0)
        self.cycle_btn = tk.Button(
            self.injection_cycle_canvas, text='Cycle', command=self.select_cycle,
            bg=self.btn_bg_color, borderwidth=self.btn_borderwidth,
            relief=self.btn_relief, fg=self.btn_text_color, font=self.btn_font,
            activebackground=self.btn_active_bg_color, activeforeground=self.btn_active_fg_color
            )
        self.cycle_btn.grid(column=1, row=0, padx=(self.btn_space_btwn, 0))
        # Due/start label
        self.due_start_label = tk.Label(
            self.injection_cycle_canvas, text='', bg=self.background_color,
            font=self.label_font, width=7
            )
        self.due_start_label.grid(column=2, row=0)
        # Due/start entry
        self.due_start_entry = tk.Entry(
            self.injection_cycle_canvas, font=self.entry_font, bg=self.entry_bg_color,
            relief=self.entry_relief, width=19, disabledbackground=self.background_color,
            state='disabled'
            )
        self.due_start_entry.grid(column=3, row=0)

        # === Dispense date label frame === #
        self.dispense_date_labelFrame = tk.LabelFrame(
            self.top, text='Dispense Date', bg=self.background_color, font=self.labelFrame_font
            )
        self.dispense_date_labelFrame.grid(column=0, row=3, sticky='w', pady=(self.labelFrame_space_btwn, 0))
        #   Dispense btn canvas
        self.dispense_btn_canvas = tk.Canvas(
            self.dispense_date_labelFrame, bg=self.background_color, highlightthickness=0
            )
        self.dispense_btn_canvas.grid(column=0, row=0, sticky='w', padx=self.canvas_padx, pady=self.canvas_pady)
        # DCS button
        self.dispense_dcs_btn = tk.Button(
            self.dispense_btn_canvas, text='DCS', command=self.select_dcs,
            bg=self.btn_bg_color, borderwidth=self.btn_borderwidth,
            relief=self.btn_relief, fg=self.btn_text_color, font=self.btn_font,
            activebackground=self.btn_active_bg_color, activeforeground=self.btn_active_fg_color
            )
        self.dispense_dcs_btn.grid(column=0, row=0)
        # FedEx button
        self.dispense_fedex_btn = tk.Button(
            self.dispense_btn_canvas, text='FedEx', command=self.select_fedex,
            bg=self.btn_bg_color, borderwidth=self.btn_borderwidth,
            relief=self.btn_relief, fg=self.btn_text_color, font=self.btn_font,
            activebackground=self.btn_active_bg_color, activeforeground=self.btn_active_fg_color
            )
        self.dispense_fedex_btn.grid(column=1, row=0, padx=(self.btn_space_btwn, 0))
        # Pick up button
        self.dispense_pickup_btn = tk.Button(
            self.dispense_btn_canvas, text='Pick Up', command=self.select_pickup,
            bg=self.btn_bg_color, borderwidth=self.btn_borderwidth,
            relief=self.btn_relief, fg=self.btn_text_color, font=self.btn_font,
            activebackground=self.btn_active_bg_color, activeforeground=self.btn_active_fg_color
            )
        self.dispense_pickup_btn.grid(column=2, row=0, padx=(self.btn_space_btwn, 0))
        # Walk over button
        self.dispense_walkover_btn = tk.Button(
            self.dispense_btn_canvas, text='Walk Over', command=self.select_walkover,
            bg=self.btn_bg_color, borderwidth=self.btn_borderwidth,
            relief=self.btn_relief, fg=self.btn_text_color, font=self.btn_font,
            activebackground=self.btn_active_bg_color, activeforeground=self.btn_active_fg_color
            )
        self.dispense_walkover_btn.grid(column=3, row=0, padx=(self.btn_space_btwn, 0))
        # Walkover location entry
        self.dispense_walkover_entry = tk.Entry(
            self.dispense_btn_canvas, font=self.entry_font, bg=self.entry_bg_color,
            relief=self.entry_relief, width=15, disabledbackground=self.background_color,
            state='disabled'
            )
        self.dispense_walkover_entry.grid(column=4, row=0, padx=(self.btn_space_btwn, 0))
        #   Dispense date canvas
        self.dispense_date_canvas = tk.Canvas(
            self.dispense_date_labelFrame, bg=self.background_color, highlightthickness=0
            )
        self.dispense_date_canvas.grid(column=0, row=1, sticky='w', padx=self.canvas_padx, pady=self.canvas_pady)
        # Dispense date label
        self.dispense_date_label = tk.Label(
            self.dispense_date_canvas, text='Dispense Date:',
            bg=self.background_color, font=self.label_font, width=13, fg=self.disabled_text_color
            )
        self.dispense_date_label.grid(column=0, row=0)
        # Dispense date entry
        self.dispense_date_entry = DateEntry(
            self.dispense_date_canvas, selectmode='day', state='disabled',
            font=self.entry_font, width=9, background=self.btn_bg_color,
            foreground='white', showweeknumbers=False, firstweekday='sunday',
            bordercolor='white', headersbackground='white', selectbackground=self.select_btn_bg_color,
            weekendbackground='gray95', weekendforeground='gray73',
            othermonthbackground='white', borderwidth=0, othermonthforeground='gray73',
            disableddaybackground='white', disableddayforeground='gray88',
            mindate=dt.date.today(), normalforeground='black'
            )
        self.dispense_date_entry.grid(column=1, row=0)
        # FedEx delivery / Pickup time label
        self.fedex_delivery_pick_time_label = tk.Label(
            self.dispense_date_canvas, font=self.label_font, bg=self.background_color,
            text=''
            )
        self.fedex_delivery_pick_time_label.grid(column=2, row=0)
        # Pick up time entry
        self.dispense_pickup_time_entry = tk.Entry(
            self.dispense_date_canvas, font=self.entry_font, bg=self.entry_bg_color,
            relief=self.entry_relief, width=0, disabledbackground=self.background_color,
            state='disabled'
            )
        self.dispense_pickup_time_entry.grid(column=3, row=0)

        # Copy WAM notes button (@ canvas widget level, master is top level window)
        self.copy_wam_notes_btn = tk.Button(
            self.dispense_date_labelFrame, text='Copy WAM Notes', command=self.copy_formatted_wam_notes,
            bg=self.copy_btn_bg_color, relief='raised', fg=self.copy_btn_fg_color,
            font=self.btn_font, activebackground=self.copy_btn_active_bg_color,
            activeforeground=self.copy_btn_active_fg_color, width=11,
            wraplength=80, disabledforeground=self.copy_btn_disabled_fg_color
            )
        self.copy_wam_notes_btn.grid(column=0, row=2, rowspan=3, padx=(275,0), pady=(20,0))

        #   Signature canvas
        self.dispense_signature_canvas = tk.Canvas(
            self.dispense_date_labelFrame, bg=self.background_color, highlightthickness=0
            )
        self.dispense_signature_canvas.grid(column=0, row=3, sticky='w', padx=self.canvas_padx, pady=self.canvas_pady)
        # Signature label
        self.dispense_signature_label = tk.Label(
            self.dispense_signature_canvas, text='Signature required?',
            bg=self.background_color, font=self.label_font, fg=self.disabled_text_color
            )
        self.dispense_signature_label.grid(column=0, row=0)
        # Yes button
        self.dispense_signature_yes_btn = tk.Button(
            self.dispense_signature_canvas, text='Yes', command=self.select_yes_sig,
            bg=self.btn_disabled_bg_color, borderwidth=self.btn_borderwidth,
            relief=self.btn_relief, fg=self.btn_text_color, font=self.btn_font,
            activebackground=self.btn_active_bg_color, activeforeground=self.btn_active_fg_color,
            disabledforeground=self.copy_btn_disabled_fg_color, state='disabled'
            )
        self.dispense_signature_yes_btn.grid(column=1, row=0)
        # No button
        self.dispense_signature_no_btn = tk.Button(
            self.dispense_signature_canvas, text='No', command=self.select_no_sig,
            bg=self.btn_disabled_bg_color, borderwidth=self.btn_borderwidth,
            relief=self.btn_relief, fg=self.btn_text_color, font=self.btn_font,
            activebackground=self.btn_active_bg_color, activeforeground=self.btn_active_fg_color,
            disabledforeground=self.copy_btn_disabled_fg_color, state='disabled'
            )
        self.dispense_signature_no_btn.grid(column=2, row=0, padx=(self.btn_space_btwn, 0))

        #   Comments canvas
        self.dispense_comments_canvas = tk.Canvas(
            self.dispense_date_labelFrame, bg=self.background_color, highlightthickness=0
            )
        self.dispense_comments_canvas.grid(column=0, row=4, sticky='w', padx=self.canvas_padx, pady=self.canvas_pady)
        # Comments label
        self.dispense_comments_label = tk.Label(
            self.dispense_comments_canvas, text='Comments:', bg=self.background_color, font=self.label_font
            )
        self.dispense_comments_label.grid(column=0, row=0)
        # Comments entry
        self.dispense_comments_entry = tk.Entry(self.dispense_comments_canvas, font=self.entry_font, bg=self.entry_bg_color, relief=self.entry_relief)
        self.dispense_comments_entry.grid(column=1, row=0)

        # === Medication efficacy label frame === #
        self.medication_efficacy_labelFrame = tk.LabelFrame(
            self.top, text='Medication Efficacy', bg=self.background_color, font=self.labelFrame_font
            )
        self.medication_efficacy_labelFrame.grid(column=0, row=4, sticky='w', pady=(self.labelFrame_space_btwn, 0))
        #   Medication efficacy canvas
        self.medication_efficacy_canvas = tk.Canvas(
            self.medication_efficacy_labelFrame, bg=self.background_color, highlightthickness=0
            )
        self.medication_efficacy_canvas.grid(column=0, row=0, sticky='w', padx=self.canvas_padx, pady=self.canvas_pady)
        # Medication efficacy label
        self.medication_efficacy_label = tk.Label(
            self.medication_efficacy_canvas, text='Is medication working?', bg=self.background_color, font=self.label_font
            )
        self.medication_efficacy_label.grid(column=0, row=0)
        # A little button
        self.medication_efficacy_alittle_btn = tk.Button(
            self.medication_efficacy_canvas, text='A little', command=self.select_a_little,
            bg=self.btn_bg_color, borderwidth=self.btn_borderwidth,
            relief=self.btn_relief, fg=self.btn_text_color, font=self.btn_font,
            activebackground=self.btn_active_bg_color, activeforeground=self.btn_active_fg_color
            )
        self.medication_efficacy_alittle_btn.grid(column=2, row=0, padx=(self.btn_space_btwn, 0))
        # A lot button
        self.medication_efficacy_alot_btn = tk.Button(
            self.medication_efficacy_canvas, text='A lot', command=self.select_a_lot,
            bg=self.btn_bg_color, borderwidth=self.btn_borderwidth,
            relief=self.btn_relief, fg=self.btn_text_color, font=self.btn_font,
            activebackground=self.btn_active_bg_color, activeforeground=self.btn_active_fg_color
            )
        self.medication_efficacy_alot_btn.grid(column=1, row=0)
        # Can't tell button
        self.medication_efficacy_cantTell_btn = tk.Button(
            self.medication_efficacy_canvas, text='Can\'t tell', command=self.select_cant_tell,
            bg=self.btn_bg_color, borderwidth=self.btn_borderwidth,
            relief=self.btn_relief, fg=self.btn_text_color, font=self.btn_font,
            activebackground=self.btn_active_bg_color, activeforeground=self.btn_active_fg_color
            )
        self.medication_efficacy_cantTell_btn.grid(column=3, row=0, padx=(self.btn_space_btwn, 0))

        # === Spoke with label frame === #
        self.spoke_with_labelFrame = tk.LabelFrame(
            self.top, text='Spoke with', bg=self.background_color, font=self.labelFrame_font
            )
        self.spoke_with_labelFrame.grid(column=0, row=5, sticky='w', pady=(self.labelFrame_space_btwn, 0))
        #   Spoke with canvas
        self.spoke_with_canvas = tk.Canvas(
            self.spoke_with_labelFrame, bg=self.background_color, highlightthickness=0
            )
        self.spoke_with_canvas.grid(column=0, row=0, sticky='w', padx=self.canvas_padx, pady=self.canvas_pady)
        # Spoke with entry
        self.spoke_with_entry = tk.Entry(
            self.spoke_with_canvas, font=self.entry_font, bg=self.entry_bg_color,
            relief=self.entry_relief, width=25
            )
        self.spoke_with_entry.grid(column=0, row=0)

        # Copy template button
        self.copy_template_btn = tk.Button(
            self.top, text='Copy Template', command=self.copy_formatted_template_notes, bg=self.copy_btn_bg_color,
            relief='raised', fg=self.copy_btn_fg_color, font=self.btn_font,
            activebackground=self.copy_btn_active_bg_color,
            activeforeground=self.copy_btn_active_fg_color, width=14,
            disabledforeground=self.copy_btn_disabled_fg_color
            )
        self.copy_template_btn.grid(column=0, row=5, padx=(260,0), pady=(15,0))

        # ~ ~ ~ bind ~ ~ ~ #
        self.dispense_walkover_entry.bind('<FocusIn>', self.remove_temp_text)
        self.top.bind('<Delete>', self.clear)
        self.top.bind('<Control-u>', self.user_setup_window)
        self.top.bind('<Configure>', self.sync_windows)
        
        # ~ ~ ~ after ~ ~ ~ #
        self.top.after(ms=50, func=self.run_validations)


        # ======================== Intervention ======================== #

        # === Changes label frame === #
        self.changes_labelFrame = tk.LabelFrame(
            self.intervention_window, text='Changes', bg=self.background_color,
            font=self.labelFrame_font, highlightthickness=0
            )
        self.changes_labelFrame.grid(column=0, row=1)

        # Changes button container
        self.changes_button_container = tk.Frame(
            self.changes_labelFrame, highlightthickness=0, bg=self.background_color
            )
        self.changes_button_container.grid(column=0, row=0, sticky='w', padx=self.canvas_padx, pady=self.canvas_pady)
        # Dose/Direction button
        self.changes_dose_direction_btn = tk.Button(
            self.changes_button_container, text='Dose/Direction', command=self._select_dose_direction,
            bg=self.btn_bg_color, borderwidth=self.btn_borderwidth,
            relief=self.btn_relief, fg=self.btn_text_color, font=self.btn_font,
            activebackground=self.btn_active_bg_color, activeforeground=self.btn_active_fg_color
            )
        self.changes_dose_direction_btn.grid(column=0, row=0)
        # Medication Profile button
        self.changes_medication_profile_btn = tk.Button(
            self.changes_button_container, text='Medication Profile', command=self._select_medication_profile,
            bg=self.btn_bg_color, borderwidth=self.btn_borderwidth,
            relief=self.btn_relief, fg=self.btn_text_color, font=self.btn_font,
            activebackground=self.btn_active_bg_color, activeforeground=self.btn_active_fg_color
            )
        self.changes_medication_profile_btn.grid(column=1, row=0, padx=(self.btn_space_btwn, 0))
        # New Allergies button
        self.changes_allergies_btn = tk.Button(
            self.changes_button_container, text='New Allergies', command=self._select_new_allergies,
            bg=self.btn_bg_color, borderwidth=self.btn_borderwidth,
            relief=self.btn_relief, fg=self.btn_text_color, font=self.btn_font,
            activebackground=self.btn_active_bg_color, activeforeground=self.btn_active_fg_color
            )
        self.changes_allergies_btn.grid(column=2, row=0, padx=(self.btn_space_btwn, 0))

        # Changes Other & Medical Condition button container
        self.changes_other_med_cond_container = tk.Frame(
            self.changes_labelFrame, highlightthickness=0, bg=self.background_color
            )
        self.changes_other_med_cond_container.grid(column=0, row=1, sticky='w', padx=self.canvas_padx, pady=self.canvas_pady)
        # Medical Condition button
        self.changes_medical_condition_btn = tk.Button(
            self.changes_other_med_cond_container, text='Medical Condition', command=self._select_medical_condition,
            bg=self.btn_bg_color, borderwidth=self.btn_borderwidth,
            relief=self.btn_relief, fg=self.btn_text_color, font=self.btn_font,
            activebackground=self.btn_active_bg_color, activeforeground=self.btn_active_fg_color
            )
        self.changes_medical_condition_btn.grid(column=0, row=0)
        # Other changes button
        self.changes_other_btn = tk.Button(
            self.changes_other_med_cond_container, text='Other', command=self._select_other_changes,
            bg=self.btn_bg_color, borderwidth=self.btn_borderwidth,
            relief=self.btn_relief, fg=self.btn_text_color, font=self.btn_font,
            activebackground=self.btn_active_bg_color, activeforeground=self.btn_active_fg_color
            )
        self.changes_other_btn.grid(column=1, row=0, padx=(self.btn_space_btwn, 0))

        # Changes Notes container
        self.changes_notes_container = tk.Frame(
            self.changes_labelFrame, highlightthickness=0, width=364, height=64,
            bg=self.background_color
            )
        self.changes_notes_container.grid(
            column=0, row=2, sticky='w', padx=self.canvas_padx, pady=self.canvas_pady
            )
        self.changes_notes_container.grid_propagate(False)
        # Changes Notes Text box
        self.changes_notes_text_box = tk.Text(
            self.changes_notes_container, font=self.entry_font, wrap=WORD,
            width=40, height=3
            )
        self.changes_notes_text_box.grid(column=0, row=0)
        self.insert_placeholder_intervention_text_box(self.changes_notes_text_box)

        # === Side Effects label frame === #
        self.side_effects_labelFrame = tk.LabelFrame(
            self.intervention_window, text='Side Effects', bg=self.background_color,
            font=self.labelFrame_font, highlightthickness=0
            )
        self.side_effects_labelFrame.grid(column=0, row=2, sticky='we', pady=(self.labelFrame_space_btwn, 0))

        # Side effect button container
        self.side_effect_button_container = tk.Frame(
            self.side_effects_labelFrame, highlightthickness=0, bg=self.background_color
            )
        self.side_effect_button_container.grid(column=0, row=0, sticky='w', padx=self.canvas_padx, pady=self.canvas_pady)
        # Injection site reaction button
        self.injection_site_rxn_btn = tk.Button(
            self.side_effect_button_container, text='Injection site reaction', command=self._select_injection_site_rxn,
            bg=self.btn_bg_color, borderwidth=self.btn_borderwidth,
            relief=self.btn_relief, fg=self.btn_text_color, font=self.btn_font,
            activebackground=self.btn_active_bg_color, activeforeground=self.btn_active_fg_color
            )
        self.injection_site_rxn_btn.grid(column=1, row=0, padx=(self.btn_space_btwn, 0))
        # Hospitalized/ER Visit button
        self.hospitalize_er_btn = tk.Button(
            self.side_effect_button_container, text='Hospitalized/ER', command=self._select_hospitalized_er,
            bg=self.btn_bg_color, borderwidth=self.btn_borderwidth,
            relief=self.btn_relief, fg=self.btn_text_color, font=self.btn_font,
            activebackground=self.btn_active_bg_color, activeforeground=self.btn_active_fg_color
            )
        self.hospitalize_er_btn.grid(column=2, row=0, padx=(self.btn_space_btwn, 0))
        # Other side effects button
        self.side_effect_other_btn = tk.Button(
            self.side_effect_button_container, text='Other', command=self._select_other_side_effects,
            bg=self.btn_bg_color, borderwidth=self.btn_borderwidth,
            relief=self.btn_relief, fg=self.btn_text_color, font=self.btn_font,
            activebackground=self.btn_active_bg_color, activeforeground=self.btn_active_fg_color
            )
        self.side_effect_other_btn.grid(column=0, row=0)

        # Side effects Notes container
        self.side_effects_notes_container = tk.Frame(
            self.side_effects_labelFrame, highlightthickness=0, width=364, height=64,
            bg=self.background_color
            )
        self.side_effects_notes_container.grid(
            column=0, row=1, sticky='w', padx=self.canvas_padx, pady=self.canvas_pady
            )
        self.side_effects_notes_container.grid_propagate(False)
         # Side effects Notes container
        self.side_effects_notes_container = tk.Frame(
            self.side_effects_labelFrame, highlightthickness=0, width=364, height=64,
            bg=self.background_color
            )
        self.side_effects_notes_container.grid(
            column=0, row=1, sticky='w', padx=self.canvas_padx, pady=self.canvas_pady
            )
        self.side_effects_notes_container.grid_propagate(False)
        # Side effects Notes Text box
        self.side_effects_notes_text_box = tk.Text(
            self.side_effects_notes_container, font=self.entry_font, wrap=WORD,
            width=40, height=3
            )
        self.side_effects_notes_text_box.grid(column=0, row=0)
        self.insert_placeholder_intervention_text_box(self.side_effects_notes_text_box)

        # === Adherence label frame === #
        self.adherence_labelFrame = tk.LabelFrame(
            self.intervention_window, text='Adherence', bg=self.background_color,
            font=self.labelFrame_font, highlightthickness=0
            )
        self.adherence_labelFrame.grid(column=0, row=3, sticky='we', pady=(self.labelFrame_space_btwn, 0))

         # Adherence notes container
        self.adherence_notes_container = tk.Frame(
            self.adherence_labelFrame, highlightthickness=0, width=364, height=64,
            bg=self.background_color
            )
        self.adherence_notes_container.grid(column=0, row=0, sticky='w', padx=self.canvas_padx, pady=self.canvas_pady)
        self.adherence_notes_container.grid_propagate(False)
        # Adherence Notes Text box
        self.adherence_notes_text_box = tk.Text(
            self.adherence_notes_container, font=self.entry_font, wrap=WORD,
            width=40, height=3
            )
        self.adherence_notes_text_box.grid(column=0, row=0)
        self.insert_placeholder_intervention_text_box(self.adherence_notes_text_box)

        # === Additional Notes label frame === #
        self.additional_notes_labelFrame = tk.LabelFrame(
            self.intervention_window, text='Additional Notes', bg=self.background_color,
            font=self.labelFrame_font, highlightthickness=0
            )
        self.additional_notes_labelFrame.grid(column=0, row=4, sticky='we', pady=(self.labelFrame_space_btwn, 0))

         # Additional notes container
        self.additional_notes_container = tk.Frame(
            self.additional_notes_labelFrame, highlightthickness=0, width=364, height=75,
            bg=self.background_color
            )
        self.additional_notes_container.grid(column=0, row=0, sticky='w', padx=self.canvas_padx, pady=self.canvas_pady)
        self.additional_notes_container.grid_propagate(False)
        # Additional Notes Text box
        self.additional_notes_text_box = tk.Text(
            self.additional_notes_container, font=self.entry_font, wrap=WORD,
            width=40, height=4
            )
        self.additional_notes_text_box.grid(column=0, row=0)
        self.insert_placeholder_intervention_text_box(self.additional_notes_text_box)

        self.intervention_window.protocol('WM_DELETE_WINDOW', self.toggle_intervention_window)

        # ~ ~ ~ bind ~ ~ ~ #
        self.changes_notes_text_box.bind('<FocusIn>', lambda e: self.remove_placeholder_intervention_text_box(self.changes_notes_text_box, e))
        self.changes_notes_text_box.bind('<FocusOut>', lambda e: self.insert_placeholder_intervention_text_box(self.changes_notes_text_box, e))
        self.side_effects_notes_text_box.bind('<FocusIn>', lambda e: self.remove_placeholder_intervention_text_box(self.side_effects_notes_text_box, e))
        self.side_effects_notes_text_box.bind('<FocusOut>', lambda e: self.insert_placeholder_intervention_text_box(self.side_effects_notes_text_box, e))
        self.adherence_notes_text_box.bind('<FocusIn>', lambda e: self.remove_placeholder_intervention_text_box(self.adherence_notes_text_box, e))
        self.adherence_notes_text_box.bind('<FocusOut>', lambda e: self.insert_placeholder_intervention_text_box(self.adherence_notes_text_box, e))
        self.additional_notes_text_box.bind('<FocusIn>', lambda e: self.remove_placeholder_intervention_text_box(self.additional_notes_text_box, e))
        self.additional_notes_text_box.bind('<FocusOut>', lambda e: self.insert_placeholder_intervention_text_box(self.additional_notes_text_box, e))

        # ~ ~ ~ Check user ~ ~ ~ #
        if self.user:
            self.top.title(f'Refill Coordination - {self.user}')
            self.center_refill_coordination_window()
            self.top.deiconify()
            self.medication_entry.focus()
        else:
            relative_path = '.data'
            if getattr(sys, 'frozen', False):
                application_path = os.path.dirname(sys.executable)
            elif __file__:
                application_path = os.path.dirname(__file__)

            absolute_path = os.path.join(application_path, relative_path)
            if not os.path.exists(absolute_path):
                self._create_data_dir(absolute_path)

            self.user_setup_window()


    def center_refill_coordination_window(self):
        """Center Refill Coordination window to monitor screen."""
        self.top.update_idletasks()
        win_width = self.top.winfo_reqwidth()
        win_height = self.top.winfo_reqheight()
        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        x = int(screen_width/2 - win_width/2)
        y = int(screen_height/2 - win_width/2)
        self.top.geometry(f"{win_width}x{win_height}+{x}+{y}")

    def select_injection(self):
        """Select injection button."""
        self.injection_btn.config(bg=self.select_btn_bg_color, command=self._unselect_injection_cycle)
        self.cycle_btn.config(bg=self.btn_bg_color, command=self.select_cycle)
        self.injection_cycle = 'Injection is due'
        self.due_start_label.config(text='is due')
        self.due_start_entry.config(state='normal')
        self.top.focus()
        if not self.day_supply_entry.get().strip():
            self.day_supply_entry.insert(0, '0')

    def select_cycle(self):
        """Select cycle button."""
        self.injection_btn.config(bg=self.btn_bg_color, command=self.select_injection)
        self.cycle_btn.config(bg=self.select_btn_bg_color, command=self._unselect_injection_cycle)
        self.injection_cycle = 'Next cycle starts'
        self.due_start_label.config(text='starts')
        self.due_start_entry.config(state='normal')
        self.top.focus()
        if not self.day_supply_entry.get().strip():
            self.day_supply_entry.insert(0, '0')
    
    def _unselect_injection_cycle(self):
        """Unselect injection/cycle button."""
        self.injection_btn.config(bg=self.btn_bg_color, command=self.select_injection)
        self.cycle_btn.config(bg=self.btn_bg_color, command=self.select_cycle)
        self.injection_cycle = ''
        self.due_start_label.config(text='')
        self.due_start_entry.delete(0, 'end')
        self.due_start_entry.config(state='disabled')

    def select_dcs(self):
        """Select DCS button."""
        self.dispense_dcs_btn.config(bg=self.select_btn_bg_color, command=self._unselect_dcs_fedex)
        self.dispense_fedex_btn.config(bg=self.btn_bg_color, command=self.select_fedex)
        self.dispense_pickup_btn.config(bg=self.btn_bg_color, command=self.select_pickup)
        self.dispense_walkover_btn.config(bg=self.btn_bg_color, command=self.select_walkover)
        self.dispense_method = 'DCS'
        self.dispense_walkover_entry.delete(0, 'end')
        self.dispense_walkover_entry.config(state='disabled')
        self.dispense_date_label.config(text='Shipping out on', fg=self.text_color)
        self.dispense_date_entry.config(state='normal')
        if self.signature_required == '':
            self.dispense_signature_yes_btn.config(state='normal', bg=self.btn_bg_color)
            self.dispense_signature_no_btn.config(state='normal', bg=self.btn_bg_color)
        self.dispense_signature_label.config(fg=self.text_color)
        self.fedex_delivery_pick_time_label.config(text='')
        self._remove_pickup_time_label_entry()

    def select_fedex(self):
        """Select FedEx button."""
        self.dispense_dcs_btn.config(bg=self.btn_bg_color, command=self.select_dcs)
        self.dispense_fedex_btn.config(bg=self.select_btn_bg_color, command=self._unselect_dcs_fedex)
        self.dispense_pickup_btn.config(bg=self.btn_bg_color, command=self.select_pickup)
        self.dispense_walkover_btn.config(bg=self.btn_bg_color, command=self.select_walkover)
        self.dispense_method = 'FedEx'
        self.dispense_walkover_entry.delete(0, 'end')
        self.dispense_walkover_entry.config(state='disabled')
        self.dispense_date_label.config(text='Shipping out on', fg=self.text_color)
        self.dispense_date_entry.config(state='normal')
        if self.signature_required == '':
            self.dispense_signature_yes_btn.config(state='normal', bg=self.btn_bg_color)
            self.dispense_signature_no_btn.config(state='normal', bg=self.btn_bg_color)
        self.dispense_signature_label.config(fg=self.text_color)
        self._remove_pickup_time_label_entry()


    def select_pickup(self):
        """Select Pick Up button."""
        self.dispense_dcs_btn.config(bg=self.btn_bg_color, command=lambda: [self.select_dcs(), self._enable_yes_no_btn()])
        self.dispense_fedex_btn.config(bg=self.btn_bg_color, command=lambda: [self.select_fedex(), self._enable_yes_no_btn()])
        self.dispense_pickup_btn.config(bg=self.select_btn_bg_color, command=self._unselect_pickup_walkover)
        self.dispense_walkover_btn.config(bg=self.btn_bg_color, command=self.select_walkover)
        self.dispense_method = 'Pick up'
        self.dispense_walkover_entry.delete(0, 'end')
        self.dispense_walkover_entry.config(state='disabled')
        self.dispense_signature_yes_btn.config(state='disabled', bg=self.btn_disabled_bg_color)
        self.dispense_signature_no_btn.config(state='disabled', bg=self.btn_disabled_bg_color)
        self.signature_required = ''
        self.dispense_signature_label.config(fg=self.disabled_text_color)
        self.dispense_date_label.config(text='Picking up on', fg=self.text_color)
        self.dispense_date_entry.config(state='normal')
        self.fedex_delivery_pick_time_label.config(text='')

    def select_walkover(self):
        """Select Walkover button."""
        self.dispense_dcs_btn.config(bg=self.btn_bg_color, command=lambda: [self.select_dcs(), self._enable_yes_no_btn()])
        self.dispense_fedex_btn.config(bg=self.btn_bg_color, command=lambda: [self.select_fedex(), self._enable_yes_no_btn()])
        self.dispense_pickup_btn.config(bg=self.btn_bg_color, command=self.select_pickup)
        self.dispense_walkover_btn.config(bg=self.select_btn_bg_color, command=self._unselect_pickup_walkover)
        self.dispense_method = 'Walk over'
        self.dispense_walkover_entry.config(state='normal')
        self.dispense_walkover_entry.insert(0, '-> enter location <-')
        self.dispense_signature_yes_btn.config(state='disabled', bg=self.btn_disabled_bg_color)
        self.dispense_signature_no_btn.config(state='disabled', bg=self.btn_disabled_bg_color)
        self.signature_required = ''
        self.dispense_signature_label.config(fg=self.disabled_text_color)
        self.dispense_date_label.config(text='Walking over on', fg=self.text_color)
        self.dispense_date_entry.config(state='normal')
        self.fedex_delivery_pick_time_label.config(text='')
        self._remove_pickup_time_label_entry()
        self.top.focus()
        
    def remove_temp_text(self, e):
        """Remove temporary text from walk over entry box."""
        if self.dispense_walkover_entry.get() == '-> enter location <-':
            self.dispense_walkover_entry.delete(0, 'end')

    def _unselect_dcs_fedex(self):
        """Unselect DCS/FedEx button."""
        self.dispense_dcs_btn.config(bg=self.btn_bg_color, command=self.select_dcs)
        self.dispense_fedex_btn.config(bg=self.btn_bg_color, command=self.select_fedex)
        self.dispense_pickup_btn.config(bg=self.btn_bg_color, command=self.select_pickup)
        self.dispense_walkover_btn.config(bg=self.btn_bg_color, command=self.select_walkover)
        self.dispense_method = ''
        self.dispense_walkover_entry.delete(0, 'end')
        self.dispense_walkover_entry.config(state='disabled')
        self.dispense_date_label.config(text='Dispense Date:', fg=self.btn_disabled_fg_color)
        self.dispense_date_entry.delete(0, 'end')
        self.dispense_date_entry.config(state='disabled')
        self.signature_required = ''
        self.dispense_signature_label.config(fg=self.disabled_text_color)
        self.dispense_signature_yes_btn.config(state='disabled', bg=self.btn_disabled_bg_color)
        self.dispense_signature_no_btn.config(state='disabled', bg=self.btn_disabled_bg_color)
        self.fedex_delivery_pick_time_label.config(text='')
        self.dispense_signature_yes_btn.config(command=self.select_yes_sig)
        self.dispense_signature_no_btn.config(command=self.select_no_sig)
  
    def _unselect_pickup_walkover(self):
        """Unselect Pick Up/Walk Over button."""
        self.dispense_dcs_btn.config(bg=self.btn_bg_color, command=self.select_dcs)
        self.dispense_fedex_btn.config(bg=self.btn_bg_color, command=self.select_fedex)
        self.dispense_pickup_btn.config(bg=self.btn_bg_color, command=self.select_pickup)
        self.dispense_walkover_btn.config(bg=self.btn_bg_color, command=self.select_walkover)
        self.dispense_method = ''
        self.dispense_walkover_entry.delete(0, 'end')
        self.dispense_walkover_entry.config(state='disabled')
        self.dispense_signature_yes_btn.config(state='normal', bg=self.btn_bg_color, command=self.select_yes_sig)
        self.dispense_signature_no_btn.config(state='normal', bg=self.btn_bg_color, command=self.select_no_sig)
        self.dispense_date_label.config(text='Dispense Date:', fg=self.btn_disabled_fg_color)
        self.dispense_date_entry.delete(0, 'end')
        self.dispense_date_entry.config(state='disabled')
        self.signature_required = ''
        self.dispense_signature_label.config(fg=self.disabled_text_color)
        self.dispense_signature_yes_btn.config(state='disabled', bg=self.btn_disabled_bg_color)
        self.dispense_signature_no_btn.config(state='disabled', bg=self.btn_disabled_bg_color)
        self._remove_pickup_time_label_entry()

    def _enable_yes_no_btn(self):
        """Enable Yes and No buttons when selecting away from Pick Up or Walk Over."""
        self.dispense_signature_yes_btn.config(
            state='normal', bg=self.btn_bg_color, command=self.select_yes_sig,
            fg=self.btn_text_color
            )
        self.dispense_signature_no_btn.config(
            state='normal', bg=self.btn_bg_color, command=self.select_no_sig,
            fg=self.btn_text_color
            )

    def select_yes_sig(self):
        """Select Yes signature button."""
        self.dispense_signature_yes_btn.config(bg=self.select_btn_bg_color, command=self._unselect_yes_no_sig) 
        self.dispense_signature_no_btn.config(bg=self.btn_bg_color, command=self.select_no_sig)
        self.signature_required = 'SIG REQUIRED'

    def select_no_sig(self):
        """Select No signature button."""
        self.dispense_signature_yes_btn.config(bg=self.btn_bg_color, command=self.select_yes_sig) 
        self.dispense_signature_no_btn.config(bg=self.select_btn_bg_color, command=self._unselect_yes_no_sig)
        self.signature_required = 'no sig'

    def _unselect_yes_no_sig(self):
        """Unselect Yes/No signature button."""
        self.dispense_signature_yes_btn.config(bg=self.btn_bg_color, command=self.select_yes_sig) 
        self.dispense_signature_no_btn.config(bg=self.btn_bg_color, command=self.select_no_sig)
        self.signature_required = ''

    def select_a_little(self):
        """Select working 'A little' button."""
        self.medication_efficacy_alittle_btn.config(bg=self.select_btn_bg_color, command=self._unselect_alittle_alot_cant_tell)
        self.medication_efficacy_alot_btn.config(bg=self.btn_bg_color, command=self.select_a_lot)
        self.medication_efficacy_cantTell_btn.config(bg=self.btn_bg_color, command=self.select_cant_tell)
        self.medication_working = 'Yes, it\'s working a little.'

    def select_a_lot(self):
        """Select working 'A lot' button."""
        self.medication_efficacy_alittle_btn.config(bg=self.btn_bg_color, command=self.select_a_little)
        self.medication_efficacy_alot_btn.config(bg=self.select_btn_bg_color, command=self._unselect_alittle_alot_cant_tell)
        self.medication_efficacy_cantTell_btn.config(bg=self.btn_bg_color, command=self.select_cant_tell)
        self.medication_working = 'Yes, it\'s working a lot.'

    def select_cant_tell(self):
        """Select "Can't tell" button."""
        self.medication_efficacy_alittle_btn.config(bg=self.btn_bg_color, command=self.select_a_little)
        self.medication_efficacy_alot_btn.config(bg=self.btn_bg_color, command=self.select_a_lot)
        self.medication_efficacy_cantTell_btn.config(bg=self.select_btn_bg_color, command=self._unselect_alittle_alot_cant_tell)
        self.medication_working = 'No, I don\'t feel a difference.'

    def _unselect_alittle_alot_cant_tell(self):
        """Unselect a little/a lot/can't tell button."""
        self.medication_efficacy_alittle_btn.config(bg=self.btn_bg_color, command=self.select_a_little)
        self.medication_efficacy_alot_btn.config(bg=self.btn_bg_color, command=self.select_a_lot)
        self.medication_efficacy_cantTell_btn.config(bg=self.btn_bg_color, command=self.select_cant_tell)
        self.medication_working = ''

    def clear(self, e=None):
        """Clear all inputs."""
        self.medication_entry.delete(0, 'end')
        self.day_supply_entry.delete(0, 'end')
        self.dispense_date_entry.delete(0, 'end')
        self.dispense_comments_entry.delete(0, 'end')
        self.spoke_with_entry.delete(0, 'end')
        self._remove_pickup_time_label_entry()

        self.dispense_date_entry.set_date(dt.date.today())
        
        self._unselect_injection_cycle()
        self._unselect_yes_no_sig()
        self._unselect_dcs_fedex()
        self._unselect_alittle_alot_cant_tell()

        win32clipboard.OpenClipboard(0)
        win32clipboard.EmptyClipboard()
        win32clipboard.CloseClipboard()

        for unselect_method in [self._unselect_dose_direction,
                                self._unselect_medication_profile,
                                self._unselect_new_allergies,
                                self._unselect_medical_condition,
                                self._unselect_other_changes,
                                self._unselect_injection_site_rxn,
                                self._unselect_hospitalized_er,
                                self._unselect_other_side_effects]:
            try:
                unselect_method()
            except ValueError:
                pass
        
        self.clear_intervention_text_box(self.changes_notes_text_box)
        self.clear_intervention_text_box(self.side_effects_notes_text_box)
        self.clear_intervention_text_box(self.adherence_notes_text_box)
        self.clear_intervention_text_box(self.additional_notes_text_box)
        if self.intervention:
            self.toggle_intervention_window()
            
        self.medication_entry.focus()

    def run_validations(self):
        """Recursively execute various validation methods."""
        self._validate_copy_btns()
        self._validate_fedex_delivery_pick_time_label()
        self._update_variables()

        self.top.after(ms=50, func=self.run_validations)
    
    def _validate_copy_btns(self):
        """Check and enable copy buttons if conditions are met."""
        copy_wam_notes_conditions_met = self._check_copy_wam_notes_conditions()
        copy_template_conditions_met = self._check_copy_template_conditions()
        if copy_wam_notes_conditions_met:
            self.copy_wam_notes_btn.config(state='normal')
            if copy_template_conditions_met:
                self.copy_template_btn.config(state='normal')
            else:
                self.copy_template_btn.config(state='disabled')
        elif copy_template_conditions_met:
            if copy_wam_notes_conditions_met:
                self.copy_template_btn.config(state='normal')
            else:
                self.copy_wam_notes_btn.config(state='disabled')
                self.copy_template_btn.config(state='disabled')
        else:
            self.copy_wam_notes_btn.config(state='disabled')
            self.copy_template_btn.config(state='disabled')

    def _check_copy_wam_notes_conditions(self) -> bool:
        """Check if Copy WAM Notes conditions are met."""
        dispense_date_entry_not_empty = self.dispense_date_entry.get().strip()
        pickup_time_not_empty = self.dispense_pickup_time_entry.get().strip()
        walkover_location = self.dispense_walkover_entry.get().strip()
        if self.dispense_method in ('DCS', 'FedEx') and dispense_date_entry_not_empty and self.signature_required\
        or self.dispense_method == 'Pick up' and dispense_date_entry_not_empty and pickup_time_not_empty\
        or self.dispense_method == 'Walk over' and dispense_date_entry_not_empty and walkover_location not in ('-> enter location <-', ''):
            return True
        else:
            return False
        

    def _check_copy_template_conditions(self) -> bool:
        """Check if Copy Template conditions are met."""
        medication_entry_not_empty = self.medication_entry.get().strip()
        day_supply_entry_not_empty = self.day_supply_entry.get().strip()
        if medication_entry_not_empty and day_supply_entry_not_empty and self.medication_working and self.spoke_with:
            return True
        else:
            return False
        
    def _remove_pickup_time_label_entry(self):
        """Remove pick up time label and entry widgets."""
        self.dispense_pickup_time_entry.delete(0, 'end')
        self.dispense_pickup_time_entry.config(width=0, state='disable')
        self.fedex_delivery_pick_time_label.config(text='')

    def _validate_fedex_delivery_pick_time_label(self):
        """Check and enable FedEx delivery date label."""
        if self.dispense_method == 'FedEx':
            self._remove_pickup_time_label_entry()
            valid_delivery_date = self._calculate_fedex_delivery_date()
            if valid_delivery_date:
                self.dispense_pickup_time_entry.config(width=0)
                self.fedex_delivery_date = valid_delivery_date
                self.fedex_delivery_pick_time_label.config(text=f'for {self.fedex_delivery_date} delivery')
            else:
                self.fedex_delivery_date = ''
                self.fedex_delivery_pick_time_label.config(text='')
        elif self.dispense_method == 'Pick up':
            self.fedex_delivery_pick_time_label.config(text='Time:')
            self.dispense_pickup_time_entry.config(width=12, state='normal')
        else:
            self.fedex_delivery_date = ''
            self._remove_pickup_time_label_entry()


    def _calculate_fedex_delivery_date(self) -> str:
        """Calculate FedEx delivery date."""
        if self.dispense_date_entry.get().strip():   
            entered_ship_date = self.dispense_date_entry.get_date()
            delivery_date = entered_ship_date + dt.timedelta(days=1)
            return f'{delivery_date.month}/{delivery_date.day}'
        else:
            return ''
      
        
    def _update_variables(self):
        """Update variables from entry."""
        self.spoke_with = self.spoke_with_entry.get().strip()

    def get_existing_user(self) -> str:
        """Get existing user from user.json file."""
        try:
            with open('.data/user.json', 'r') as f:
                data = json.load(f)
                first_name = data['first_name']
                last_name = data['last_name']
                if first_name and last_name:
                    return f'{first_name} {last_name}'
                else:
                    raise Exception()
        except:
            return ''

    def _create_user_json(self, first_name: str, last_name: str):
        """Create user.json file."""
        with open('.data/user.json', 'w') as f:
            data = {'first_name': first_name, 'last_name': last_name}
            json.dump(data, f, indent=4)
    
    def _create_data_dir(self, path: str):
        """Create .data directory."""
        os.mkdir(path)
        subprocess.call(["attrib", "+h", path]) # hidden directory

    def user_setup_window(self, e=None):
        """Graphic user interface for setting up a new user."""

        def flash(entry_box, counter=4, color='#ffd7d0'):
            """Flash the given entry box a certain number of times."""
            duration1 = 100
            duration2 = 200
            for _ in range(counter):
                setup_window.after(duration1, lambda: entry_box.config(bg=color))
                setup_window.after(duration2, lambda: entry_box.config(bg=self.entry_bg_color))
                duration1 += 200
                duration2 += 200

        def confirm_user(e=None):
            """Confirm user first and last name."""
            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()

            if first_name and last_name:
                first_name_title = first_name.title()
                last_name_title = last_name.title()
                self._create_user_json(first_name_title, last_name_title)
                self.user = f'{first_name_title} {last_name_title}'
                self.top.title(f'Refill Coordination - {self.user}')
                self.top.attributes('-disabled', 0)
                self.top.deiconify()
                self.medication_entry.focus()
                setup_window.destroy()
            else:
                if first_name == '':
                    flash(first_name_entry)
                if last_name == '':
                    flash(last_name_entry)

        setup_window = tk.Toplevel(self.top)
        setup_window.withdraw()
        setup_window.title('User Setup')
        setup_window.config(bg=self.background_color, padx=20, pady=20)
        setup_window.resizable(False, False)

        first_name_label = tk.Label(
            setup_window, text='First Name:', bg=self.background_color, font=self.label_font
            )
        first_name_label.grid(column=0, row=0, padx=5)
        first_name_entry = tk.Entry(
            setup_window, font=self.entry_font, bg=self.entry_bg_color, relief=self.entry_relief
            )
        first_name_entry.grid(column=1, row=0, pady=(0, 5))
        
        last_name_label = tk.Label(
            setup_window, text='Last Name:', bg=self.background_color, font=self.label_font
            )
        last_name_label.grid(column=0, row=1, padx=5)
        last_name_entry = tk.Entry(
            setup_window, font=self.entry_font, bg=self.entry_bg_color, relief=self.entry_relief
            )
        last_name_entry.grid(column=1, row=1)

        ok_btn = tk.Button(
            setup_window, text='OK', bg=self.copy_btn_bg_color, relief='raised',
            font=self.btn_font, activebackground=self.copy_btn_bg_color, width=9,
            command=confirm_user
            )
        ok_btn.grid(column=0, row=2, columnspan=2, pady=(5, 0))

        # Center setup window to screen
        if self.user == '':
            setup_window.update_idletasks()
            setup_window_width = setup_window.winfo_reqwidth()
            setup_window_height = setup_window.winfo_reqheight()
            screen_width = setup_window.winfo_screenwidth()
            screen_height = setup_window.winfo_screenheight()
            x = int(screen_width/2 - setup_window_width/2)
            y = int(screen_height/2 - setup_window_width/2)
            setup_window.geometry(f"{setup_window_width}x{setup_window_height}+{x}+{y}")
            
        else: # center setup window to top window
            setup_window.update_idletasks()
            top_x = self.top.winfo_x()
            top_y = self.top.winfo_y()
            top_width = self.top.winfo_reqwidth()
            top_height = self.top.winfo_reqheight()
            setup_window_width = setup_window.winfo_reqwidth()
            setup_window_height = setup_window.winfo_reqheight()
            dx = int((top_width / 2) - (setup_window_width / 2))
            dy = int((top_height / 2) - (setup_window_height / 2))
            setup_window.geometry('+%d+%d' % (top_x + dx, top_y + dy))

        self.top.attributes('-disabled', 1)
        setup_window.wm_transient(self.top)
        setup_window.deiconify()
        first_name_entry.focus()
        
        setup_window.protocol('WM_DELETE_WINDOW', lambda: self.on_closing_user_setup_window(setup_window))

        setup_window.bind('<Return>', confirm_user)
        setup_window.bind('<Escape>', lambda e: self.on_closing_user_setup_window(setup_window, e))

    def on_closing_user_setup_window(self, setup_window, e=None):
        """Enable top window on closing user setup window."""
        if self.user == '':
            sys.exit()

        self.top.attributes('-disabled', 0)
        self.top.deiconify()
        self.medication_entry.focus()
        setup_window.destroy()

    def copy_rtf_to_clipboard(self, formatted_text: str):
        """Copy formatted rich text to clipboard."""
        rtf = bytearray(fr'{{\rtf1\ansi\deff0 {{\fonttbl {{\f0 Arial;}}}}{{\colortbl;\red0\green0\blue0;\red255\green0\blue0;\red255\green255\blue0;}} {formatted_text}}}', 'utf8')
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
        dispense_date = self.dispense_date_entry.get_date()
        return f'{dispense_date.month}/{dispense_date.day}'
    

    def format_wam_notes(self, format='plain') -> str:
        """Format WAM notes with plain or rich text."""
        dispense_comments = self.dispense_comments_entry.get().capitalize()
        if format == 'plain':
            wam_notes = f'{self.dispense_method} {self.get_formatted_dispense_date()}' 
            if self.dispense_method == 'DCS':
                wam_notes += f', {self.signature_required}'
                if dispense_comments:
                    wam_notes += f'\n{dispense_comments}'
                    
            elif self.dispense_method == 'FedEx':
                wam_notes += f' for {self.fedex_delivery_date} delivery, {self.signature_required}'       
                if dispense_comments:
                    wam_notes += f'\n{dispense_comments}'

            elif self.dispense_method == 'Pick up':
                pickup_time = self.dispense_pickup_time_entry.get().strip()
                if pickup_time[0].isdigit():
                    wam_notes += f' at'
                
                wam_notes += f' {pickup_time}'
                if dispense_comments:
                    wam_notes += f'\n{dispense_comments}'
            else:
                wam_notes += f' to {self.dispense_walkover_entry.get().upper()}'
                if dispense_comments:
                    wam_notes += f'\n{dispense_comments}'
                    
        elif format == 'rich':
            wam_notes = fr'{{{self.dispense_method}}} {{{self.get_formatted_dispense_date()}}}' 
            if self.dispense_method == 'DCS':
                wam_notes += fr', {{{self.signature_required}}}'
                if dispense_comments:
                    wam_notes += fr'\line{{{dispense_comments}}}'
                
            elif self.dispense_method == 'FedEx':
                wam_notes += fr' for {{{self.fedex_delivery_date}}} delivery, {{{self.signature_required}}}'     
                if dispense_comments:
                    wam_notes += fr'\line{{{dispense_comments}}}'

            elif self.dispense_method == 'Pick up':
                pickup_time = self.dispense_pickup_time_entry.get().strip()
                if pickup_time[0].isdigit():
                    wam_notes += fr' at'
                    
                wam_notes += fr' {{{pickup_time}}}'
                if dispense_comments:
                    wam_notes += fr'\line{{{dispense_comments}}}'

            else:
                wam_notes += fr' to {{{self.dispense_walkover_entry.get().upper()}}}'
                if dispense_comments:
                    wam_notes += fr'\line{{{dispense_comments}}}'
                
        return wam_notes
    
    def format_template_notes(self) -> str:
        """Format Template notes with rich text."""

        medication = self.medication_entry.get().strip().capitalize()
        if self.dispense_method == 'Pick up':
            hipaa_verification = 'Name, DOB, Drug Prescribed'
        else:
            hipaa_verification = 'Name, DOB, Address, Drug Prescribed'
        
        ready_to_fill = 'Yes, refill initiated in WAM.'
        days_supply = self.day_supply_entry.get().strip()
        injection_cycle_date = self.due_start_entry.get().strip()
        if injection_cycle_date:
            next_injection_cycle_due = f' {self.injection_cycle} {injection_cycle_date}'
        else:
            next_injection_cycle_due = ''

        delivery_pickup = self.dispense_method
        if delivery_pickup == 'Walk over':
            delivery_pickup = 'Clinic delivery'

        dispense_date = self.format_wam_notes(format='rich')
        allergies_reviewed = 'Yes'
        medication_review = 'Yes,'
        spoke_with = self.spoke_with_entry.get().strip()
        if spoke_with.lower() in ('patient', 'the patient', 'pt', 'pateint', 'thepatient', 'patients'):
            medication_review_confirmation = 'patient confirmation.'
        else:
            medication_review_confirmation = fr'other.\
Confirmed with {spoke_with}'
  
        medical_conditions_review = 'Yes'
        continuation_therapy = 'Yes'
        med_working = self.medication_working
        goal = 'Yes' 
        user = self.user
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

        if self.intervention:
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
                
                changes_notes = self.get_notes_from_text_box(self.changes_notes_text_box)
                if changes_notes:
                    changes += f'\line\line\t {changes_notes}'

            if self.new_allergies == 'Yes':
                new_allergies = 'Yes - updated new allergies'
            if self.new_medication == 'Yes':
                new_medications = 'Yes'
            if self.medical_conditions_changes != 'None':
                medical_condition_changes = self.medical_conditions_changes
            if self.symptoms_reported:
                number_of_different_symptoms = len(self.symptoms_reported)
                # Move 'Other' to the end of the list
                if 'Other' in self.symptoms_reported and number_of_different_symptoms > 1:
                    self.symptoms_reported.append(self.symptoms_reported.pop(self.symptoms_reported.index('Other')))
                review_symptoms = fr''
                if number_of_different_symptoms == 1:
                    review_symptoms = self.symptoms_reported[0]
                elif number_of_different_symptoms == 2:
                    review_symptoms = fr'{{{self.symptoms_reported[0]}}} and {{{self.symptoms_reported[1]}}}'
                else:
                    for _symptom in self.symptoms_reported:
                        if _symptom == self.symptoms_reported[-1]:
                            review_symptoms += ', and '
                        else:
                            review_symptoms += ', '
                        review_symptoms += _symptom
                    review_symptoms = review_symptoms[2:]
                
                symptom_notes = self.get_notes_from_text_box(self.side_effects_notes_text_box)
                if symptom_notes:
                    review_symptoms += fr'\line\tab {symptom_notes}'
                review_symptoms += fr'\line\line\tab If side-effect reported, documented by tech. If documented by tech, triage to RPh? Yes.\line'
                intervention_necessary = 'Yes. Routed to RPH.'

            adherence_notes = self.get_notes_from_text_box(self.adherence_notes_text_box)
            if adherence_notes:
                adherence = 'NOT ADHERENT'
                embedded_adherence_notes = fr'\line\line\tab {adherence_notes}'

        template = fr'\b\fs26Refill Reminder\b0\fs24\
\
Medication: {{{medication}}}\
\
Methods of HIPAA Verification: {{{hipaa_verification}}}\
\
Changes Since Last Visit: {{{changes}}}\
\
Is patient ready to fill? {{{ready_to_fill}}}\
\
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
\
\b\fs26 Medical Conditions Review \b0\fs24\
Medical conditions review was performed: {{{medical_conditions_review}}}\
Were there changes to the medical condition? {{{medical_condition_changes}}}\
\
\b\fs26 Is continuation of therapy appropriate: \b0\fs24 {{{continuation_therapy}}}\
\
\b\fs26 Do you feel like this medication is working for you:\b0\fs24  {{{med_working}}}\
\
Has the patient reported experiencing any of the following? {{{review_symptoms}}}\
Is intervention necessary (if yes for any above): {{{intervention_necessary}}}\
\
Patient is {{{adherence}}} to therapy.{{{embedded_adherence_notes}}}\
\
***\
\
GOAL: Is patient meeting goal? {{{goal}}}\
\
Does patient need to speak to a pharmacist? {{{speak_to_rph}}}\
\
{{{user}}}\
Specialty Pharmacy'

        if self.intervention:
            additional_notes = self.get_notes_from_text_box(self.additional_notes_text_box)
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


    def insert_placeholder_intervention_text_box(self, text_widget, e=None):
        """Insert a placeholder text at the center inside intervention text box."""
        if not text_widget.get(1.0, 'end').split():
            text_widget.config(fg=self.placeholder_text_color, font=self.placeholder_text_font)
            text_widget.insert(1.0, '\t    Notes')
       
        

    def remove_placeholder_intervention_text_box(self, text_widget, e=None):
        """Remove placeholder text inside intervention text box."""
        if text_widget.get(1.0, 'end').split()[0] == 'Notes':
            text_widget.delete(1.0, 'end')
            text_widget.config(
                fg=self.text_color, font=self.entry_font
                )
    
    def clear_intervention_text_box(self, text_widget):
        """Clear contents of intervention text box."""
        text_widget.delete(1.0, 'end')
        text_widget.config(fg=self.placeholder_text_color, font=self.placeholder_text_font)
        text_widget.insert(1.0, '\t    Notes')
        
    def sync_windows(self, event=None):
        """Attach intervention window to root window on the left."""
        if self.intervention:
            x = self.top.winfo_x() - self.top.winfo_width() + 26
            y = self.top.winfo_y()
            self.intervention_window.geometry("+%d+%d" % (x,y))
            self.intervention_window.lift()
        else:
            self.intervention_window.withdraw()
        
    def toggle_intervention_window(self):
        """Toggle intervention window."""
        if self.intervention:
            self.intervention = False
            self.intervention_window.withdraw()
            self.intervention_btn.config(relief='raised', fg=self.text_color)
        else:
            self.intervention = True
            self.sync_windows()
            self.intervention_window.deiconify()
            self.intervention_btn.config(relief='sunken', fg='red2')
            self.intervention_window.focus()

    def _select_dose_direction(self):
        """Select Dose/Direction button."""
        self.changes_dose_direction_btn.config(
            bg=self.select_btn_bg_color, command=self._unselect_dose_direction
            )
        self.changes.append('Change to dose/directions of current medication')
    
    def _unselect_dose_direction(self):
        """Unselect Dose/Direction button."""
        self.changes_dose_direction_btn.config(
            bg=self.btn_bg_color, command=self._select_dose_direction
            )
        self.changes.remove('Change to dose/directions of current medication')

    def _select_medication_profile(self):
        """Select Medication Profile button."""
        self.changes_medication_profile_btn.config(
            bg=self.select_btn_bg_color, command=self._unselect_medication_profile
            )
        self.changes.append('Change to medication profile')
        self.new_medication = 'Yes'

    def _unselect_medication_profile(self):
        """Unselect Medication Profile button."""
        self.changes_medication_profile_btn.config(
            bg=self.btn_bg_color, command=self._select_medication_profile
            )
        self.changes.remove('Change to medication profile')
        self.new_medication = 'No'

    def _select_new_allergies(self):
        """Select New Allergies button."""
        self.changes_allergies_btn.config(
            bg=self.select_btn_bg_color, command=self._unselect_new_allergies
            )
        self.changes.append('Changes in allergies')
        self.new_allergies = 'Yes'

    def _unselect_new_allergies(self):
        """Unselect New Allergies button."""
        self.changes_allergies_btn.config(
            bg=self.btn_bg_color, command=self._select_new_allergies
            )
        self.changes.remove('Changes in allergies')
        self.new_allergies = 'No'

    def _select_medical_condition(self):
        """Select Medical Condition button."""
        self.changes_medical_condition_btn.config(
            bg=self.select_btn_bg_color, command=self._unselect_medical_condition
            )
        self.changes.append('New Medication Condition(s)')
        self.medical_conditions_changes = 'Yes - Noted new additions of medical conditions and appropriately documented.'

    def _unselect_medical_condition(self):
        """Unselect Medical Condition button."""
        self.changes_medical_condition_btn.config(
            bg=self.btn_bg_color, command=self._select_medical_condition
            )
        self.changes.remove('New Medication Condition(s)')
        self.medical_conditions_changes = 'No'

    def _select_other_changes(self):
        """Select Other changes button."""
        self.changes_other_btn.config(
            bg=self.select_btn_bg_color, command=self._unselect_other_changes
            )
        self.changes.append('Other')

    def _unselect_other_changes(self):
        """Unselect Other changes button."""
        self.changes_other_btn.config(
            bg=self.btn_bg_color, command=self._select_other_changes
            )
        self.changes.remove('Other')

    def _select_injection_site_rxn(self):
        """Select Injection Site Reaction button."""
        self.injection_site_rxn_btn.config(
            bg=self.select_btn_bg_color, command=self._unselect_injection_site_rxn
            )
        self.symptoms_reported.append('Injection site reaction')

    def _unselect_injection_site_rxn(self):
        """Unselect Injection Site Reaction button."""
        self.injection_site_rxn_btn.config(
            bg=self.btn_bg_color, command=self._select_injection_site_rxn
            )
        self.symptoms_reported.remove('Injection site reaction')

    def _select_hospitalized_er(self):
        """Select Hospitalized/ER button."""
        self.hospitalize_er_btn.config(
            bg=self.select_btn_bg_color, command=self._unselect_hospitalized_er
            )
        self.symptoms_reported.append('Hospitalized/ER visit')

    def _unselect_hospitalized_er(self):
        """Unselect Hospitalized/ER button."""
        self.hospitalize_er_btn.config(
            bg=self.btn_bg_color, command=self._select_hospitalized_er
            )
        self.symptoms_reported.remove('Hospitalized/ER visit')

    def _select_other_side_effects(self):
        """Select Other side effects button."""
        self.side_effect_other_btn.config(
            bg=self.select_btn_bg_color, command=self._unselect_other_side_effects
            )
        self.symptoms_reported.append('Other')

    def _unselect_other_side_effects(self):
        """Unselect Other side effects button."""
        self.side_effect_other_btn.config(
            bg=self.btn_bg_color, command=self._select_other_side_effects
            )
        self.symptoms_reported.remove('Other')

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


if __name__ == '__main__':
    root = tk.Tk()
    rt = RefillTemplate()

    root.mainloop()
