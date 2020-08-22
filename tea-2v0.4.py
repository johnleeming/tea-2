import os
import re
import tkinter as tk
from tkinter import scrolledtext
from tkinter import font as tkfont
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
winheight = 1000
winwidth = 1000
winx = 100
winy = 100
paddingh = 5
paddingv = 5
hint_text= "[abc] - one of the listed letters | . any character | * 0 or more | + 1 or more | ? optional | (a|b) a or b " \
           "| \Z end of string"


def load_list(filename):
    temp_list = []
    with open (home_path + filename, 'r') as input_file:
        for line in input_file:
            temp_list.append(line[:-1])
    load_message = 'Using ' + filename + ' containing ' + str(len(temp_list)) + ' words.'
    return(temp_list, load_message)


def find_matches(query, list, min, max):
    start_time = datetime.now()
    matches = ''
    for i in list:
        if query.match(i) and min <= len(i) <= max:
            matches += i + '\t'
    end_time = datetime.now()
    time_taken = end_time - start_time
    return(matches, time_taken)


def go():
    query = input_query.get()
    min_len = int(min_length.get())
    max_len = int(max_length.get())
    re_query = re.compile(query)
    match_list, search_time = find_matches(re_query, word_list, min_len, max_len)
    time_text = 'search took: ' + str(search_time.total_seconds()) + ' seconds'
    solution_time_label = tk.Label(root, text = time_text, font=(text_font, text_size),bg=bgcolour[theme],
                                   fg=fgcolour[theme]).grid(row = 10, column = 0, columnspan = 2)
    no_results_text = str(len(match_list)) + ' matches found'
    no_results_label = tk.Label(root, text = no_results_text, font=(text_font, text_size),bg=bgcolour[theme],
                                fg=fgcolour[theme]).grid(row = 10, column = 2, columnspan = 2)

    results_text = scrolledtext.ScrolledText(root, font=(text_font, text_size),bg=bgcolour[theme],fg=fgcolour[theme],
                             wrap = 'word')
    font_in_use = tkfont.Font(font=results_text['font'])
    tab_width = font_in_use.measure('M' * (max_len + 2))
    print(tab_width)
    results_text.config(tabs=(tab_width,))
    results_text.grid(row = 12, column = 0, columnspan = 4)
    results_text.delete(1.0)
    results_text.insert(1.0,match_list)


root = tk.Tk()

word_list, load_message = load_list(word_file)
print(load_message)
root.title('Regex-based Word Search')
root['bg'] = bgcolour[theme]
root.geometry('%dx%d+%d+%d' % (winwidth, winheight, winx, winy))
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
load_message_label = tk.Label(root, text = load_message, font=(text_font, text_size),bg=bgcolour[theme],fg=fgcolour[theme])\
    .grid(row = 0, sticky='wn', column = 0, columnspan =3, padx=paddingh, pady=paddingv)
prompt = tk.Label(root, text = 'Enter Regex query: ', font=(text_font, text_size),bg=bgcolour[theme],fg=fgcolour[theme])\
    .grid(row = 1, column = 0, padx=paddingh, pady=paddingv)
input_query = tk.StringVar()
query_entry = tk.Entry(root, textvariable = input_query, font=(text_font, text_size),bg=bgcolour[theme],
                       fg=fgcolour[theme]).grid(row = 1, column = 1, columnspan = 2)
enter_button = tk.Button(root, text="Go", font=(text_font, text_size), bg=buttonbg[theme], fg=fgcolour[theme],
                           command= go).grid(row=1, column = 3, padx=paddingh, pady=paddingv)
min_length_label = tk.Label(root, text = 'Minimum length: ', font=(text_font, text_size),bg=bgcolour[theme],fg=fgcolour[theme])\
    .grid(row = 2, column = 0, padx=paddingh, pady=paddingv)
min_length = tk.StringVar()
min_length.set(3)
min_length_entry = tk.Entry(root, textvariable = min_length, font=(text_font, text_size),bg=bgcolour[theme],
                       fg=fgcolour[theme]).grid(row = 2, column = 1, padx=paddingh, pady=paddingv)
max_length_label = tk.Label(root, text = 'Maximum length: ', font=(text_font, text_size),bg=bgcolour[theme],fg=fgcolour[theme])\
    .grid(row = 2, column = 2, padx=paddingh, pady=paddingv)
max_length = tk.StringVar()
max_length.set(12)
max_length_entry = tk.Entry(root, textvariable = max_length, font=(text_font, text_size),bg=bgcolour[theme],
                       fg=fgcolour[theme]).grid(row = 2, column = 3, padx=paddingh, pady=paddingv)
hint_label = tk.Label(root, text = hint_text, font=(text_font, text_size-2 ),bg=bgcolour[theme],fg=fgcolour[theme])\
    .grid(row = 3, sticky='wn', column = 0, columnspan =4, padx=paddingh, pady=paddingv)


root.mainloop()
