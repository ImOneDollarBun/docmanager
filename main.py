import os
import pathlib
import sqlite3
import sys
import webbrowser
import shutil
from datetime import datetime
from tkinter import Tk, END, Label, Menu, Button, Entry, Frame, VERTICAL, NO, RIGHT, LEFT, BOTH, Y, Checkbutton, \
    BooleanVar
from tkinter import filedialog
from tkinter import ttk, messagebox, scrolledtext

from database import Docs

import zipfile


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        # Если это исполняемый файл
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Если это скрипт в IDE
        return os.path.join(os.path.dirname(__file__), relative_path)


def resource_path_ico(relative_path):
    """ Получить абсолютный путь к ресурсу, работает как в обычном режиме, так и в PyInstaller. """
    try:
        # PyInstaller создает временные пути для файлов, которые мы можем использовать
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def create_database():
    db_name = rf"C:\Users\{os.getlogin()}\AppData\Roaming\Andrew's filemanager\docs-base.db"
    if not os.path.exists(rf"C:\Users\{os.getlogin()}\AppData\Roaming\Andrew's filemanager"):
        os.mkdir(rf"C:\Users\{os.getlogin()}\AppData\Roaming\Andrew's filemanager")

    # Подключение к базе данных (создаст файл, если его нет)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # SQL-запрос для создания таблицы docs
    create_docs_table = """
    CREATE TABLE IF NOT EXISTS docs (
        doc_id INTEGER PRIMARY KEY UNIQUE,
        docs_dictionary TEXT,
        filename TEXT,
        file_description TEXT,
        time TEXT,
        mark TEXT,
        path_on_pc TEXT
    );
    """

    # SQL-запрос для создания таблицы dictionaries
    create_dictionaries_table = """
    CREATE TABLE IF NOT EXISTS dictionaries (
        dict_num INTEGER PRIMARY KEY UNIQUE,
        dict_name TEXT
    );
    """

    # Выполнение запросов
    cursor.execute(create_docs_table)
    cursor.execute(create_dictionaries_table)

    # Сохранение изменений и закрытие соединения
    conn.commit()
    conn.close()

    return db_name


# Получаем путь к базе данных
db_path = create_database()
dict_path = rf"C:\Users\{os.getlogin()}\AppData\Roaming\Andrew's filemanager\dicts"

# Инициализируем базу данных
db = Docs(db_path)
# db_path = os.path.join(os.path.dirname(__file__), 'docs-base.db')

window = Tk()
window.title("Andrew's filemanager")
window.geometry("950x520")
window.wm_iconbitmap(resource_path_ico("15105674.ico"))


def get_cur():
    lbl_cur_dict_settings.configure(text=f"{combo_settings.get()}")
    combo_settings['values'] = tuple(db.export_name_dictionaries())


def delete_dict_from_pc(name):
    os.rmdir(name)


def delete_cur_dict():
    db.delete_dictionary(combo_settings.get())
    delete_dict_from_pc(rf"C:\Users\{os.getlogin()}\AppData\Roaming\Andrew's filemanager\dicts\{combo_settings.get()}")
    combo_settings['values'] = tuple(db.export_name_dictionaries())


def set_dict():
    db.set_dictionary(entry_add_dict_settings.get())
    combo_settings['values'] = tuple(db.export_name_dictionaries())
    create_dicts()


def export_db():
    file_path = filedialog.asksaveasfilename(
        title="Сохранить базу данных",
        defaultextension=".sqlite3",
        filetypes=[("SQLite files", "*.sqlite3"), ("All files", "*.*")],
        initialfile="Andrew-s filemanager database"
    )

    if file_path:
        try:
            # Подключаемся к исходной базе данных
            source_db = sqlite3.connect(db_path)

            # Клонируем базу данных
            source_db.execute(f"VACUUM INTO '{file_path}';")

            # Закрываем соединение с исходной базой данных
            source_db.close()

            # messagebox.showinfo("Успех", "База данных успешно клонирована!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")


