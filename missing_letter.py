import os
import re
import subprocess
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import *
from datetime import datetime
import logging

home_path = os.path.expanduser('~/')
word_file = home_path + 'word_lists/default.txt'
text_font = "liberation sans"
text_size = 16
bgcolour = {'dark': 'black', 'light': 'white', 'alarm': 'red'}
fgcolour = {'dark': 'white', 'light': 'black', 'alarm': 'black'}
buttonbg = {'dark': 'darkgrey', 'light': 'lightgrey', 'alarm': 'darkgrey'}
theme = 'light'
winheight = 180
winwidth = 1000
rwinheight = 680
winx = 100
winy = 50
rwiny = winy + winheight + 40
paddingh = 5
paddingv = 5
log_file = home_path + 'logs/misprints.log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
punctuation = {33: None, 34: None, 39: None, 40: None, 41: None, 42: None, 44: None, 45: None, 58: None, 59: None,
               94: None, 95: None, 96: None}
match_word = []
match_list = []
is_error = False


def choose_list():
    global word_list, load_message
    in_file_name = filedialog.askopenfilename(initialdir=home_path + 'word_lists/', title="Select wordlist",
                                              filetypes=(("Text files", "*.txt"), ("all files", "*.*")))
    word_list, load_message = load_list(in_file_name)
    load_button_message.set(load_message)
    return


def load_list(filename):
    temp_list = []
    with open(filename, 'r') as input_file:
        for line in input_file:
            temp_list.append(line[:-1])
    load_message = 'Using ' + os.path.basename(filename) + ' (' + str(len(temp_list)) + ' words).'
    return temp_list, load_message


def find_matches(query, q_len, o_w, list, ignore_punct, case_sense):
    start_time = datetime.now()
    matches = []
    for i in list:
        if len(i) == q_len and i != o_w:
            j = i
            if ignore_punct:
                j = j.translate(punctuation)
            if not case_sense:
                j = j.lower()
            if query.match(j) and i not in matches:
                matches.append(i)
    end_time = datetime.now()
    time_taken = (end_time - start_time).total_seconds()
    return matches, time_taken


def display_results(matches, first, time_text, no_results_text):
    global match_word, definition_box, results_window
    results_window = tk.Toplevel()
    results_window.title('Results')
    results_window['bg'] = bgcolour[theme]
    results_window.geometry('%dx%d+%d+%d' % (winwidth, rwinheight, winx, rwiny))
    results_window.grid_columnconfigure(0, weight=1)
    results_window.grid_columnconfigure(1, weight=1)
    results_window.grid_columnconfigure(2, weight=1)
    results_window.grid_columnconfigure(3, weight=1)
    solution_time_label = tk.Label(results_window, text=time_text, font=(text_font, text_size), bg=bgcolour[theme],
                                   fg=fgcolour[theme]).grid(row=10, column=0, columnspan=2, sticky='ew')
    no_results_label = tk.Label(results_window, text=no_results_text, font=(text_font, text_size), bg=bgcolour[theme],
                                fg=fgcolour[theme]).grid(row=10, column=2, columnspan=2, sticky='ew')
    definition_box = scrolledtext.ScrolledText(results_window, background=bgcolour[theme], relief=SOLID, borderwidth=1,
                                               font=(text_font, text_size - 2), fg=fgcolour[theme], wrap='word',
                                               height=12)
    definition_box.grid(row=50, column=0, columnspan=4)
    i = 0
    while i > len(match_word):
        match_word[i].grid_forget()
        i += 1
    match_word.clear()
    root.update()
    match_tip = []
    if len(match_list) - first < 39:
        last = len(match_list) - 1
    else:
        last = first + 39
    i = 0
    while i <= last - first:
        column_no = int(i / 10)
        row_no = 20 + i - column_no * 10
        match_word.append(tk.Button(results_window, text=matches[first + i], font=(text_font, text_size - 1),
                                    command=lambda b=i: toggle(b)))
        match_word[i].configure(anchor='w', relief='raised')
        match_word[i].grid(row=row_no, column=column_no, sticky='ew')
        i += 1


def get_definition(word):
    try:
        response = subprocess.run(['dict', word, ], capture_output=True)
        if len(response.stdout) > 0:
            definition = response.stdout
        else:
            definition = 'No definitions found.'
        logging.debug(response.stderr)
    except Exception:
        definition = 'Lookup failed'
        logging.info(response.stderr)
    return definition


def go_enter(event):
    go()


