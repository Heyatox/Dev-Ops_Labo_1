import os
import datetime
import shutil
import sys

from my_sqlite3 import *

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True


def init(top, gui, *args, **kwargs):
    global w, top_level, root
    w = gui
    top_level = top
    root = top


def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global w, root
    root = tk.Tk()
    top = fenetre_principale(root)
    init(root, top)
    root.mainloop()


def nouvel_employe_start_gui():
    '''Starting point when module is the main routine.'''
    global w, root
    root = tk.Tk()
    top = popup_nouvel_employe(root)
    init(root, top)
    root.mainloop()


def modifier_employe_start_gui():
    '''Starting point when module is the main routine.'''
    global w, root
    root = tk.Tk()
    top = popup_modifier_employe(root)
    init(root, top)
    root.mainloop()


def nouveau_menu_start_gui():
    '''Starting point when module is the main routine.'''
    global w, root
    root = tk.Tk()
    top = popup_ajouter_menu(root)
    init(root, top)
    root.mainloop()


def modifier_menu_start_gui():
    '''Starting point when module is the main routine.'''
    global w, root
    root = tk.Tk()
    top = popup_modifier_menu(root)
    init(root, top)
    root.mainloop()


w = None

##########################
#### Global variables ####
##########################

db_name = 'meals.db'
db_path = db_name  # will be different if "db" is not in the same directory

###################
#### Functions ####
###################


def purchase():
    purchase_id = get_purchase_id()
    current_date = datetime.datetime.now()
    formated_date = current_date.strftime("%d-%m-%Y %H:%M:%S")
    employee_id = get_employee_id()
    employee_name = get_employee_name(employee_id)
    ticket_data = [purchase_id, formated_date, employee_name]
    db_link = connect_to_db(db_path)
    db_cursor = create_cursor(db_link)
    sql_query = "INSERT INTO purchase(date,employee_id) VALUES (?,?)"
    sql_values = (formated_date, employee_id)
    write_to_cursor(db_cursor, sql_query, sql_values)
    menu_id_list = get_id_list('menu')

    while True:
        menu_id = input("\nEnter menu ID : ")

        if not menu_id:  # TODO if menu_id in menu_id_list:
            break

        os.system('clear')
        menu_id = int(menu_id)

        if menu_id in menu_id_list:
            # TODO get_purchase_detail plutôt que get_menu_price?
            menu_price = get_menu_price(menu_id)
            sql_query = "INSERT INTO purchase_detail(purchase_id,menu_id,menu_price) VALUES (?,?,?)"
            sql_values = (purchase_id, menu_id, menu_price)
            write_to_cursor(db_cursor, sql_query, sql_values)
            ticket_data.append(sql_values)

        display_ticket(ticket_data)
    confirm = input("Confirm your order (y/n) : ")

    if ((confirm == 'y') and (len(ticket_data) >= 4)):
        commit_to_db(db_link)
        disconnect_from_db(db_link)
        save_database(db_path)


def get_purchase_id():
    db_link = connect_to_db(db_path)
    db_cursor = create_cursor(db_link)
    sql_query = "SELECT MAX(id) FROM purchase"
    query_result = read_from_cursor(db_cursor, sql_query)
    disconnect_from_db(db_link)

    if query_result[0][0] is not None:
        last_purchase_id = query_result[0][0]

    else:
        last_purchase_id = 0

    purchase_id = last_purchase_id + 1
    return purchase_id


def get_employee_id():  # TODO idem que get_menu_id()?
    employee_id_list = get_id_list('employee')
    # print(employee_id_list) #[1, 2, 3, 4]
    employee_id = 0

    while employee_id not in employee_id_list:
        os.system('clear')
        employee_id = input("Enter the employee ID : ")

        if not employee_id:
            employee_id = 0

        else:
            employee_id = int(employee_id)

    return employee_id


def get_id_list(table_name):
    db_link = connect_to_db(db_path)
    db_cursor = create_cursor(db_link)

    if (table_name == 'employee'):  # TODO simlify with ?
        sql_query = "SELECT id FROM employee"

    elif (table_name == 'menu'):
        sql_query = "SELECT id FROM menu"

    query_result = read_from_cursor(db_cursor, sql_query)
    id_list = []

    for id in query_result:
        id_list.append(id[0])

    disconnect_from_db(db_link)
    return id_list


def get_employee_name(employee_id):
    db_link = connect_to_db(db_path)
    db_cursor = create_cursor(db_link)
    sql_query = "SELECT first_name,family_name FROM employee WHERE id=?"
    sql_values = (employee_id,)
    query_result = read_from_cursor(db_cursor, sql_query, sql_values)
    employee_name = query_result[0][0] + ' ' + query_result[0][1]
    disconnect_from_db(db_link)
    return employee_name


def get_menu_price(menu_id):
    db_link = connect_to_db(db_path)
    db_cursor = create_cursor(db_link)
    sql_query = "SELECT price FROM menu WHERE id=?"
    sql_values = (menu_id,)
    query_result = read_from_cursor(db_cursor, sql_query, sql_values)
    menu_price = query_result[0][0]
    disconnect_from_db(db_link)
    return menu_price


def display_ticket(ticket_data):
    purchase_line = 'Purchase number : ' + str(ticket_data[0])
    date_line = 'Date : ' + ticket_data[1]
    employee_line = 'Employee : ' + ticket_data[2] + '\n'
    print(purchase_line)
    print(date_line)
    print(employee_line)
    amount = 0.0

    for index in range(3, len(ticket_data)
                       ):  # [purchase_id,date,employee,(p_id,menu_id,price)]
        menu_id = ticket_data[index][1]
        description = get_menu_description(menu_id)
        price = ticket_data[index][2]
        detail_string = "Menu: {:<18} {:>6} €"
        detail_line = detail_string.format(description, price)
        print(detail_line)
        amount = amount + price  # TODO pourquoi 3.3 * 3 donne 9.89999999?

    amount_line = '\nAmount : ' + str(amount) + ' €'
    print(amount_line)