def export_files():
    filepath = filedialog.asksaveasfilename(
        title="Выгрузить все записи",
        defaultextension=".txt",
        filetypes=[("text files", "*.txt"), ("All files", "*.*")],
        initialfile="Andrew-s filemanager files",
        confirmoverwrite=False
    )

    if filepath:
        try:
            with open(filepath, "w+") as file:
                # titles
                marks = [f"{'id':<5}",
                         f"{'Cat':<15}",
                         f"{'name':<30}",
                         f"{'description':<40}",
                         f"{'date':<20}"]
                if check_for.get():
                    marks.append(f"{'Путь к файлу':<40}")
                for i in marks:
                    file.write(f"{i}")
                file.write("\n")

                # elements
                for el in db.get_all_files():
                    file.write("\n")
                    file.write(f"{el[0]:<5}")
                    file.write(f"{el[1]:<15}")
                    file.write(f"{el[2]:<30}")
                    file.write(f"{el[3]:<40}")
                    file.write(f"{el[4]:<20}")
                    if check_for.get():
                        if el[5] is None:
                            file.write(f"{'None':<40}")
                        else:
                            file.write(f"{el[5]:<40}")

        except Exception as e:
            messagebox.showerror("Error", f"{e}")
    os.startfile(filepath)


def update_dicts():
    combo_add_file['values'] = tuple(db.export_name_dictionaries())
    find_by_dict_combobox['values'] = tuple(db.export_name_dictionaries())


def send_fileid(filename):
    lbl_file_id.configure(text=db.get_fileid(filename))


def cleanup():
    entry_add_filename.delete(0, END)

    text_description.delete("1.0", END)
    entry_filepath.delete(0, "end")
    entry_new_filepath.delete(0, "end")


def empty_areas():
    messagebox.showerror("Emtpy areas", "Emtpy areas\nDictionary box and filename box")


def confirm_add():
    dictionary = combo_add_file.get()
    filename = entry_add_filename.get()
    mark = entry_add_default_mark_abc.get() + entry_add_default_mark_num.get()

    if not len(entry_filepath.get()) == 0:
        get_new_dict(entry_filepath.get())
        filepath = entry_new_filepath.get()
    else:
        filepath = None

    description = text_description.get("1.0", END)[:-1]

    cur_time = datetime.now()
    time = f"{cur_time.year}-" + f"{cur_time.month}-" + f"{cur_time.day}" + f" {cur_time.hour}:" + f"{cur_time.minute}"

    if len(filename) == 0 or len(dictionary) == 0:
        empty_areas()

    else:

        if len(description) == 0:
            description = "None"

        db.set_doc(filename, dictionary, description, time, mark=mark, filepath=filepath)
        create_dicts()
        send_mark()
        send_fileid(filename)

        cleanup()
        get_mark(mark)
        db.commit_changes()


def find_docs():
    filename = entry_find_by_filename.get()
    filemark = entry_find_by_mark.get()
    combo = find_by_dict_combobox.get()
    if len(filename) != 0:
        find_like(filename)
    elif len(filemark) != 0:
        draw_res(db.find_by_mark(filemark))
    elif len(combo) != 0:
        find_by_dict(combo)

    if len(filename) != 0 and len(filemark) != 0 and len(combo) != 0:
        entry_find_by_filename.delete(0, 'end')
        entry_find_by_mark.delete(0, 'end')
        find_by_dict_combobox.set("")

        messagebox.showinfo("Info", 'find file only by single filer')


def find_by_dict(dictio):
    items = db.find_file_by_directory(dictio)
    contents = []
    for item in items:
        contents.append(item)
    draw_res(contents)


def draw_res(results):
    for item in tree.get_children():
        tree.delete(item)
    for el in results:
        tree.insert("", END, values=(f"{el[0]}",
                                     f"{el[1]}",
                                     f"{el[5]}",
                                     f"{el[2]}",
                                     f"{el[3]}",
                                     f"{el[4]}",
                                     f"{el[6]}"
                                     ))


def find_like(pattern: str):
    contents = db.export_filenames()
    tmp_list = []
    for el in contents:
        if pattern.lower() in el.lower():
            tmp_list.append(db.find_by_filename(el))
    draw_res(tmp_list)


def all_files():
    draw_res(db.get_all_files())


def delete_from_folder(path):
    os.remove(path)


