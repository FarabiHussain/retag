import editor, re
from CTkMessagebox import CTkMessagebox as popup


## validates the form
def validate(fill_info):
    for key, val in fill_info.items():

        if (len(fill_info[key]) < 1):
            popup(icon="cancel", title="Error", message="All fields need to be filled", corner_radius=4)
            print("All fields need to be filled")
            return False

        if (key == "email_address") and ("@" not in fill_info[key]) and ("." not in fill_info[key]):
            popup(icon="cancel", title="Error", message="Invalid email address", corner_radius=4)
            print("Invalid email address")
            return False
        
        if (key == "payment_list"):
            for index in range(len(fill_info['payment_list'])):
                current_pay = fill_info['payment_list'][index]

                if (len(current_pay['amount']) == 0 and len(current_pay['date']) == 0):
                    popup(icon="cancel", title="Error", message="Payment " + str(index + 1) + " contains empty field(s)", corner_radius=4)
                    return False

                if (re.match('^[0-9]*$', current_pay['amount']) == False):
                    popup(icon="cancel", title="Error", message="Invalid amount in payment #" + str(index + 1), corner_radius=4)
                    return False

                if (re.match('^[0-3]{0,1}[0-9]{1}' + '/' + '[0-2]{0,1}[0-9]{1}' + '/' + '20[0-9]{1}[0-9]{1}$', current_pay['date']) == None):
                    popup(icon="cancel", title="Error", message="Invalid date in payment #" + str(index + 1), corner_radius=4)
                    return False

    return True


## runs the editor and displays message
def generate(fill_info, include_taxes, toPrinter, toPdf):
    if (validate(fill_info) == True):
        return editor.process(fill_info, include_taxes, toPrinter, toPdf)

    return False


## reset form fields
def reset(form_elements):
    form_elements['client_name'].delete(0, "end")
    form_elements['application_type'].delete(0, "end")
    form_elements['application_fee'].delete(0, "end")
    form_elements['email_address'].delete(0, "end")
    form_elements['phone_number'].delete(0, "end")
    form_elements['document_date'].delete(0, "end")

    for i in range(len(form_elements['payment_list'])):
        form_elements['payment_list'][i]['amount'].delete(0, "end")
        form_elements['payment_list'][i]['amount'].insert("end", "")
        form_elements['payment_list'][i]['date'].delete(0, "end")
        form_elements['payment_list'][i]['date'].insert("end", "")

    return form_elements
