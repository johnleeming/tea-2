#word searching using regex
import re
import tkinter as tk
from tkinter import filedialog
import os
import logging
from datetime import datetime
import time

# configuration variables
home_path =  os.path.expanduser('~/')
log_file = home_path + 'logs/tea-2' + datetime.now().strftime('%y-%m-%d') + '.txt'
logging.basicConfig(filename=log_file,level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
winheight = 440
winwidth = 800
winx = 10
winy = 10
paddingh = 5
paddingv = 5

# asking for wordlist to use - expects .txt file with 1 word per line
def choose_list ():
#    root.withdraw()
    in_file_name =  filedialog.askopenfilename(initialdir =home_path + 'word_lists/', title ="Select wordlist",
                                               filetypes = (("Text files","*.txt"),("all files","*.*")))
    return(in_file_name)


def load_list(file_name):
    new_list = []
    a = 0
    try:
        with open (file_name, 'r') as in_file:
            for line in in_file:
                new_list.append(line)
                a += 1
    except:
        logging.exception('wordlist load failed')
        new_list.append('ERROR')
    return(new_list, a)

def retrieve_input():
    input_text = input_page.input_box.get("1.0",'end-1c')
    return (input_text)

def input_query():
    print('input query')
    input_page = tk.Toplevel()
    input_page.geometry('%dx%d+%d+%d' % (winwidth, winheight, winx, winy))
    input_page.title('Input Query')
    input_page.grid_columnconfigure(0, weight=1)
    input_page.grid_columnconfigure(1, weight=1)
    input_page.grid_rowconfigure(0, weight=1)
    input_page.grid_rowconfigure(1, weight=1)
    input_page.grid_rowconfigure(2, weight=1)
#    new_query = tk.StringVar()
    invalid_query = True
#    while invalid_query:
    instruction = tk.Label(input_page, text="Enter Regex here").grid(column=0, row=0)
    input_box= tk.Text(input_page).grid(column=0, row=1)
    new_query = tk.Button(input_page, text="Enter", command= lambda: retrieve_input() ).grid(column=1, row=2)
#        try:
    temp_q = str(new_query)
    new_re_query = re.compile(temp_q)
    time.sleep(10)
    invalid_query = False
#        except:
#            tk.Label(input_page, text="Invalid Regex - try again")
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

print('Hello')
list_file_name = choose_list()
word_list, total_words = load_list(list_file_name)
print(list_file_name + ' loaded '+ str(total_words) + ' imported.')
root = tk.Tk()
root.geometry('%dx%d+%d+%d' % (winwidth, winheight, winx, winy))
root.mainloop
re_query, str_query = input_query()
start_time = datetime.now()
results_list = search_list(re_query)
end_time = datetime.now()
time_taken = end_time - start_time

display_output(results_list, time_taken)


