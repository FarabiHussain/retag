from tkinter import BooleanVar, StringVar
from docx import Document
from path_manager import resource_path
from CTkTable import *
from CTkTableRowSelector import *
from CTkMessagebox import CTkMessagebox as popup
from dateutil import relativedelta as rd
import form_logic, customtkinter as ctk, datetime as dt, win32print, os, win32api, win32print, names, random, time, pandas as pd
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

form = {}
icon = {}
root = ctk.CTk()
root.resizable(False, False)
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen
status_string = StringVar(value="Ready")
printer_selected = StringVar(value=win32print.GetDefaultPrinter())
printer_list = []
version = "v0.9.0"
table_ranges = { 'start': 0, 'end': 15}
current_payment_index = 1
current_plus_month_posy = 101
history_window = None
history_entries = None
filtered_entries = None
history_table_frame = None
print_window = None
filters = {'only_inactive': False}


##
def handle_click_docx():
    global status_string
    status_string.set('writing docx')

    toPrinter = False
    toPdf = False
    isCodeOfConduct = False
    handle_generate(toPrinter, toPdf, isCodeOfConduct)


##
def handle_click_pdf():
    global status_string
    status_string.set('creating pdf')

    toPrinter = False
    toPdf = True
    isCodeOfConduct = False
    handle_generate(toPrinter, toPdf, isCodeOfConduct)


##
def handle_click_conduct():
    global status_string
    status_string.set('creating code of conduct')

    toPrinter = printer_selected.get()
    toPdf = False
    isCodeOfConduct = True
    handle_generate(toPrinter, toPdf, isCodeOfConduct)


##
def handle_click_print():
    global print_window, form

    if (print_window is None or not print_window.winfo_exists()): 
        print_window = ctk.CTkToplevel()

        w = 240
        h = 170
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)

        print_window.geometry('%dx%d+%d+%d' % (w, h, x, y))
        print_window.focus()
        print_window.after(201, lambda: print_window.iconbitmap("assets\\logo.ico"))
        print_window.title("Print")
        print_window.resizable(False, False)
        print_window.after(100, lambda: print_window.focus())

        form['frame_printer'] = ctk.CTkFrame(print_window, width=220, height=150)
        form['frame_printer'].place(x=10, y=10)

        form['select_device_label'] = ctk.CTkLabel(print_window, text="Select Device", bg_color='#212121', fg_color='#212121')
        form['select_device_label'].pack(padx=10, pady=[25,0])

        form['printer_dropdown'] = ctk.CTkComboBox(print_window, values=printer_list, border_width=0, corner_radius=4, fg_color='#313131', variable=printer_selected)
        form['printer_dropdown'].pack(padx=10, pady=[5,10])

        form['print_on_device_btn'] = ctk.CTkButton(print_window, text="Confirm", border_width=0, corner_radius=4, command=send_to_device, width=60, height=40)
        form['print_on_device_btn'].place(x=50, y=100)

        form['test_print_btn'] = ctk.CTkButton(print_window, text="", image=icon['test_prnt_icon'], border_width=1, corner_radius=4, fg_color='#1F1E1E', command=handle_click_test_print, width=60, height=40)
        form['test_print_btn'].place(x=130, y=100)

    else:
        print_window.focus()


##
def send_to_device():
    global status_string
    status_string.set('printing on device: ' + printer_selected.get())

    toPrinter = printer_selected.get()
    toPdf = False
    isCodeOfConduct = False

    handle_generate(toPrinter, toPdf, isCodeOfConduct)


##
def handle_click_output_folder():
    output_dir = (os.getcwd() + "\\output")
    os.startfile(output_dir)


##
def handle_click_history():
    pass


##
def handle_generate(toPrinter, toPdf, isCodeOfConduct):
    temp_list = []
    global form, status_string

    for i in range(len(form['payment_list'])):
        if len(form['payment_list'][i]['amount'].get()) > 0 and len(form['payment_list'][i]['date'].get()) > 0:
            temp_list.append({
                'amount': form['payment_list'][i]['amount'].get(),
                'date': form['payment_list'][i]['date'].get()
            })

    fill_info = {
        "document_date": form['document_date'].get(),
        "client_name": form['client_name'].get(),
        "application_type": form['application_type'].get(),
        "application_fee": form['application_fee'].get(),
        "email_address": form['email_address'].get(),
        "phone_number": form['phone_number'].get(),
        "payment_list": temp_list,
    }

    isTaxIncluded = form['include_taxes'].get()
    isOpenOutputActive = form['open_output_switch'].get()
    isRetainerActive = form['active_switch'].get()

    response = form_logic.generate(fill_info, isTaxIncluded, isOpenOutputActive, isRetainerActive, toPrinter, toPdf, isCodeOfConduct)

    if toPrinter == False:
        if response == False:
            status_string.set("Error")
        else:
            status_string.set("Agreement created")