def get_menu_description(menu_id):
    db_link = connect_to_db(db_path)
    db_cursor = create_cursor(db_link)
    sql_query = "SELECT description FROM menu WHERE id=?"
    sql_values = (menu_id,)
    query_result = read_from_cursor(db_cursor, sql_query, sql_values)
    description = query_result[0][0]
    disconnect_from_db(db_link)
    return description


def save_database(db_name):
    backup_dir = 'backup'

    if not os.path.isdir(backup_dir):
        os.makedirs(backup_dir)

    date = datetime.datetime.now()
    hour = date.strftime("%H")
    source = db_name
    backup = backup_dir + '/' + db_name + '_' + hour
    shutil.copyfile(source, backup)


def add_employee(prenom, nom, email):
    first_name = prenom
    family_name = nom
    email_address = email
    db_link = connect_to_db(db_path)
    db_cursor = create_cursor(db_link)
    sql_query = "INSERT INTO employee(first_name,family_name,email_address) VALUES (?,?,?)"
    print(first_name, family_name, email_address)
    sql_values = (first_name, family_name, email_address)
    write_to_cursor(db_cursor, sql_query, sql_values)
    commit_to_db(db_link)
    disconnect_from_db(db_link)


def modify_employee(id_user, prenom, nom, email):
    employee_id = int(id_user)
    db_link = connect_to_db(db_path)
    db_cursor = create_cursor(db_link)
    sql_query = "SELECT first_name,family_name,email_address FROM employee WHERE id=?"
    sql_values = (employee_id,)
    query_result = read_from_cursor(
        db_cursor,
        sql_query,
        sql_values)  # [('Jack', 'DAVIS', None)]
    first_name = query_result[0][0]
    family_name = query_result[0][1]
    email_address = query_result[0][2]
    db_cursor.close()
    db_cursor = create_cursor(db_link)
    new_first_name = prenom

    if new_first_name:
        sql_query = "UPDATE employee SET first_name = ? WHERE id=?"
        sql_values = (new_first_name, employee_id)
        write_to_cursor(db_cursor, sql_query, sql_values)

    new_family_name = nom

    if new_family_name:
        sql_query = "UPDATE employee SET family_name = ? WHERE id=?"
        sql_values = (new_family_name, employee_id)
        write_to_cursor(db_cursor, sql_query, sql_values)

    new_email_address = email

    if new_email_address:
        sql_query = "UPDATE employee SET email_address = ? WHERE id=?"
        sql_values = (new_email_address, employee_id)
        write_to_cursor(db_cursor, sql_query, sql_values)

    commit_to_db(db_link)
    disconnect_from_db(db_link)


def add_menu(description_menu, prix_menu):
    description = description_menu
    price = prix_menu
    db_link = connect_to_db(db_path)
    db_cursor = create_cursor(db_link)
    sql_query = "INSERT INTO menu(description,price) VALUES (?,?)"
    sql_values = (description, price)
    write_to_cursor(db_cursor, sql_query, sql_values)
    commit_to_db(db_link)
    disconnect_from_db(db_link)


def modify_menu(id_menu, description_menu, nouveau_prix):
    menu_id = id_menu
    db_link = connect_to_db(db_path)
    db_cursor = create_cursor(db_link)
    sql_query = "SELECT description,price FROM menu WHERE id=?"
    sql_values = (menu_id,)
    query_result = read_from_cursor(db_cursor, sql_query, sql_values)
    description = query_result[0][0]
    price = query_result[0][1]
    db_cursor.close()
    db_cursor = create_cursor(db_link)
    new_description = description_menu

    if new_description:
        sql_query = "UPDATE menu SET description = ? WHERE id=?"
        sql_values = (new_description, menu_id)
        write_to_cursor(db_cursor, sql_query, sql_values)

    new_price = nouveau_prix

    if new_price:
        sql_query = "UPDATE menu SET price = ? WHERE id=?"
        sql_values = (new_price, menu_id)
        write_to_cursor(db_cursor, sql_query, sql_values)

    commit_to_db(db_link)
    disconnect_from_db(db_link)


def exit_program():
    sys.exit()

##########################
### FENÊTRE PRINCIPALE ###
##########################


def create_fenetre_principale(rt, *args, **kwargs):
    '''Starting point when module is imported by another module.
       Correct form of call: 'create_fenetre_principale(root, *args, **kwargs)' .'''
    global w, w_win, root
    #rt = root
    root = rt
    w = tk.Toplevel(root)
    top = fenetre_principale(w)
    init(w, top, *args, **kwargs)
    return (w, top)


