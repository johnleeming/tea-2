import os
import re
import tkinter as tk
from datetime import datetime
import time

home_path =  os.path.expanduser('~/')
word_file = 'word_lists/wlist_match3.txt'
text_font = "liberation sans"
text_size = 16
bgcolour = {'dark': 'black', 'light': 'white', 'alarm': 'red'}
fgcolour = {'dark': 'white', 'light': 'black', 'alarm': 'black'}
buttonbg = {'dark': 'darkgrey', 'light': 'lightgrey', 'alarm': 'darkgrey'}
theme = 'light'
winheight = 500
winwidth = 1000
winx = 10
winy = 10
paddingh = 5
paddingv = 5


def load_list(filename):
    temp_list = []
    with open (home_path + filename, 'r') as input_file:
        for line in input_file:
            temp_list.append(line[:-1])
    load_message = 'File ' + filename + ' loaded containing ' + str(len(temp_list)) + ' words.'
    return(temp_list, load_message)


def find_matches(query, list):
    start_time = datetime.now()
    matches = []
    for i in list:
        if query.match(i):
            matches.append(i)
    end_time = datetime.now()
    time_taken = end_time - start_time
    return(matches, time_taken)


def go():
    query = input_query.get()
    re_query = re.compile(query)
    match_list, search_time = find_matches(re_query, word_list)
    time_text = 'search took: ' + str(search_time.total_seconds()) + ' seconds'
    solution_time_label = tk.Label(root, text = time_text, font=(text_font, text_size),bg=bgcolour[theme],
                                   fg=fgcolour[theme]).grid(row = 2, column = 0, columnspan = 3)
    no_results_text = str(len(match_list)) + ' matches found'
    no_results_lable = tk.Label(root, text = no_results_text, font=(text_font, text_size),bg=bgcolour[theme],
                                fg=fgcolour[theme]).grid(row = 3, column = 0, columnspan = 3)
    results_label = tk.Label(root, text = match_list, font=(text_font, text_size),bg=bgcolour[theme],fg=fgcolour[theme],
                             wraplength = winwidth - 20).grid(row = 4, column = 0, columnspan = 3)


root = tk.Tk()

word_list, load_message = load_list(word_file)
print(load_message)
root.title('Regex-based Word Search')
root.geometry('%dx%d+%d+%d' % (winwidth, winheight, winx, winy))
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
message1 = tk.Label(root, text = load_message, font=(text_font, text_size),bg=bgcolour[theme],fg=fgcolour[theme])\
    .grid(row = 0, column = 0, columnspan =2)
prompt = tk.Label(root, text = 'Enter Regex query: ', font=(text_font, text_size),bg=bgcolour[theme],fg=fgcolour[theme])\
    .grid(row = 1, column = 0)
input_query = tk.StringVar()
query_entry = tk.Entry(root, textvariable = input_query, font=(text_font, text_size),bg=bgcolour[theme],fg=fgcolour[theme]).grid(row = 1, column = 1)
enter_button = tk.Button(root, text="Go", font=(text_font, text_size), bg=buttonbg[theme], fg=fgcolour[theme],
                           command= go).grid(row=1, column = 3, padx=paddingh, pady=paddingv)


root.mainloop()
