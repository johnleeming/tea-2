import os
import re
import subprocess
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import logging
from idlelib import tooltip

home_path =  os.path.expanduser('~/')
word_file = home_path + 'word_lists/wlist_match3.txt'
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
log_file = home_path + 'logs/tea-2' + datetime.now().strftime('%y-%m-%d') + '.txt'
logging.basicConfig(filename=log_file,level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
punctuation = {33: None, 34: None, 39: None, 40: None, 41: None, 42: None, 44: None, 45: None, 58: None, 59: None,
               94: None, 95: None, 96: None }


def choose_list():
    global word_list, load_message
    in_file_name =  filedialog.askopenfilename(initialdir =home_path + 'word_lists/', title ="Select wordlist",
                                               filetypes = (("Text files","*.txt"),("all files","*.*")))
    word_list, load_message = load_list(in_file_name)
    load_button_message.set(load_message)
    return


def load_list(filename):
    temp_list = []
    with open (filename, 'r') as input_file:
        for line in input_file:
            temp_list.append(line[:-1])
    load_message = 'Using ' + os.path.basename(filename) + ' containing ' + str(len(temp_list)) + ' words.'
    return(temp_list, load_message)


def find_matches(query, list, min, max, ignore_punct):
    start_time = datetime.now()
    matches = []
    no_matches = 0
    if ignore_punct:
        for i in list:
            j = i.translate(punctuation)
            if query.match(j) and min <= len(j) <= max:
                matches.append(i)
                no_matches += 1
    else:
        for i in list:
            if query.match(i) and min <= len(i) <= max:
                matches.append(i)
                no_matches += 1
    end_time = datetime.now()
    time_taken = end_time - start_time
    return(matches, no_matches, time_taken)


def display_results(matches, first):
    match_word = []
    match_tip = []
    tip_text = []
    if len(matches) - first < 39:
        last = len(matches)-1
    else:
        last = first + 39
    i = 0
    while i <= last - first:
        column_no = int(i/10)
        row_no = 20+ i - column_no * 10
        match_word.append(tk.Label(root,text = matches[first + i], font=(text_font, text_size),bg=bgcolour[theme],
                                   fg=fgcolour[theme], justify=LEFT))
        match_word[i].grid(row=row_no, column = column_no, sticky='ew')
        tip_text.append(get_definition(matches[first + i]))
#        match_tip.append(tooltip.Hovertip(match_word[i],tip_text[i]))
        tooltip.Hovertip(match_word[i], tip_text[i])
        i +=1


def get_definition(word):
    try:
        response = subprocess.run('dict',word,)
        definition = response.stdout()
        print(response.stderr())
    except:
        logging.error('dict lookup failed ')
        definition = 'Lookup failed'
    return definition


def go():
    query = input_query.get()
    min_len = min_length.get()
    max_len = max_length.get()
    ignore_punct = ignore_punctuation.get()
    error_state = tk.StringVar()
    error_label = tk.Label(root, textvar=error_state, font=(text_font, text_size), bg=bgcolour[theme],
                           fg='red').grid(row=1, column=2, sticky='ew')
    try:
        error_state.set(' ')
        re_query = re.compile(query)
        match_list, no_matches, search_time = find_matches(re_query, word_list, min_len, max_len, ignore_punct)
        time_text = 'search took: ' + str(search_time.total_seconds()) + ' seconds'
        solution_time_label = tk.Label(root, text = time_text, font=(text_font, text_size),bg=bgcolour[theme],
                                       fg=fgcolour[theme]).grid(row = 10, column = 0, columnspan = 2, sticky='ew')
        no_results_text = str(no_matches) + ' matches found'
        if no_matches > 40:
            no_results_text += ' (first 40 displayed)'
        no_results_label = tk.Label(root, text = no_results_text, font=(text_font, text_size),bg=bgcolour[theme],
                                    fg=fgcolour[theme]).grid(row = 10, column = 2, columnspan = 2, sticky='ew')
        display_results(match_list,0)
    except:
        logging.exception('regex error: '+ query)
        error_state.set('Not valid REGEX')



root = tk.Tk()

word_list, load_message = load_list(word_file)
print(load_message)
root.title('Regex-based Word Search')
root['bg'] = bgcolour[theme]
root.geometry('%dx%d+%d+%d' % (winwidth, winheight, winx, winy))
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
load_button_message = tk.StringVar()
load_button_message.set(load_message)
load_message_button = tk.Button(root, textvar = load_button_message, font=(text_font, text_size),bg=buttonbg[theme],
                                fg=fgcolour[theme], command = choose_list)
load_message_button.grid(row = 0, sticky='wn', column = 0, columnspan =3,padx=paddingh, pady=paddingv)
ignore_punctuation = tk.BooleanVar()
punctuation_checkbox = tk.Checkbutton(root,text = 'Ignore Punctuation',variable = ignore_punctuation, onvalue = True,
                                      offvalue = False,font=(text_font, text_size),bg=bgcolour[theme],fg=fgcolour[theme])
punctuation_checkbox.grid(row = 0, sticky='wn', column = 3, padx=paddingh, pady=paddingv)
prompt = tk.Label(root, text = 'Enter Regex query: ', font=(text_font, text_size),bg=bgcolour[theme],fg=fgcolour[theme])\
    .grid(row = 1, column = 0, padx=paddingh, pady=paddingv)
input_query = tk.StringVar()
query_entry = tk.Entry(root, textvariable = input_query, font=(text_font, text_size),bg=bgcolour[theme],
                       fg=fgcolour[theme]).grid(row = 1, column = 1, sticky='ew')
enter_button = tk.Button(root, text="Go", font=(text_font, text_size), bg=buttonbg[theme], fg=fgcolour[theme],
                           command= go).grid(row=1, column = 3, padx=paddingh, pady=paddingv, sticky='ew')
min_length_label = tk.Label(root, text = 'Minimum length: ', font=(text_font, text_size),bg=bgcolour[theme],fg=fgcolour[theme])\
    .grid(row = 2, column = 0, padx=paddingh, pady=paddingv, sticky='ew')
min_length = tk.IntVar()
min_length.set(3)
min_length_entry = tk.Entry(root, textvariable = min_length, font=(text_font, text_size),bg=bgcolour[theme],
                       fg=fgcolour[theme]).grid(row = 2, column = 1, padx=paddingh, pady=paddingv, sticky='ew')
max_length_label = tk.Label(root, text = 'Maximum length: ', font=(text_font, text_size),bg=bgcolour[theme],fg=fgcolour[theme])\
    .grid(row = 2, column = 2, padx=paddingh, pady=paddingv, sticky='ew')
max_length = tk.IntVar()
max_length.set(12)
max_length_entry = tk.Entry(root, textvariable = max_length, font=(text_font, text_size),bg=bgcolour[theme],
                       fg=fgcolour[theme]).grid(row = 2, column = 3, padx=paddingh, pady=paddingv, sticky='ew')
hint_label = tk.Label(root, text = hint_text, font=(text_font, text_size-2 ),bg=bgcolour[theme],fg=fgcolour[theme])\
    .grid(row = 3, sticky='wn', column = 0, columnspan =4, padx=paddingh, pady=paddingv)


root.mainloop()