class fenetre_principale:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'

        top.geometry("1024x768+369+133")
        top.minsize(120, 1)
        top.maxsize(1924, 2141)
        top.resizable(0, 0)
        top.title("Caisse enregistreuse")
        top.configure(background="#d9d9d9")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")

        self.affichage_ticket = tk.Listbox(top)
        self.affichage_ticket.place(
            relx=0.039,
            rely=0.052,
            relheight=0.876,
            relwidth=0.632)
        self.affichage_ticket.configure(background="#ffffff")
        self.affichage_ticket.configure(disabledforeground="#a3a3a3")
        self.affichage_ticket.configure(font="TkFixedFont 20")
        self.affichage_ticket.configure(foreground="#000000")

        self.affichage_ticket.configure(relief="ridge")

        # TODO affichage en dur à modifier
        '''
        self.affichage_ticket.insert("end","Achat numéro: 7")
        self.affichage_ticket.insert("end","Date: 01/12/2020")
        self.affichage_ticket.insert("end","Employé: Olivia JONES")
        self.affichage_ticket.insert("end","")
        self.affichage_ticket.insert("end","")
        self.affichage_ticket.insert("end","Menu: Sandwitch")
        self.affichage_ticket.insert("end","Menu: Salad")
        self.affichage_ticket.insert("end","Menu: Chicken")
        self.affichage_ticket.insert("end","Menu: Steak")
        self.affichage_ticket.insert("end","Menu: Canard")
        self.affichage_ticket.insert("end","Menu: Lait")
        self.affichage_ticket.insert("end","")
        self.affichage_ticket.insert("end","")
        self.affichage_ticket.insert("end","TOTAL: 33.75€")
        self.affichage_ticket.configure(130,200,fill="darkblue",font="Times 25",
            text="Menu: Chicken")
        self.affichage_ticket.configure(130,240,fill="darkblue",font="Times 25",
            text="Menu: Steak")
        self.affichage_ticket.configure(130,270,fill="darkblue",font="Times 25",
            text="Menu: Canard")
        self.affichage_ticket.configure(130,300,fill="darkblue",font="Times 25",
            text="Menu: Lait")
        '''

        self.nouvel_employe = tk.Button(top)
        self.nouvel_employe.place(relx=0.703, rely=0.065, height=74, width=117)
        self.nouvel_employe.configure(activebackground="#ececec")
        self.nouvel_employe.configure(activeforeground="#000000")
        self.nouvel_employe.configure(background="#d9d9d9")
        self.nouvel_employe.configure(disabledforeground="#a3a3a3")
        self.nouvel_employe.configure(foreground="#000000")
        self.nouvel_employe.configure(highlightbackground="#d9d9d9")
        self.nouvel_employe.configure(highlightcolor="black")
        self.nouvel_employe.configure(pady="0")
        self.nouvel_employe.configure(
            text='''Nouvel employé''',
            command=nouvel_employe_start_gui)

        self.modifier_employe = tk.Button(top)
        self.modifier_employe.place(
            relx=0.85, rely=0.065, height=74, width=117)
        self.modifier_employe.configure(activebackground="#ececec")
        self.modifier_employe.configure(activeforeground="#000000")
        self.modifier_employe.configure(background="#d9d9d9")
        self.modifier_employe.configure(disabledforeground="#a3a3a3")
        self.modifier_employe.configure(foreground="#000000")
        self.modifier_employe.configure(highlightbackground="#d9d9d9")
        self.modifier_employe.configure(highlightcolor="black")
        self.modifier_employe.configure(pady="0")
        self.modifier_employe.configure(
            text='''Modifier employé''',
            command=modifier_employe_start_gui)

        self.nouveau_menu = tk.Button(top)
        self.nouveau_menu.place(relx=0.703, rely=0.195, height=74, width=117)
        self.nouveau_menu.configure(activebackground="#ececec")
        self.nouveau_menu.configure(activeforeground="#000000")
        self.nouveau_menu.configure(background="#d9d9d9")
        self.nouveau_menu.configure(disabledforeground="#a3a3a3")
        self.nouveau_menu.configure(foreground="#000000")
        self.nouveau_menu.configure(highlightbackground="#d9d9d9")
        self.nouveau_menu.configure(highlightcolor="black")
        self.nouveau_menu.configure(pady="0")
        self.nouveau_menu.configure(
            text='''Nouveau menu''',
            command=nouveau_menu_start_gui)

        self.modifier_menu = tk.Button(top)
        self.modifier_menu.place(relx=0.85, rely=0.195, height=74, width=117)
        self.modifier_menu.configure(activebackground="#ececec")
        self.modifier_menu.configure(activeforeground="#000000")
        self.modifier_menu.configure(background="#d9d9d9")
        self.modifier_menu.configure(disabledforeground="#a3a3a3")
        self.modifier_menu.configure(foreground="#000000")
        self.modifier_menu.configure(highlightbackground="#d9d9d9")
        self.modifier_menu.configure(highlightcolor="black")
        self.modifier_menu.configure(pady="0")
        self.modifier_menu.configure(
            text='''Modifier menu''',
            command=modifier_menu_start_gui)

        self.sept = tk.Button(top)
        self.sept.place(relx=0.703, rely=0.326, height=54, width=67)
        self.sept.configure(activebackground="#ececec")
        self.sept.configure(activeforeground="#000000")
        self.sept.configure(background="#d9d9d9")
        self.sept.configure(disabledforeground="#a3a3a3")
        self.sept.configure(foreground="#000000")
        self.sept.configure(highlightbackground="#d9d9d9")
        self.sept.configure(highlightcolor="black")
        self.sept.configure(pady="0")
        self.sept.configure(text='''7''')

        self.huit = tk.Button(top)
        self.huit.place(relx=0.801, rely=0.326, height=54, width=67)
        self.huit.configure(activebackground="#ececec")
        self.huit.configure(activeforeground="#000000")
        self.huit.configure(background="#d9d9d9")
        self.huit.configure(disabledforeground="#a3a3a3")
        self.huit.configure(foreground="#000000")
        self.huit.configure(highlightbackground="#d9d9d9")
        self.huit.configure(highlightcolor="black")
        self.huit.configure(pady="0")
        self.huit.configure(text='''8''')

        self.neuf = tk.Button(top)
        self.neuf.place(relx=0.898, rely=0.326, height=54, width=67)
        self.neuf.configure(activebackground="#ececec")
        self.neuf.configure(activeforeground="#000000")
        self.neuf.configure(background="#d9d9d9")
        self.neuf.configure(disabledforeground="#a3a3a3")
        self.neuf.configure(foreground="#000000")
        self.neuf.configure(highlightbackground="#d9d9d9")
        self.neuf.configure(highlightcolor="black")
        self.neuf.configure(pady="0")
        self.neuf.configure(text='''9''')

        self.quatre = tk.Button(top)
        self.quatre.place(relx=0.703, rely=0.43, height=54, width=67)
        self.quatre.configure(activebackground="#ececec")
        self.quatre.configure(activeforeground="#000000")
        self.quatre.configure(background="#d9d9d9")
        self.quatre.configure(disabledforeground="#a3a3a3")
        self.quatre.configure(foreground="#000000")
        self.quatre.configure(highlightbackground="#d9d9d9")
        self.quatre.configure(highlightcolor="black")
        self.quatre.configure(pady="0")
        self.quatre.configure(text='''4''')

        self.cinq = tk.Button(top)
        self.cinq.place(relx=0.801, rely=0.43, height=54, width=67)
        self.cinq.configure(activebackground="#ececec")
        self.cinq.configure(activeforeground="#000000")
        self.cinq.configure(background="#d9d9d9")
        self.cinq.configure(disabledforeground="#a3a3a3")
        self.cinq.configure(foreground="#000000")
        self.cinq.configure(highlightbackground="#d9d9d9")
        self.cinq.configure(highlightcolor="black")
        self.cinq.configure(pady="0")
        self.cinq.configure(text='''5''')

        self.six = tk.Button(top)
        self.six.place(relx=0.898, rely=0.43, height=54, width=67)
        self.six.configure(activebackground="#ececec")
        self.six.configure(activeforeground="#000000")
        self.six.configure(background="#d9d9d9")
        self.six.configure(disabledforeground="#a3a3a3")
        self.six.configure(foreground="#000000")
        self.six.configure(highlightbackground="#d9d9d9")
        self.six.configure(highlightcolor="black")
        self.six.configure(pady="0")
        self.six.configure(text='''6''')

        self.un = tk.Button(top)
        self.un.place(relx=0.703, rely=0.534, height=54, width=67)
        self.un.configure(activebackground="#ececec")
        self.un.configure(activeforeground="#000000")
        self.un.configure(background="#d9d9d9")
        self.un.configure(disabledforeground="#a3a3a3")
        self.un.configure(foreground="#000000")
        self.un.configure(highlightbackground="#d9d9d9")
        self.un.configure(highlightcolor="black")
        self.un.configure(pady="0")
        self.un.configure(text='''1''')

        self.deux = tk.Button(top)
        self.deux.place(relx=0.801, rely=0.534, height=54, width=67)
        self.deux.configure(activebackground="#ececec")
        self.deux.configure(activeforeground="#000000")
        self.deux.configure(background="#d9d9d9")
        self.deux.configure(disabledforeground="#a3a3a3")
        self.deux.configure(foreground="#000000")
        self.deux.configure(highlightbackground="#d9d9d9")
        self.deux.configure(highlightcolor="black")
        self.deux.configure(pady="0")
        self.deux.configure(text='''2''')

        self.trois = tk.Button(top)
        self.trois.place(relx=0.898, rely=0.534, height=54, width=67)
        self.trois.configure(activebackground="#ececec")
        self.trois.configure(activeforeground="#000000")
        self.trois.configure(background="#d9d9d9")
        self.trois.configure(disabledforeground="#a3a3a3")
        self.trois.configure(foreground="#000000")
        self.trois.configure(highlightbackground="#d9d9d9")
        self.trois.configure(highlightcolor="black")
        self.trois.configure(pady="0")
        self.trois.configure(text='''3''')

        self.zero = tk.Button(top)
        self.zero.place(relx=0.703, rely=0.638, height=54, width=167)
        self.zero.configure(activebackground="#ececec")
        self.zero.configure(activeforeground="#000000")
        self.zero.configure(background="#d9d9d9")
        self.zero.configure(disabledforeground="#a3a3a3")
        self.zero.configure(foreground="#000000")
        self.zero.configure(highlightbackground="#d9d9d9")
        self.zero.configure(highlightcolor="black")
        self.zero.configure(pady="0")
        self.zero.configure(text='''0''')

        self.point = tk.Button(top)
        self.point.place(relx=0.898, rely=0.638, height=54, width=67)
        self.point.configure(activebackground="#ececec")
        self.point.configure(activeforeground="#000000")
        self.point.configure(background="#d9d9d9")
        self.point.configure(disabledforeground="#a3a3a3")
        self.point.configure(foreground="#000000")
        self.point.configure(highlightbackground="#d9d9d9")
        self.point.configure(highlightcolor="black")
        self.point.configure(pady="0")
        self.point.configure(text='''.''')

        self.annulation = tk.Button(top)
        self.annulation.place(relx=0.703, rely=0.742, height=54, width=117)
        self.annulation.configure(activebackground="#ececec")
        self.annulation.configure(activeforeground="#000000")
        self.annulation.configure(background="#d9d9d9")
        self.annulation.configure(disabledforeground="#a3a3a3")
        self.annulation.configure(foreground="#000000")
        self.annulation.configure(highlightbackground="#d9d9d9")
        self.annulation.configure(highlightcolor="black")
        self.annulation.configure(pady="0")
        self.annulation.configure(text='''ANNULER''')

        self.validation = tk.Button(top)
        self.validation.place(relx=0.85, rely=0.742, height=54, width=117)
        self.validation.configure(activebackground="#ececec")
        self.validation.configure(activeforeground="#000000")
        self.validation.configure(background="#d9d9d9")
        self.validation.configure(disabledforeground="#a3a3a3")
        self.validation.configure(foreground="#000000")
        self.validation.configure(highlightbackground="#d9d9d9")
        self.validation.configure(highlightcolor="black")
        self.validation.configure(pady="0")
        self.validation.configure(text='''VALIDER''')

        self.commande_suivante = tk.Button(top)
        self.commande_suivante.place(
            relx=0.703, rely=0.846, height=54, width=267)
        self.commande_suivante.configure(activebackground="#ececec")
        self.commande_suivante.configure(activeforeground="#000000")
        self.commande_suivante.configure(background="#d9d9d9")
        self.commande_suivante.configure(disabledforeground="#a3a3a3")
        self.commande_suivante.configure(foreground="#000000")
        self.commande_suivante.configure(highlightbackground="#d9d9d9")
        self.commande_suivante.configure(highlightcolor="black")
        self.commande_suivante.configure(pady="0")
        self.commande_suivante.configure(text='''COMMANDE      SUIVANTE''')