def go():
    global match_list, results_window
    try:
        results_window.destroy()
    except Exception:
        pass
    try:
        error_window.destroy()
    except Exception:
        pass
    start_no = 0
    search_time = 0
    match_list = []
    o_word = input_query.get()
    ignore_punct = ignore_punctuation.get()
    case_sensitivity = case_sensitive.get()
    if not case_sensitivity:
        o_word = o_word.lower()
    i = 0
    query_word_length = len(o_word) + 1
    while i < query_word_length:
        if i == 0:
            t_q = '.' + o_word
        elif i == query_word_length:
            t_q = o_word + '.'
        else:
            t_q = o_word[:i] + '.' + o_word[i:]
        try:
            re_query = re.compile(t_q)
            t_match_list, t_search_time = find_matches(re_query, query_word_length, o_word, word_list,
                                                       ignore_punct, case_sensitivity)
            for w in t_match_list:
                if w not in match_list:
                    match_list.append(w)
            search_time += t_search_time
        except re.error as error_message:
            error_state = tk.StringVar()
            error_window = tk.Toplevel()
            error_window.title('Regex Error')
            error_window['bg'] = bgcolour[theme]
            error_window.geometry('%dx%d+%d+%d' % (winwidth / 4, winheight, winx + winwidth, winy))
            error_label = tk.Label(error_window, textvar=error_state, font=(text_font, text_size), bg=bgcolour[theme],
                                   fg='red', wraplength=(winwidth / 4 - 10)).pack()
            logging.exception('regex error: ' + o_word)
            error_str = str(error_message)
            error_state.set(error_str)
        except Exception:
            error_state = tk.StringVar()
            error_window = tk.Toplevel()
            error_window.title('Regex Error')
            error_window['bg'] = bgcolour[theme]
            error_window.geometry('%dx%d+%d+%d' % (winwidth / 4, winheight, winx + winwidth, winy))
            error_label = tk.Label(error_window, textvar=error_state, font=(text_font, text_size), bg=bgcolour[theme],
                                   fg='red', wraplength=(winwidth / 4 - 10)).pack()
            logging.exception('other error')
            error_state.set('something else went wrong')
        i += 1
    time_text = 'search took: ' + str(round(search_time, 3)) + ' seconds'
    match_list.sort()
    no_results_text = str(len(match_list)) + ' matches found'
    if len(match_list) > 40:
        no_results_text += ' (first 40 displayed)'
    display_results(match_list, start_no, time_text, no_results_text)


def toggle(button_no):
    global match_word, definition_box
    definition_box.delete(1.0, END)
    if match_word[button_no].config('relief')[-1] == 'raised':
        match_word[button_no].config(relief="sunken")
        definition_text = get_definition(match_list[button_no])
        definition_box.insert(1.0, definition_text)
        i = 0
        while i < len(match_word):
            if i != button_no and match_word[i].config('relief')[-1] == 'sunken':
                match_word[i].config(relief='raised')
            i += 1
    else:
        print('sunken')
        match_word[button_no].config(relief="raised")


root = tk.Tk()

word_list, load_message = load_list(word_file)
print(load_message)
root.title('Missing letter')
root['bg'] = bgcolour[theme]
root.geometry('%dx%d+%d+%d' % (winwidth, winheight, winx, winy))
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)
load_button_message = tk.StringVar()
load_button_message.set(load_message)
load_message_button = tk.Button(root, textvar=load_button_message, font=(text_font, text_size - 1), bg=buttonbg[theme],
                                fg=fgcolour[theme], command=choose_list)
load_message_button.grid(row=0, sticky='wn', column=0, columnspan=2, padx=paddingh, pady=paddingv)
ignore_punctuation = tk.BooleanVar()
punctuation_checkbox = tk.Checkbutton(root, text='Ignore Punctuation', variable=ignore_punctuation, onvalue=True,
                                      offvalue=False, font=(text_font, text_size), bg=bgcolour[theme],
                                      fg=fgcolour[theme])
punctuation_checkbox.grid(row=0, sticky='wn', column=3, padx=paddingh, pady=paddingv)
case_sensitive = tk.BooleanVar()
case_sensitive_checkbox = tk.Checkbutton(root, text='Case Sensitive', variable=case_sensitive, onvalue=True,
                                         offvalue=False, font=(text_font, text_size), bg=bgcolour[theme],
                                         fg=fgcolour[theme])
case_sensitive_checkbox.grid(row=0, sticky='wn', column=2, padx=paddingh, pady=paddingv)
prompt = tk.Label(root, text='Enter word with missing letter: ', font=(text_font, text_size), bg=bgcolour[theme],
                  fg=fgcolour[theme])
prompt.grid(row=1, column=0, padx=paddingh, pady=paddingv)
input_query = tk.StringVar()
query_entry = tk.Entry(root, textvariable=input_query, font=(text_font, text_size), bg=bgcolour[theme],
                       fg=fgcolour[theme])
query_entry.grid(row=1, column=1, columnspan=2, sticky='ew')
query_entry.bind('<Return>', go_enter)
enter_button = tk.Button(root, text="Go", font=(text_font, text_size), bg=buttonbg[theme], fg=fgcolour[theme],
                         command=go).grid(row=1, column=3, padx=paddingh, pady=paddingv, sticky='ew')


root.mainloop()