##
def handle_click_reset():
    global form, status_string, current_payment_index, current_plus_month_posy, table_ranges
    status_string.set("form cleared")
    form = form_logic.reset(form)
    form['include_taxes'].set(True)
    form['open_output'].set(True)
    current_payment_index = 1
    current_plus_month_posy = 101
    table_ranges = { 'start': 0, 'end': 15}

    replace_plus_month_button(place_button=False)


##
def handle_click_today():
    global form
    form['document_date'].delete(0, "end")
    form['document_date'].insert(0, dt.datetime.now().strftime("%d/%m/%Y"))
    (form['payment_list'][0]['date']).delete(0, "end")
    (form['payment_list'][0]['date']).insert(0, dt.datetime.now().strftime("%d/%m/%Y"))

    if current_payment_index == 1:
        form['plus_month_btn'] = ctk.CTkButton(master=root, text="+1 month", border_width=0, corner_radius=4, bg_color='#343638', command=handle_click_plus_month, width=60, height=25)
        form['plus_month_btn'].place(x=568, y=101)


##
def handle_click_test_print():
    global form, status_string, printer_selected
    status_string.set("printing test")

    # defining the file path
    file_path = os.getcwd() + '\\assets\\test.docx'

    # delete any file called test.docx in case it already exists and has contents
    if os.path.exists(file_path):
        os.remove(file_path)

    # create a new document with nothing in it
    document = Document()
    document.save(file_path)

    # print the blank document
    win32print.SetDefaultPrinter(printer_selected.get())
    win32api.ShellExecute(0, "print", file_path, None,  ".",  0)

    # add a delay so that the print command has time to find the file, then remove the document
    time.sleep(2)
    if os.path.exists(file_path):
        os.remove(file_path)


##
def handle_click_test_data():
    global form, status_string
    status_string.set("dummy data placed")

    client_name = names.get_full_name()
    application_fee = (random.randint(1,4) * 1000)

    form['document_date'].delete(0, 'end')
    form['client_name'].delete(0, 'end')
    form['application_type'].delete(0, 'end')
    form['application_fee'].delete(0, 'end')
    form['email_address'].delete(0, 'end')
    form['phone_number'].delete(0, 'end')
    form['document_date'].insert(0, '1/3/2024')
    form['client_name'].insert(0, client_name)
    form['application_type'].insert(0, random.choice(['EOI','MPNP','PR','PGWP','Citizenship']))
    form['application_fee'].insert(0, application_fee)
    form['email_address'].insert(0, client_name.replace(" ", "").lower() + '@email.com')
    form['phone_number'].insert(0, random.choice(['431','204']) + str(random.randint(1000000, 9999999)))

    installments = random.randint(1,12)
    per_installment = float(application_fee/installments)

    for i in range(12):
        form['payment_list'][i]['date'].delete(0, 'end')
        form['payment_list'][i]['amount'].delete(0, 'end')
    
    for i in range(installments):
        m = str((3 + i) % 12 + 1)
        y = str(int((4 + i) / 12) + 2024)

        form['payment_list'][i]['date'].insert(0, ('1/' + m + "/" + y))
        form['payment_list'][i]['amount'].insert(0, "{:.2f}".format((per_installment)))


##
def handle_click_500dollars():
    global form
    form['application_fee'].delete(0, "end")
    form['application_fee'].insert(0, 500)


##
def handle_click_1000dollars():
    global form
    form['application_fee'].delete(0, "end")
    form['application_fee'].insert(0, 1000)


##
def handle_click_advance():
    global form
    form['payment_list'][0]['date'].delete(0, 'end')
    form['payment_list'][0]['date'].insert(0, 'advance')

    if current_payment_index == 1:
        replace_plus_month_button()