######################
### NOUVEL EMPLOYE ###
######################


def create_popup_nouvel_employe(rt, *args, **kwargs):
    '''Starting point when module is imported by another module.
       Correct form of call: 'create_popup_nouvel_employe(root, *args, **kwargs)' .'''
    global w, w_win, root
    # rt = root
    root = rt
    w = tk.Toplevel(root)
    top = popup_nouvel_employe(w)
    init(w, top, *args, **kwargs)
    return (w, top)


class popup_nouvel_employe:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'

        top.geometry("1024x768+369+133")
        top.minsize(120, 1)
        top.maxsize(1924, 2141)
        top.resizable(0, 0)
        top.title("Nouvel employé")
        top.configure(background="#d9d9d9")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")

        self.annulation = tk.Button(top)
        self.annulation.place(relx=0.703, rely=0.846, height=54, width=117)
        self.annulation.configure(activebackground="#ececec")
        self.annulation.configure(activeforeground="#000000")
        self.annulation.configure(background="#d9d9d9")
        self.annulation.configure(disabledforeground="#a3a3a3")
        self.annulation.configure(foreground="#000000")
        self.annulation.configure(highlightbackground="#d9d9d9")
        self.annulation.configure(highlightcolor="black")
        self.annulation.configure(pady="0")
        self.annulation.configure(text='''ANNULER''', command=root.destroy)

        self.nom = tk.Label(top)
        self.nom.place(relx=0.049, rely=0.078, height=140, width=247)
        self.nom.configure(activebackground="#f9f9f9")
        self.nom.configure(activeforeground="black")
        self.nom.configure(background="#d9d9d9")
        self.nom.configure(disabledforeground="#a3a3a3")
        self.nom.configure(foreground="#000000")
        self.nom.configure(highlightbackground="#d9d9d9")
        self.nom.configure(highlightcolor="black")
        self.nom.configure(text='''Nom :''')

        self.Entry1 = tk.Entry(top)
        self.Entry1.place(relx=0.264, rely=0.156, height=20, relwidth=0.209)
        self.Entry1.configure(background="white")
        self.Entry1.configure(disabledforeground="#a3a3a3")
        self.Entry1.configure(font="TkFixedFont")
        self.Entry1.configure(foreground="#000000")
        self.Entry1.configure(highlightbackground="#d9d9d9")
        self.Entry1.configure(highlightcolor="black")
        self.Entry1.configure(insertbackground="black")
        self.Entry1.configure(selectbackground="blue")
        self.Entry1.configure(selectforeground="white")

        self.prenom = tk.Label(top)
        self.prenom.place(relx=0.098, rely=0.234, height=113, width=150)
        self.prenom.configure(activebackground="#f9f9f9")
        self.prenom.configure(activeforeground="black")
        self.prenom.configure(background="#d9d9d9")
        self.prenom.configure(disabledforeground="#a3a3a3")
        self.prenom.configure(foreground="#000000")
        self.prenom.configure(highlightbackground="#d9d9d9")
        self.prenom.configure(highlightcolor="black")
        self.prenom.configure(text='''Prénom :''')

        self.Entry2 = tk.Entry(top)
        self.Entry2.place(relx=0.264, rely=0.299, height=20, relwidth=0.209)
        self.Entry2.configure(background="white")
        self.Entry2.configure(disabledforeground="#a3a3a3")
        self.Entry2.configure(font="TkFixedFont")
        self.Entry2.configure(foreground="#000000")
        self.Entry2.configure(highlightbackground="#d9d9d9")
        self.Entry2.configure(highlightcolor="black")
        self.Entry2.configure(insertbackground="black")
        self.Entry2.configure(selectbackground="blue")
        self.Entry2.configure(selectforeground="white")

        self.mail = tk.Label(top)
        self.mail.place(relx=0.088, rely=0.365, height=152, width=174)
        self.mail.configure(activebackground="#f9f9f9")
        self.mail.configure(activeforeground="black")
        self.mail.configure(background="#d9d9d9")
        self.mail.configure(disabledforeground="#a3a3a3")
        self.mail.configure(foreground="#000000")
        self.mail.configure(highlightbackground="#d9d9d9")
        self.mail.configure(highlightcolor="black")
        self.mail.configure(text='''Mail :''')

        self.Entry3 = tk.Entry(top)
        self.Entry3.place(relx=0.264, rely=0.456, height=20, relwidth=0.209)
        self.Entry3.configure(background="white")
        self.Entry3.configure(disabledforeground="#a3a3a3")
        self.Entry3.configure(font="TkFixedFont")
        self.Entry3.configure(foreground="#000000")
        self.Entry3.configure(highlightbackground="#d9d9d9")
        self.Entry3.configure(highlightcolor="black")
        self.Entry3.configure(insertbackground="black")
        self.Entry3.configure(selectbackground="blue")
        self.Entry3.configure(selectforeground="white")

        self.validation = tk.Button(top)
        self.validation.place(relx=0.85, rely=0.846, height=54, width=117)
        self.validation.configure(activebackground="#ececec")
        self.validation.configure(activeforeground="#000000")
        self.validation.configure(background="#d9d9d9")
        self.validation.configure(disabledforeground="#a3a3a3")
        self.validation.configure(foreground="#000000")
        self.validation.configure(highlightbackground="#d9d9d9")
        self.validation.configure(highlightcolor="black")
        self.validation.configure(pady="0")

        def _add_employe():
            if self.Entry3.get():
                email_employe = self.Entry3.get()
            else:
                email_employe = None
            add_employee(
                nom=self.Entry1.get(),
                prenom=self.Entry2.get(),
                email=email_employe)
        self.validation.configure(text='''VALIDER''', command=_add_employe)


