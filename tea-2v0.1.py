#word searching using regex
import re
import tkinter as tk
from tkinter import filedialog
from tkinter import *
import os
import logging
from datetime import datetime
import time

# configuration variables
home_path =  os.path.expanduser('~/')
log_file = home_path + 'logs/tea-2' + datetime.now().strftime('%y-%m-%d') + '.txt'
logging.basicConfig(filename=log_file,level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
textfont = "liberation sans narrow"
textsize = 16
bgcolour = {'dark': 'black', 'light': 'white', 'alarm': 'red'}
fgcolour = {'dark': 'white', 'light': 'black', 'alarm': 'black'}
buttonbg = {'dark': 'darkgrey', 'light': 'lightgrey', 'alarm': 'darkgrey'}
theme = 'light'
winheight = 1000
winwidth = 2000
winx = 10
winy = 10
paddingh = 5
paddingv = 5

#initialisation
input_text = ''
list_file_name =''
word_list = []

def root_menu():
    global theme
    root.geometry('%dx%d+%d+%d' % (winwidth, winheight, winx, winy))
    root['bg'] = bgcolour[theme]
    root.grid_columnconfigure(0, weight=1)
    list_btn = tk.Button(root, text="Select Wordlist", font=(textfont, textsize), bg=buttonbg[theme],
                        fg=fgcolour[theme], command= lambda: choose_list()).grid(row=0, sticky=W + E + N + S, padx=paddingh,
                                                                       pady=paddingv)
    query_btn = tk.Button(root, text="Enter Query", font=(textfont, textsize), bg=buttonbg[theme],
                         fg=fgcolour[theme], command=input_query()).grid(row=1, sticky=W + E + N + S, padx=paddingh,
                                                                       pady=paddingv)
    themebtn = tk.Button(root, text="Theme", font=(textfont, textsize), bg=buttonbg[theme], fg=fgcolour[theme],
                         command=lambda: toggle_theme(root, 'root')).grid(row=2, sticky=W + E + N + S,
                                                                          padx=paddingh, pady=paddingv)
    quitbtn = tk.Button(root, text="Quit", font=(textfont, textsize), bg=buttonbg[theme], fg=fgcolour[theme],
                        command=root.destroy).grid(row=4, sticky=W + E + N + S, padx=paddingh, pady=paddingv)
    time_displayer(root)


# asking for wordlist to use - expects .txt file with 1 word per line
def choose_list ():
#    root.withdraw()
    global list_file_name
    list_file_name =  filedialog.askopenfilename(initialdir =home_path + 'word_lists/', title ="Select wordlist",
                                               filetypes = (("Text files","*.txt"),("all files","*.*")))
    load_list(list_file_name)
#    root.deiconify()
    return


def load_list(file_name):
    try:
        with open (file_name, 'r') as in_file:
            for line in in_file:
                word_list.append(line)
    except:
        logging.exception('wordlist load failed')
        word_list.append('ERROR')
    return


def retrieve_input():
    global input_text
    input_text = root.input_box.get("1.0",'end-1c')


def input_query():
    print('input query')
    input_window = tk.Toplevel()
    input_window.title('Input Query')
#    new_query = tk.StringVar()
    invalid_query = True
#    while invalid_query:
    instruction = tk.Label(input_window, text="Enter Regex here", font=(textfont, textsize), bg=bgcolour[theme],
                                 fg=fgcolour[theme])
#    entry= tk.Entry(input_window)
    enter_button = tk.Button(input_window, text="Enter", command= retrieve_input)
#        try:
#    temp_q = str(entry)
#    new_re_query = re.compile(temp_q)
    time.sleep(5)
    invalid_query = False
#        except:
#            tk.Label(root, text="Invalid Regex - try again")
    return (new_re_query, temp_q)


def search_list(query_to_search):
    print('starting search')
    found_list = []
    for i in word_list:
        if query_to_search.match(i):
            found_list.append(i)
    if len(found_list) == 0:
        found_list.append('No match found.')
    return(found_list)


def display_output(list_to_display, search_time):
    output_page = tk.Toplevel()
    output_page.title('Results')
    output_message = str(len(list_to_display)) + ' words found in ' + str(search_time.total_seconds())
    tk.Label(output_page, text=output_message).grid(column=0, row=0)
    output_list = tk.StringVar()
    temp_list = ''
    for i in list_to_display:
        temp_list += i + '\n'
    output_list.set(temp_list)
    tk.Label(output_page, text=output_list).grid(column=0, row=1)


# main
root = tk.Tk()
print('Hello')
root_menu()

word_list, total_words = load_list(list_file_name)
print(list_file_name + ' loaded '+ str(total_words) + ' words imported.')


re_query, str_query = input_query()
start_time = datetime.now()
results_list = search_list(re_query)
end_time = datetime.now()
time_taken = end_time - start_time

display_output(results_list, time_taken)

root.mainloop