##
def replace_plus_month_button(place_button = True):
    global form, current_plus_month_posy

    form['plus_month_btn'].destroy()
    form['plus_month_btn'] = ctk.CTkButton(master=root, text="+1 month", border_width=0, corner_radius=4, bg_color='#343638', command=handle_click_plus_month, width=60, height=25)
    
    if place_button:
        form['plus_month_btn'].place(x=568, y=current_plus_month_posy)


##
def handle_click_plus_month():
    global form, current_payment_index, current_plus_month_posy
    pixels_to_next_row = 34

    if (current_payment_index < 12 and len(form['payment_list'][current_payment_index - 1]['date'].get()) != 0): 

        prev_payment_date = form['payment_list'][current_payment_index - 1]['date'].get()
        
        if (prev_payment_date == "advance"):
            prev_payment_date = dt.datetime.now().strftime('%d/%m/%Y')

        dt_object = dt.datetime.strptime(prev_payment_date, '%d/%m/%Y')
        dt_object = dt_object + rd.relativedelta(months=1)

        form['payment_list'][current_payment_index]['date'].delete(0, 'end')
        form['payment_list'][current_payment_index]['date'].insert(0, dt_object.strftime('%d/%m/%Y'))

        current_payment_index += 1

        if current_payment_index < 12:
            current_plus_month_posy += pixels_to_next_row
            form['plus_month_btn'].place(x=568, y=current_plus_month_posy)
        else:
            form['plus_month_btn'].destroy()

    elif len(form['payment_list'][0]['date'].get()) == 0:
        popup(title="Failed", message="Unable to add month as previous payment date is empty", corner_radius=4)

    elif len(form['payment_list'][current_payment_index - 1]['date'].get()) < 8:
        current_payment_index -= 1
        current_plus_month_posy -= pixels_to_next_row
        replace_plus_month_button()
        handle_click_plus_month()


##
def autofill_first_amount(var, index, mode):
    global form
    amount_input = form['autofill_amount'].get()
    (form['payment_list'][0]['amount']).delete(0, 'end')
    (form['payment_list'][0]['amount']).insert(0, amount_input)


##
def autofill_first_date(var, index, mode):
    global form

    doc_date = form['document_date'].get()

    for i in range(len(doc_date)):
        if (doc_date[i].isdigit() or doc_date[i] == '/'):
            (form['payment_list'][0]['date']).delete(0, 'end')
            (form['payment_list'][0]['date']).insert(0, doc_date)
        else:
            form['document_date'].delete(0, 'end')
            form['document_date'].insert(0, doc_date[0:-1])
            (form['payment_list'][0]['date']).delete(0, 'end')
            (form['payment_list'][0]['date']).insert(0, doc_date[0:-1])

    if (len(doc_date) == 0):
        (form['payment_list'][0]['date']).delete(0, 'end')


##
def render_form():
    global form

    x_offset = 10
    y_offset = 0

    form['frame_info'].place(x=20, y=40)
    form['client_info_label'].place(x=120, y=10)

    labels = ['document_date_label', 'client_name_label', 'application_type_label', 'application_fee_label', 'email_address_label', 'phone_number_label']
    entries = ['document_date', 'client_name', 'application_type', 'application_fee', 'email_address', 'phone_number']

    for i in range(len(labels)):
        form[labels[i]].place(x=x_offset, y=y_offset + 10)
        form[entries[i]].place(x=x_offset, y=y_offset + 40)
        y_offset += 70

    form['frame_payments'].place(x=340, y=40)
    form['payment_instructions_label'].place(x=430, y=10)
    form['amount_label'].place(x=40, y=0)
    form['date_label'].place(x=140, y=0)

    y_offset = 15
    for i in range(len(form['payment_list'])):
        curr_payment = form['payment_list'][i]
        curr_payment['serial'] = ctk.CTkLabel(form['frame_payments'], text=(str(i + 1) + "."))

        curr_payment['serial'].place(x=x_offset + 5, y=y_offset + 11)
        curr_payment['amount'].place(x=x_offset + 30, y=y_offset + 10)
        curr_payment['date'].place(x=x_offset + 130, y=y_offset + 10)
        y_offset += 34


    form['today_btn'].place(x=250, y=50)
    form['500_btn'].place(x=180, y=260)
    form['1000_btn'].place(x=250, y=260)
    form['advance_btn'].place(x=568, y=67)

    y_offset = 40
    form['tax_switch'].place(x=660, y=y_offset)
    y_offset += 40
    form['open_output_switch'].place(x=660, y=y_offset)
    y_offset += 40
    form['active_switch'].place(x=660, y=y_offset)
    y_offset += 40

    # buffer
    buffer = 358

    y_offset += (buffer - y_offset)
    form['test_data_btn'].place(x=660, y=y_offset)
    y_offset += 42
    form['history_btn'].place(x=660, y=y_offset)
    form['output_btn'].place(x=702, y=y_offset)
    form['clear_btn'].place(x=744, y=y_offset)
    y_offset += 42
    form['print_btn'].place(x=660, y=y_offset)
    form['docx_btn'].place(x=702, y=y_offset)
    form['pdf_btn'].place(x=744, y=y_offset)
    y_offset += 42
    form['conduct_btn'].place(x=660, y=y_offset)

    # frame
    form['frame_status'].place(x=20, y=490)
    form['status_label'].place(x=10, y=1)