########################
### MODIFIER EMPLOYE ###
########################


def create_popup_modifier_employe(rt, *args, **kwargs):
    '''Starting point when module is imported by another module.
       Correct form of call: 'create_popup_modifier_employe(root, *args, **kwargs)' .'''
    global w, w_win, root
    #rt = root
    root = rt
    w = tk.Toplevel(root)
    top = popup_modifier_employe(w)
    init(w, top, *args, **kwargs)
    return (w, top)


class popup_modifier_employe:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'

        top.geometry("1024x768+369+133")
        top.minsize(120, 1)
        top.maxsize(1924, 2141)
        top.resizable(0, 0)
        top.title("Modifier employé")
        top.configure(background="#d9d9d9")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")

        self.annulation = tk.Button(top)
        self.annulation.place(relx=0.703, rely=0.846, height=54, width=117)
        self.annulation.configure(activebackground="#ececec")
        self.annulation.configure(activeforeground="#000000")
        self.annulation.configure(background="#d9d9d9")
        self.annulation.configure(disabledforeground="#a3a3a3")
        self.annulation.configure(foreground="#000000")
        self.annulation.configure(highlightbackground="#d9d9d9")
        self.annulation.configure(highlightcolor="black")
        self.annulation.configure(pady="0")
        self.annulation.configure(text='''ANNULER''', command=root.destroy)

        self.nom = tk.Label(top)
        self.nom.place(relx=0.049, rely=0.078, height=140, width=247)
        self.nom.configure(activebackground="#f9f9f9")
        self.nom.configure(activeforeground="black")
        self.nom.configure(background="#d9d9d9")
        self.nom.configure(disabledforeground="#a3a3a3")
        self.nom.configure(foreground="#000000")
        self.nom.configure(highlightbackground="#d9d9d9")
        self.nom.configure(highlightcolor="black")
        self.nom.configure(text='''Nom :''')

        self.Entry0 = tk.Entry(top)

        self.Entry1 = tk.Entry(top)
        self.Entry1.place(relx=0.264, rely=0.156, height=20, relwidth=0.209)
        self.Entry1.configure(background="white")
        self.Entry1.configure(disabledforeground="#a3a3a3")
        self.Entry1.configure(font="TkFixedFont")
        self.Entry1.configure(foreground="#000000")
        self.Entry1.configure(highlightbackground="#d9d9d9")
        self.Entry1.configure(highlightcolor="black")
        self.Entry1.configure(insertbackground="black")
        self.Entry1.configure(selectbackground="blue")
        self.Entry1.configure(selectforeground="white")

        self.prenom = tk.Label(top)
        self.prenom.place(relx=0.098, rely=0.234, height=113, width=150)
        self.prenom.configure(activebackground="#f9f9f9")
        self.prenom.configure(activeforeground="black")
        self.prenom.configure(background="#d9d9d9")
        self.prenom.configure(disabledforeground="#a3a3a3")
        self.prenom.configure(foreground="#000000")
        self.prenom.configure(highlightbackground="#d9d9d9")
        self.prenom.configure(highlightcolor="black")
        self.prenom.configure(text='''Prénom :''')

        self.Entry2 = tk.Entry(top)
        self.Entry2.place(relx=0.264, rely=0.299, height=20, relwidth=0.209)
        self.Entry2.configure(background="white")
        self.Entry2.configure(disabledforeground="#a3a3a3")
        self.Entry2.configure(font="TkFixedFont")
        self.Entry2.configure(foreground="#000000")
        self.Entry2.configure(highlightbackground="#d9d9d9")
        self.Entry2.configure(highlightcolor="black")
        self.Entry2.configure(insertbackground="black")
        self.Entry2.configure(selectbackground="blue")
        self.Entry2.configure(selectforeground="white")

        self.mail = tk.Label(top)
        self.mail.place(relx=0.088, rely=0.365, height=152, width=174)
        self.mail.configure(activebackground="#f9f9f9")
        self.mail.configure(activeforeground="black")
        self.mail.configure(background="#d9d9d9")
        self.mail.configure(disabledforeground="#a3a3a3")
        self.mail.configure(foreground="#000000")
        self.mail.configure(highlightbackground="#d9d9d9")
        self.mail.configure(highlightcolor="black")
        self.mail.configure(text='''Mail :''')

        self.Entry3 = tk.Entry(top)
        self.Entry3.place(relx=0.264, rely=0.456, height=20, relwidth=0.209)
        self.Entry3.configure(background="white")
        self.Entry3.configure(disabledforeground="#a3a3a3")
        self.Entry3.configure(font="TkFixedFont")
        self.Entry3.configure(foreground="#000000")
        self.Entry3.configure(highlightbackground="#d9d9d9")
        self.Entry3.configure(highlightcolor="black")
        self.Entry3.configure(insertbackground="black")
        self.Entry3.configure(selectbackground="blue")
        self.Entry3.configure(selectforeground="white")

        self.liste_employes = tk.Listbox(top)
        db_link = connect_to_db(db_path)
        db_cursor = create_cursor(db_link)
        self.sql_query = 'SELECT * FROM employee'
        self.query_result = read_from_cursor(db_cursor, self.sql_query)
        disconnect_from_db(db_link)

        for a in self.query_result:
            self.liste_employes.insert('end', a)

        def callback(event):

            selection = event.widget.curselection()
            if selection:
                index = selection[0]
                data = event.widget.get(index)
                self.Entry0.delete(0, 'end')
                self.Entry0.insert(0, data[0])
                self.Entry2.delete(0, "end")
                self.Entry2.insert(0, data[1])
                self.Entry1.delete(0, "end")
                self.Entry1.insert(0, data[2])
                self.Entry3.delete(0, "end")
                self.Entry3.insert(0, data[3])
            else:
                self.Entry0.insert(0, "")
                self.Entry1.insert(0, "")
                self.Entry2.insert(0, "")
                self.Entry3.insert(0, "")

        self.liste_employes.bind("<<ListboxSelect>>", callback)
        self.liste_employes.place(
            relx=0.703,
            rely=0.091,
            relheight=0.693,
            relwidth=0.258)
        self.liste_employes.configure(background="white")
        self.liste_employes.configure(disabledforeground="#a3a3a3")
        self.liste_employes.configure(font="TkFixedFont")
        self.liste_employes.configure(foreground="#000000")
        self.liste_employes.configure(highlightbackground="#d9d9d9")
        self.liste_employes.configure(highlightcolor="black")
        self.liste_employes.configure(selectbackground="blue")
        self.liste_employes.configure(selectforeground="white")

        self.validation = tk.Button(top)
        self.validation.place(relx=0.85, rely=0.846, height=54, width=117)
        self.validation.configure(activebackground="#ececec")
        self.validation.configure(activeforeground="#000000")
        self.validation.configure(background="#d9d9d9")
        self.validation.configure(disabledforeground="#a3a3a3")
        self.validation.configure(foreground="#000000")
        self.validation.configure(highlightbackground="#d9d9d9")
        self.validation.configure(highlightcolor="black")
        self.validation.configure(pady="0")

        def _modify_employee():
            if self.Entry3.get() and self.Entry3.get() != "None":
                email_employe = self.Entry3.get()
                print('ok')
            else:
                email_employe = None
                print('ko')
            modify_employee(
                id_user=self.Entry0.get(),
                nom=self.Entry2.get(),
                prenom=self.Entry1.get(),
                email=email_employe)
        self.validation.configure(text='''VALIDER''', command=_modify_employee)