def delete_file():
    selected_items = tree.selection()
    for el in selected_items:
        file_text = tree.item(el, "values")
        db.delete_file_by_id(file_text[0])
        if not file_text[-1] == "None":
            delete_from_folder(file_text[-1])
    all_files()
    db.commit_changes()


def help_button():
    messagebox.showinfo("Tutorial", "1. Choose settings tab\n"
                                    "2. Select 'add dict' area\n"
                                    "3. Name new dictionary\n"
                                    "4. Click an 'add' button\n"
                                    "Now, you have the new dictionary\n\n"
                                    "To delete an dictionary:\n"
                                    "1. Choose name in a top left box\n"
                                    "2. Click the next button\n"
                                    "3. Click 'del' button\n\n"
                                    "Next, go to Add file tab:\n"
                                    "1. Choose the dictionary\n"
                                    "2. Write file name\n"
                                    "3. Write file description\n"
                                    "4. Click on the 'confirm and add' button\n"
                                    "5. Write down an file id\n\n"
                                    "To find the file, go to the same tab:\n"
                                    "Write file name or file id to find the information about file\n\n"
                                    "To delete file:\n"
                                    "1. choose file in the table by mouse click\n"
                                    "2. click delete button on the left\n\n")


def add_file_path():
    filepath = filedialog.askopenfilename(initialdir=rf"C:\Users\{os.getlogin()}\Documents")
    entry_filepath["state"] = "normal"
    entry_filepath.delete(0, "end")
    entry_filepath.insert(0, filepath)
    entry_filepath["state"] = "disabled"


def create_dicts():
    parent = rf"C:\Users\{os.getlogin()}\AppData\Roaming\Andrew's filemanager\dicts"
    if not os.path.exists(parent):
        os.mkdir(parent)
    for dictionary in db.export_name_dictionaries():
        if not os.path.exists(rf"{parent}\{dictionary}"):
            os.mkdir(rf"{parent}\{dictionary}")


def get_new_dict(filepath):
    dir_list = os.listdir(rf"C:\Users\{os.getlogin()}\AppData\Roaming\Andrew's filemanager\dicts")
    parent = rf"C:\Users\{os.getlogin()}\AppData\Roaming\Andrew's filemanager\dicts"
    for directory in dir_list:
        if combo_add_file.get() == directory:
            shutil.copy(filepath, rf"{parent}\{directory}")

            only_file = os.path.basename(filepath)

            entry_new_filepath["state"] = "normal"
            entry_new_filepath.delete(0, "end")
            entry_new_filepath.insert(0,
                                      rf"{parent}\{directory}\{only_file}")
            entry_new_filepath["state"] = "disabled"


def browser():
    webbrowser.open_new("https://github.com/ImOneDollarBun")


def open_parent_folder():
    create_dicts()
    os.startfile(rf"C:\Users\{os.getlogin()}\AppData\Roaming\Andrew's filemanager")


def export_rar():
    filepath = filedialog.asksaveasfilename(
        title="Сохранить базу данных",
        defaultextension=".zip",
        filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
        initialfile="Andrew-s filemanager archive"
    )

    if filepath:
        try:
            directory = pathlib.Path(rf"C:\Users\{os.getlogin()}\AppData\Roaming\Andrew's filemanager")

            with zipfile.ZipFile(f"{filepath}", mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=5) as archive:
                for file_path in directory.rglob('*'):
                    archive.write(file_path, arcname=file_path.relative_to(directory))

        except Exception as e:
            messagebox.showerror("Error", f"{e}")


def get_mark(old_mark):
    abc = entry_add_default_mark_abc.get()
    num = entry_add_default_mark_num.get()

    try:
        if abc in old_mark:
            if str(int(num)) in old_mark:
                entry_add_default_mark_num.delete(0, "end")
                entry_add_default_mark_num.insert(0, str(int(num)+1))
    except Exception as e:
        messagebox.showerror('oshibka', f"{e}")


def send_mark():
    result_mark["state"] = "normal"
    result_mark.delete(0, "end")
    result_mark.insert(0, f"{entry_add_default_mark_abc.get()}-{entry_add_default_mark_num.get()}")
    result_mark['state'] = "disabled"