##
def init_form():
    global root, printer_list, form, icon

    printer_list = [printer[2] for printer in win32print.EnumPrinters(2) if 'PDF' not in printer[2]]

    # calculate x and y coordinates for the Tk root window
    w = 800
    h = 540
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)

    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    root.iconbitmap(resource_path("assets\\logo.ico"))
    root.title("AMCAIM RetAG " + version)

    form['autofill_amount'] = StringVar()
    form['autofill_amount'].trace_add('write', autofill_first_amount)
    form['autofill_date'] = StringVar()
    form['autofill_date'].trace_add('write', autofill_first_date)
    form['include_taxes'] = BooleanVar(value=True)
    form['open_output'] = BooleanVar(value=True)
    form['is_active'] = BooleanVar(value=False)

    ## left frame
    form['frame_info'] = ctk.CTkFrame(master=root, width=300, height=440)
    current_frame = form['frame_info']

    form['client_info_label'] = ctk.CTkLabel(root, text="Client Information")
    form['document_date_label'] = ctk.CTkLabel(current_frame, text="Date on document (DD/MM/YYYY)")
    form['client_name_label'] = ctk.CTkLabel(current_frame, text="Client name")
    form['application_type_label'] = ctk.CTkLabel(current_frame, text="Application type")
    form['application_fee_label'] = ctk.CTkLabel(current_frame, text="Application fee")
    form['email_address_label'] = ctk.CTkLabel(current_frame, text="Email address")
    form['phone_number_label'] = ctk.CTkLabel(current_frame, text="Phone number")

    form['document_date'] = ctk.CTkEntry(current_frame, width=280, border_width=0, corner_radius=4, placeholder_text='DD/MM/YYYY', textvariable=form['autofill_date'])
    form['client_name'] = ctk.CTkEntry(current_frame, width=280, border_width=0, corner_radius=4)
    form['application_type'] = ctk.CTkEntry(current_frame, width=280, border_width=0, corner_radius=4)
    form['application_fee'] = ctk.CTkEntry(current_frame, width=280, border_width=0, corner_radius=4, textvariable=form['autofill_amount'])
    form['email_address'] = ctk.CTkEntry(current_frame, width=280, border_width=0, corner_radius=4)
    form['phone_number'] = ctk.CTkEntry(current_frame, width=280, border_width=0, corner_radius=4)

    ## right frame
    form['frame_payments'] = ctk.CTkFrame(master=root, width=300, height=440)
    current_frame = form['frame_payments']

    form['payment_instructions_label'] = ctk.CTkLabel(root, text="Payment Instructions")
    form['amount_label'] = ctk.CTkLabel(current_frame, text="Amount")
    form['date_label'] = ctk.CTkLabel(current_frame, text="Date (DD/MM/YYYY)")

    form['payment_list'] = []
    for _ in range(12):
        form['payment_list'].append({
            'amount': ctk.CTkEntry(current_frame, width=90, border_width=0, corner_radius=4),
            'date': ctk.CTkEntry(current_frame, width=150, border_width=0, corner_radius=4)
        })

    ## button images
    icon['history_icon'] = tk.PhotoImage(file=resource_path("assets\\icons\\history.png"))
    icon['folder_icon'] = tk.PhotoImage(file=resource_path("assets\\icons\\folder.png"))
    icon['clear_icon'] = tk.PhotoImage(file=resource_path("assets\\icons\\clear.png"))
    icon['pdf_icon'] = tk.PhotoImage(file=resource_path("assets\\icons\\pdf.png"))
    icon['docx_icon'] = tk.PhotoImage(file=resource_path("assets\\icons\\docx.png"))
    icon['prnt_icon'] = tk.PhotoImage(file=resource_path("assets\\icons\\print.png"))
    icon['conduct_icon'] = tk.PhotoImage(file=resource_path("assets\\icons\\conduct.png"))
    icon['test_data_icon'] = tk.PhotoImage(file=resource_path("assets\\icons\\testData.png"))
    icon['test_prnt_icon'] = tk.PhotoImage(file=resource_path("assets\\icons\\testPrnt.png"))

    ## buttons
    button_size = 36

    form['today_btn'] = ctk.CTkButton(master=root, text="today", border_width=0, corner_radius=4, bg_color='#212121', command=handle_click_today, width=60, height=25)
    form['500_btn'] = ctk.CTkButton(master=root, text="$500", border_width=0, corner_radius=4, bg_color='#212121', command=handle_click_500dollars, width=60, height=25)
    form['1000_btn'] = ctk.CTkButton(master=root, text="$1000", border_width=0, corner_radius=4, bg_color='#212121', command=handle_click_1000dollars, width=60, height=25)
    form['advance_btn'] = ctk.CTkButton(master=root, text="advance", border_width=0, corner_radius=4, bg_color='#343638', command=handle_click_advance, width=60, height=25)
    form['plus_month_btn'] = ctk.CTkButton(master=root, text="+1 month", border_width=0, corner_radius=4, bg_color='#343638', command=handle_click_plus_month, width=60, height=25)

    form['test_data_btn'] = ctk.CTkButton(master=root, text="", image=icon['test_data_icon'], border_width=1, corner_radius=4, fg_color='#1F1E1E', command=handle_click_test_data, width=120, height=button_size)

    form['history_btn'] = ctk.CTkButton(master=root, text="", image=icon['history_icon'], border_width=0, corner_radius=4, fg_color='#313131', command=handle_click_history, width=button_size, height=button_size)
    form['output_btn'] = ctk.CTkButton(master=root, text="", image=icon['folder_icon'], border_width=0, corner_radius=4, fg_color='#313131', command=handle_click_output_folder, width=button_size, height=button_size)
    form['clear_btn'] = ctk.CTkButton(master=root, text="", image=icon['clear_icon'], border_width=0, corner_radius=4, fg_color='#313131', command=handle_click_reset, width=button_size, height=button_size)
    form['print_btn'] = ctk.CTkButton(master=root, text="", image=icon['prnt_icon'], border_width=0, corner_radius=4, fg_color="#e07b00", text_color="black", command=handle_click_print, width=button_size, height=button_size)
    form['docx_btn'] = ctk.CTkButton(master=root, text="", image=icon['docx_icon'], border_width=0, corner_radius=4, fg_color="#383FBC", command=handle_click_docx, width=button_size, height=button_size)
    form['pdf_btn'] = ctk.CTkButton(master=root, text="", image=icon['pdf_icon'], border_width=0, corner_radius=4, fg_color="#b02525", command=handle_click_pdf, width=button_size, height=button_size)
    form['conduct_btn'] = ctk.CTkButton(master=root, text="", image=icon['conduct_icon'], border_width=0, corner_radius=4, fg_color="#1A8405", command=handle_click_conduct, width=120, height=button_size)

    ## switches
    form['tax_switch'] = ctk.CTkSwitch(master=root, text="Add Taxes", border_width=0, corner_radius=4, onvalue=True, offvalue=False, variable=form['include_taxes'])
    form['open_output_switch'] = ctk.CTkSwitch(master=root, text="Open Output", border_width=0, corner_radius=4, onvalue=True, offvalue=False, variable=form['open_output'])
    form['active_switch'] = ctk.CTkSwitch(master=root, text="Set Active", border_width=0, corner_radius=4, onvalue=True, offvalue=False, variable=form['is_active'])

    form['frame_status'] = ctk.CTkFrame(master=root, width=620, height=30)
    current_frame = form['frame_status']

    form['status_label'] = ctk.CTkLabel(current_frame, textvariable=status_string)

    render_form()

    root.mainloop()