####################
### NOUVEAU MENU ###
####################


def create_popup_ajouter_menu(rt, *args, **kwargs):
    '''Starting point when module is imported by another module.
       Correct form of call: 'create_popup_ajouter_menu(root, *args, **kwargs)' .'''
    global w, w_win, root
    #rt = root
    root = rt
    w = tk.Toplevel(root)
    top = popup_ajouter_menu(w)
    init(w, top, *args, **kwargs)
    return (w, top)


class popup_ajouter_menu:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'

        top.geometry("1024x768+369+133")
        top.minsize(120, 1)
        top.maxsize(1924, 2141)
        top.resizable(0, 0)
        top.title("Ajouter menu")
        top.configure(background="#d9d9d9")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")

        self.annulation = tk.Button(top)
        self.annulation.place(relx=0.703, rely=0.846, height=54, width=117)
        self.annulation.configure(activebackground="#ececec")
        self.annulation.configure(activeforeground="#000000")
        self.annulation.configure(background="#d9d9d9")
        self.annulation.configure(disabledforeground="#a3a3a3")
        self.annulation.configure(foreground="#000000")
        self.annulation.configure(highlightbackground="#d9d9d9")
        self.annulation.configure(highlightcolor="black")
        self.annulation.configure(pady="0")
        self.annulation.configure(text='''ANNULER''', command=root.destroy)

        self.menu = tk.Label(top)
        self.menu.place(relx=0.049, rely=0.078, height=140, width=247)
        self.menu.configure(activebackground="#f9f9f9")
        self.menu.configure(activeforeground="black")
        self.menu.configure(background="#d9d9d9")
        self.menu.configure(disabledforeground="#a3a3a3")
        self.menu.configure(foreground="#000000")
        self.menu.configure(highlightbackground="#d9d9d9")
        self.menu.configure(highlightcolor="black")
        self.menu.configure(text='''Menu :''')

        self.Entry1 = tk.Entry(top)
        self.Entry1.place(relx=0.264, rely=0.156, height=20, relwidth=0.209)
        self.Entry1.configure(background="white")
        self.Entry1.configure(disabledforeground="#a3a3a3")
        self.Entry1.configure(font="TkFixedFont")
        self.Entry1.configure(foreground="#000000")
        self.Entry1.configure(highlightbackground="#d9d9d9")
        self.Entry1.configure(highlightcolor="black")
        self.Entry1.configure(insertbackground="black")
        self.Entry1.configure(selectbackground="blue")
        self.Entry1.configure(selectforeground="white")

        self.prix = tk.Label(top)
        self.prix.place(relx=0.088, rely=0.365, height=152, width=174)
        self.prix.configure(activebackground="#f9f9f9")
        self.prix.configure(activeforeground="black")
        self.prix.configure(background="#d9d9d9")
        self.prix.configure(disabledforeground="#a3a3a3")
        self.prix.configure(foreground="#000000")
        self.prix.configure(highlightbackground="#d9d9d9")
        self.prix.configure(highlightcolor="black")
        self.prix.configure(text='''Prix :''')

        self.Entry3 = tk.Entry(top)
        self.Entry3.place(relx=0.264, rely=0.456, height=20, relwidth=0.209)
        self.Entry3.configure(background="white")
        self.Entry3.configure(disabledforeground="#a3a3a3")
        self.Entry3.configure(font="TkFixedFont")
        self.Entry3.configure(foreground="#000000")
        self.Entry3.configure(highlightbackground="#d9d9d9")
        self.Entry3.configure(highlightcolor="black")
        self.Entry3.configure(insertbackground="black")
        self.Entry3.configure(selectbackground="blue")
        self.Entry3.configure(selectforeground="white")

        self.validation = tk.Button(top)
        self.validation.place(relx=0.85, rely=0.846, height=54, width=117)
        self.validation.configure(activebackground="#ececec")
        self.validation.configure(activeforeground="#000000")
        self.validation.configure(background="#d9d9d9")
        self.validation.configure(disabledforeground="#a3a3a3")
        self.validation.configure(foreground="#000000")
        self.validation.configure(highlightbackground="#d9d9d9")
        self.validation.configure(highlightcolor="black")
        self.validation.configure(pady="0")
        self.validation.configure(text='''VALIDER''')

        def _add_menu():
            add_menu(
                description_menu=self.Entry1.get(),
                prix_menu=self.Entry3.get())
        self.validation.configure(text='''VALIDER''', command=_add_menu)
