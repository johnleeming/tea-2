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
log_file = home_path + 'logs/consecutive_jumble.log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
output_file = home_path + 'answers.txt'
punctuation = {33: None, 34: None, 39: None, 40: None, 41: None, 42: None, 44: None, 45: None, 58: None, 59: None,
               94: None, 95: None, 96: None}
match_word = []
match_list = []
is_error = False


def choose_list():
    global word_list, load_message, words_by_length
    in_file_name = filedialog.askopenfilename(initialdir=home_path + 'word_lists/', title="Select wordlist",
                                              filetypes=(("Text files", "*.txt"), ("all files", "*.*")))
    word_list, load_message = load_list(in_file_name)
    words_by_length = split_words_by_length(word_list)
    load_button_message.set(load_message)
    return


def load_list(filename):
    temp_list = []
    with open(filename, 'r') as input_file:
        for line in input_file:
            temp_list.append(line[:-1].lower())
    load_message = 'Using ' + os.path.basename(filename) + ' (' + str(len(temp_list)) + ' words).'
    return temp_list, load_message


def split_words_by_length(words):
    word_lists_by_length = {}
    for word in words:
        t_l = len(word)
        if t_l in word_lists_by_length:
            word_lists_by_length[t_l].append(word)
        else:
            word_lists_by_length[t_l] = [word]
    return word_lists_by_length


def is_possible(w, l_dict):
    temp_letter_counts = l_dict.copy()
    poss = True
    i = 0
    while i < len(w):
        let = w[i]
        if let not in temp_letter_counts:
            poss = False
        else:
            if temp_letter_counts[let] == 0:
                poss = False
            temp_letter_counts[let] -= 1
        if not poss:
            break
        i += 1
    if poss:
        return_dict = temp_letter_counts.copy()
    else:
        return_dict = l_dict.copy()
    return poss, return_dict


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
                                   fg=fgcolour[theme])
    solution_time_label.grid(row=10, column=0, columnspan=2, sticky='ew')
    no_results_label = tk.Label(results_window, text=no_results_text, font=(text_font, text_size), bg=bgcolour[theme],
                                fg=fgcolour[theme])
    no_results_label.grid(row=10, column=2, columnspan=2, sticky='ew')
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


def get_letter_counts(letters):
    counts = {}
    for letter in letters:
        if letter in counts:
            counts[letter] += 1
        else:
            counts[letter] = 1
    return counts


def get_spares(residual_dict):
    spares = '('
    for ltr in residual_dict:
        if residual_dict[ltr] > 0:
            spares = spares + ltr * residual_dict[ltr]
    spares = spares + ')'
    return spares


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
    error_message = ''
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
    letter_sequence = input_query.get()
    ignore_punct = ignore_punctuation.get()
    case_sensitivity = case_sensitive.get()
    if not case_sensitivity:
        letter_sequence = letter_sequence.lower()
    word_len = word_length.get()
    if word_len > len(letter_sequence):
        error_message = error_message + 'Not enough letters.'
    if error_message == '':
        ###
        print(match_list)
    else:
        print(error_message)
    time_text = 'search took: ' + str(round(search_time, 3)) + ' seconds'
    match_list.sort()
    no_results_text = str(len(match_list)) + ' matches found'
    if len(match_list) > 40:
        no_results_text += ' (first 40 displayed)'
    if len(match_list) > 0:
        with open(output_file, 'w') as out:
            for n in match_list:
                out.writelines(str(n) + '\n')
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
words_by_length = split_words_by_length(word_list)
print(load_message)
root.title('Search for hidden consecutive jumble')
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
prompt_1 = tk.Label(root, text='Enter sequence of letters: ', font=(text_font, text_size), bg=bgcolour[theme],
                    fg=fgcolour[theme])
prompt_1.grid(row=1, column=0, padx=paddingh, pady=paddingv)
prompt_2 = tk.Label(root, text='Enter length of word to be found: ', font=(text_font, text_size),
                    bg=bgcolour[theme], fg=fgcolour[theme])
prompt_2.grid(row=2, column=0, padx=paddingh, pady=paddingv)
input_query = tk.StringVar()
query_entry = tk.Entry(root, textvariable=input_query, font=(text_font, text_size), bg=bgcolour[theme],
                       fg=fgcolour[theme])
query_entry.grid(row=1, column=1, columnspan=2, sticky='ew')
query_entry.bind('<Return>', go_enter)
word_length = tk.IntVar()
word_length_entry = tk.Entry(root, textvariable=word_length, font=(text_font, text_size), bg=bgcolour[theme],
                             fg=fgcolour[theme])
word_length_entry.grid(row=2, column=1, columnspan=2, sticky='ew')
word_length_entry.bind('<Return>', go_enter)
enter_button = tk.Button(root, text="Go", font=(text_font, text_size), bg=buttonbg[theme], fg=fgcolour[theme],
                         command=go).grid(row=1, column=3, padx=paddingh, pady=paddingv, sticky='ew')


root.mainloop()