# menu
main_menu = Menu()
# option_help = Menu(menu)

help_menu = Menu(tearoff=0)

help_menu.add_command(label="how to use", command=help_button)

about_menu = Menu(tearoff=0)
about_menu.add_command(label="About developer (link)", command=browser)

main_menu.add_cascade(label="Help", menu=help_menu)
main_menu.add_cascade(label="About", menu=about_menu)
# tab manager
tab_control = ttk.Notebook(window)

# tabs
tab_settings = ttk.Frame(tab_control)
tab_add_file = ttk.Frame(tab_control)
tab_find_file = ttk.Frame(tab_control)

# adding tabs
tab_control.add(tab_find_file, text="Find file")
tab_control.add(tab_add_file, text="Add file")
tab_control.add(tab_settings, text="Settings")


# label tabs
# settings \tab_settings\ ----------------------------------------------------------------------------------------------
combo_settings = ttk.Combobox(tab_settings, width=20)
combo_settings['values'] = tuple(db.export_name_dictionaries())
combo_settings["state"] = "readonly"

lbl_cur_dict_settings = Label(tab_settings, text="", bg="lightgray", width=35)

btn_confirm_cur_dict_settings = Button(tab_settings, text="✔", command=get_cur)
btn_delete_confirm_dict_settings = Button(tab_settings, text="del", command=delete_cur_dict)

lbl_txt_cur_dict_settings = Label(tab_settings, text="Current dict")


lbl_txt_add_dict_settings = Label(tab_settings, text="Add dict")
entry_add_dict_settings = Entry(tab_settings, width=41)
btn_add_dict_settings = Button(tab_settings, text="add", command=set_dict)


empty_lbl_rowb = Label(tab_settings, height=22)
btn_export_database = Button(tab_settings, text="export database", command=export_db)

btn_export_files = Button(tab_settings, text="export files via txt", command=export_files)

btn_open_parent_folder = Button(tab_settings, text="Open filemanager folder", command=open_parent_folder)

check_for = BooleanVar()
check_for.set(False)
check_for_path = Checkbutton(tab_settings, text="Enter file path", variable=check_for)

export_via_rar = Button(tab_settings, text="Export via ZIP (only-on-pc-files)", command=export_rar)


# add file \tab_add_file\ ----------------------------------------------------------------------------------------------
lbl_add_file = Label(tab_add_file, text="filename")
combo_add_file = ttk.Combobox(tab_add_file, width=20)
combo_add_file['values'] = tuple(db.export_name_dictionaries())
combo_add_file["state"] = "readonly"
entry_add_filename = Entry(tab_add_file, width=52)
text_description = scrolledtext.ScrolledText(tab_add_file, width=60, height=10)
lbl_add_desc = Label(tab_add_file, text="description")
lbl_file_id = Label(tab_add_file, text="", bg="gray")
btn_confirm = Button(tab_add_file, text="Confirm and add", command=confirm_add)
btn_update_dicts = Button(tab_add_file, text="🔄", command=update_dicts)


txt_file_id = Label(tab_add_file, text="file_id for mark", underline=10)

entry_filepath = Entry(tab_add_file, width=81, state="disabled")
txt_filepath = Label(tab_add_file, text="Optionally")
btn_file_path = Button(tab_add_file, text="📂", command=add_file_path)

txt_filepath_will_be_saved = Label(tab_add_file, text=f"it will be copied in")
entry_new_filepath = Entry(tab_add_file, width=81, state="disabled")

txt_add_mark = Label(tab_add_file, text="mark")
entry_add_default_mark_abc = Entry(tab_add_file, width=10)
entry_add_default_mark_num = Entry(tab_add_file, width=5)
result_mark = Entry(tab_add_file, width=15, state="disabled")


# find file \tab_find_file\ --------------------------------------------------------------------------------------------
txt_enter_filename = Label(tab_find_file, text="enter filename")
entry_find_by_filename = Entry(tab_find_file, width=81)

txt_enter_fileid = Label(tab_find_file, text="enter mark")
entry_find_by_mark = Entry(tab_find_file, width=72)
txt_results = Label(tab_find_file, text="results")

tree_frame = Frame(tab_find_file)

scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL)
tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set,
                    columns=("doc-id", "dictionary", "mark", "filename", "description", "time", "path"), height=17)
tree.heading("#0", text="", anchor="center")
tree.heading("doc-id", text="id")
tree.heading("dictionary", text="Категория")
tree.heading("mark", text="Метка")
tree.heading("filename", text="Наименование")
tree.heading("description", text="Описание")
tree.heading("time", text="Дата добавления")
tree.heading("path", text="Путь")

tree.column("#0", width=0, stretch=NO)
tree.column("doc-id", anchor="center", width=30, stretch=False)
tree.column("dictionary", anchor="center", width=100)
tree.column("mark", anchor="center", width=50)
tree.column("filename", anchor="center", width=140)
tree.column("description", anchor="center", width=250)
tree.column("time", anchor="center", width=100)
tree.column("path", anchor="center", width=150)

scrollbar.config(command=tree.yview)


btn_find_file = Button(tab_find_file, text="Find ▶", command=find_docs)

btn_all_files = Button(tab_find_file, text="All files", command=all_files)

btn_delete_item = Button(tab_find_file, text="delete", command=delete_file)

find_by_dict_combobox = ttk.Combobox(tab_find_file, width=20)
find_by_dict_combobox['values'] = tuple(db.export_name_dictionaries())
find_by_dict_combobox['state'] = 'readonly'

btn_update_dicts_findtab = Button(tab_find_file, text="🔄", command=update_dicts)

txt_or = Label(tab_find_file, text="or enter dictionary")

# pasting labels and other
# settings -------------------------------------------------------------------------------------------------------------

combo_settings.place(x=15, y=15)
lbl_cur_dict_settings.place(x=300, y=15)
btn_confirm_cur_dict_settings.place(x=163, y=13)

lbl_txt_cur_dict_settings.place(x=226, y=15)
btn_delete_confirm_dict_settings.place(x=559, y=13)


lbl_txt_add_dict_settings.place(x=245, y=50)
entry_add_dict_settings.place(x=300, y=50)
btn_add_dict_settings.place(x=559, y=50)

btn_export_database.place(x=15, y=437)

btn_export_files.place(x=120, y=437)

btn_open_parent_folder.place(x=15, y=400)

check_for_path.place(x=230, y=437)

export_via_rar.place(x=350, y=437)

# add file -------------------------------------------------------------------------------------------------------------
lbl_add_file.place(x=200+280, y=15)
lbl_add_desc.place(x=15+280, y=60)
combo_add_file.place(x=15, y=15)
entry_add_filename.place(x=260+280, y=16)
text_description.place(x=90+280, y=61)
btn_update_dicts.place(x=160, y=13)
lbl_file_id.place(x=100, y=437)
txt_file_id.place(x=15, y=437)
btn_confirm.place(x=480+280, y=437)

btn_file_path.place(x=235-170+280, y=298)
txt_filepath.place(x=90+280, y=275)
entry_filepath.place(x=260-170+280, y=300)

txt_filepath_will_be_saved.place(x=90+280, y=300+25)
entry_new_filepath.place(x=260-170+280, y=315+30)

txt_add_mark.place(x=15, y=100)
entry_add_default_mark_abc.place(x=50, y=100)
entry_add_default_mark_num.place(x=110, y=100)
result_mark.place(x=50, y=130)

# find file ------------------------------------------------------------------------------------------------------------
txt_enter_filename.place(x=15, y=15)
entry_find_by_filename.place(x=100, y=15)

txt_enter_fileid.place(x=15, y=40)
entry_find_by_mark.place(x=100, y=40)

btn_find_file.place(x=547, y=40)

txt_results.place(x=15, y=100)


tree.pack(side=LEFT, fill=BOTH)
scrollbar.pack(side=RIGHT, fill=Y)

btn_all_files.place(x=15, y=437)

btn_delete_item.place(x=15, y=200)

tree_frame.place(x=100, y=100)

find_by_dict_combobox.place(x=740, y=14)
txt_or.place(x=620, y=15)

btn_update_dicts_findtab.place(x=887, y=12)

# finishing
tab_control.pack(expand=1, fill="both")
window.config(menu=main_menu)

window.mainloop()