#####################
### MODIFIER MENU ###
#####################


def create_popup_modifier_menu(rt, *args, **kwargs):
    '''Starting point when module is imported by another module.
       Correct form of call: 'create_popup_modifier_menu(root, *args, **kwargs)' .'''
    global w, w_win, root
    #rt = root
    root = rt
    w = tk.Toplevel(root)
    top = popup_modifier_menu(w)
    init(w, top, *args, **kwargs)
    return (w, top)


class popup_modifier_menu:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'

        top.geometry("1024x768+369+133")
        top.minsize(120, 1)
        top.maxsize(1924, 2141)
        top.resizable(0, 0)
        top.title("Modifier menu")
        top.configure(background="#d9d9d9")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")

        self.annulation = tk.Button(top)
        self.annulation.place(relx=0.703, rely=0.846, height=54, width=117)
        self.annulation.configure(activebackground="#ececec")
        self.annulation.configure(activeforeground="#000000")
        self.annulation.configure(background="#d9d9d9")
        self.annulation.configure(disabledforeground="#a3a3a3")
        self.annulation.configure(foreground="#000000")
        self.annulation.configure(highlightbackground="#d9d9d9")
        self.annulation.configure(highlightcolor="black")
        self.annulation.configure(pady="0")
        self.annulation.configure(text='''ANNULER''', command=root.destroy)

        self.menu = tk.Label(top)
        self.menu.place(relx=0.049, rely=0.078, height=140, width=247)
        self.menu.configure(activebackground="#f9f9f9")
        self.menu.configure(activeforeground="black")
        self.menu.configure(background="#d9d9d9")
        self.menu.configure(disabledforeground="#a3a3a3")
        self.menu.configure(foreground="#000000")
        self.menu.configure(highlightbackground="#d9d9d9")
        self.menu.configure(highlightcolor="black")
        self.menu.configure(text='''Menu :''')
        self.Entry0 = tk.Entry(top)
        self.Entry1 = tk.Entry(top)
        self.Entry1.place(relx=0.264, rely=0.156, height=20, relwidth=0.209)
        self.Entry1.configure(background="white")
        self.Entry1.configure(disabledforeground="#a3a3a3")
        self.Entry1.configure(font="TkFixedFont")
        self.Entry1.configure(foreground="#000000")
        self.Entry1.configure(highlightbackground="#d9d9d9")
        self.Entry1.configure(highlightcolor="black")
        self.Entry1.configure(insertbackground="black")
        self.Entry1.configure(selectbackground="blue")
        self.Entry1.configure(selectforeground="white")

        self.prix = tk.Label(top)
        self.prix.place(relx=0.088, rely=0.365, height=152, width=174)
        self.prix.configure(activebackground="#f9f9f9")
        self.prix.configure(activeforeground="black")
        self.prix.configure(background="#d9d9d9")
        self.prix.configure(disabledforeground="#a3a3a3")
        self.prix.configure(foreground="#000000")
        self.prix.configure(highlightbackground="#d9d9d9")
        self.prix.configure(highlightcolor="black")
        self.prix.configure(text='''Prix :''')

        self.Entry3 = tk.Entry(top)
        self.Entry3.place(relx=0.264, rely=0.456, height=20, relwidth=0.209)
        self.Entry3.configure(background="white")
        self.Entry3.configure(disabledforeground="#a3a3a3")
        self.Entry3.configure(font="TkFixedFont")
        self.Entry3.configure(foreground="#000000")
        self.Entry3.configure(highlightbackground="#d9d9d9")
        self.Entry3.configure(highlightcolor="black")
        self.Entry3.configure(insertbackground="black")
        self.Entry3.configure(selectbackground="blue")
        self.Entry3.configure(selectforeground="white")

        self.liste_menu = tk.Listbox(top)

        db_link = connect_to_db(db_path)
        db_cursor = create_cursor(db_link)
        self.sql_query = 'SELECT * FROM menu'
        self.query_result = read_from_cursor(db_cursor, self.sql_query)
        disconnect_from_db(db_link)

        for a in self.query_result:
            self.liste_menu.insert('end', a)

        def callback(event):

            selection = event.widget.curselection()
            if selection:
                index = selection[0]
                data = event.widget.get(index)
                self.Entry0.delete(0, 'end')
                self.Entry0.insert(0, data[0])
                self.Entry1.delete(0, "end")
                self.Entry1.insert(0, data[1])
                self.Entry3.delete(0, "end")
                self.Entry3.insert(0, data[2])
            else:
                self.Entry0.insert(0, "")
                self.Entry1.insert(0, "")
                self.Entry3.insert(0, "")

        self.liste_menu.bind("<<ListboxSelect>>", callback)

        self.liste_menu.place(
            relx=0.703,
            rely=0.091,
            relheight=0.693,
            relwidth=0.258)
        self.liste_menu.configure(background="white")
        self.liste_menu.configure(disabledforeground="#a3a3a3")
        self.liste_menu.configure(font="TkFixedFont")
        self.liste_menu.configure(foreground="#000000")
        self.liste_menu.configure(highlightbackground="#d9d9d9")
        self.liste_menu.configure(highlightcolor="black")
        self.liste_menu.configure(selectbackground="blue")
        self.liste_menu.configure(selectforeground="white")

        self.validation = tk.Button(top)
        self.validation.place(relx=0.85, rely=0.846, height=54, width=117)
        self.validation.configure(activebackground="#ececec")
        self.validation.configure(activeforeground="#000000")
        self.validation.configure(background="#d9d9d9")
        self.validation.configure(disabledforeground="#a3a3a3")
        self.validation.configure(foreground="#000000")
        self.validation.configure(highlightbackground="#d9d9d9")
        self.validation.configure(highlightcolor="black")
        self.validation.configure(pady="0")
        self.validation.configure(text='''VALIDER''')

        def _modify_menu():
            modify_menu(
                id_menu=self.Entry0.get(),
                description_menu=self.Entry1.get(),
                nouveau_prix=self.Entry3.get())
        self.validation.configure(text='''VALIDER''', command=_modify_menu)


if __name__ == '__main__':
    vp_start_gui()
