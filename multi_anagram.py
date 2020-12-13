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
hover_tip = []
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


def get_letter_counts(letters):
    counts = {}
    for letter in letters:
        if letter in counts:
            counts[letter] += 1
        else:
            counts[letter] = 1
    return counts


def get_spares(residual_dict):
    for ltr in residual_dict:
        if residual_dict(ltr) > 0:
            spares = spares + ltr * residual_dict(ltr)


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
    letter_list = input_query.get()
    ignore_punct = ignore_punctuation.get()
    case_sensitivity = case_sensitive.get()
    if not case_sensitivity:
        letter_list = letter_list.lower()
    query_letter_counts = get_letter_counts(letter_list)
    word_lengths_text = input_query_2.get()
    word_lengths_str = word_lengths_text.split(',')
    word_lengths = []
    for w_l in word_lengths_str:
        word_lengths.append(int(w_l))
    word_lengths.sort(reverse=True)
    if len(word_lengths) > 4:
        error_message = 'Too many words, max 4.  '
    else:
        while len(word_lengths) < 4:
            word_lengths.append(0)
    if sum(word_lengths) > len(letter_list):
        error_message = error_message + 'Not enough letters.'
    if error_message == '':
        i = 0
        while i < len(words_by_length[word_lengths[0]]):
#            print('l0 trying: ', words_by_length[word_lengths[0]][i], query_letter_counts)
            possible_0, rd_0 = is_possible(words_by_length[word_lengths[0]][i], query_letter_counts)
#            print('lo answer: ', possible_0, rd_0)
            if possible_0:
                m_0 = words_by_length[word_lengths[0]][i]
                if word_lengths[1] == word_lengths[0]:
                    j = i
                else:
                    j = 0
#                print('m_o =', m_0, str(j), rd_0)
                while j < len(words_by_length[word_lengths[1]]):
#                    print(m_0, 'l1 trying: ', words_by_length[word_lengths[1]][i], rd_0)
                    possible_1, rd_1 = is_possible(words_by_length[word_lengths[1]][j], rd_0)
#                    print(m_0, j, 'l1 answer: ', possible_1, rd_1)
                    if possible_1:
                        m_1 = words_by_length[word_lengths[1]][j]
                        if word_lengths[2] > 0:
                            if word_lengths[2] == word_lengths[1]:
                                k = j
                            else:
                                k = 0
                            while k < len(words_by_length[word_lengths[2]]):
    #                            print('l2 trying: ', words_by_length[word_lengths[2]][i], rd_1)
                                possible_2, rd_2 = is_possible(words_by_length[word_lengths[2]][k], rd_1)
    #                            print('l2 answer: ', possible_2, rd_1)
                                if possible_2:
                                    m_2 = words_by_length[word_lengths[1]][k]
                                    if word_lengths[3] > 0:
                                        if word_lengths[3] == word_lengths[2]:
                                            l = k
                                        else:
                                            l = 0
                                        while l < len(words_by_length[word_lengths[3]]):
                                            possible_3, rd_3 = is_possible(words_by_length[word_lengths[3]][l], rd_2)
                                            if possible_3:
                                                m_3 = words_by_length[word_lengths[3]][l]
                                                print(m_0, m_1, m_2, m_3)
                                                match_list.append([m_0, m_1, m_2, m_3])
                                            l += 1
                                    else:
                                        match_list.append([m_0, m_1, m_2])
                                k += 1
                        else:
                            match_list.append([m_0,m_1])
                    j += 1
            i += 1
        print(match_list)
    else:
        print(error_message)
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
words_by_length = split_words_by_length(word_list)
print(load_message)
root.title('Multiword Anagram Search')
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
prompt_1 = tk.Label(root, text='Enter list of letters: ', font=(text_font, text_size), bg=bgcolour[theme],
                    fg=fgcolour[theme])
prompt_1.grid(row=1, column=0, padx=paddingh, pady=paddingv)
prompt_2 = tk.Label(root, text='Enter lengths of words separated by commas: ', font=(text_font, text_size),
                    bg=bgcolour[theme], fg=fgcolour[theme])
prompt_2.grid(row=2, column=0, padx=paddingh, pady=paddingv)
input_query = tk.StringVar()
query_entry = tk.Entry(root, textvariable=input_query, font=(text_font, text_size), bg=bgcolour[theme],
                       fg=fgcolour[theme])
query_entry.grid(row=1, column=1, columnspan=2, sticky='ew')
query_entry.bind('<Return>', go_enter)
input_query_2 = tk.StringVar()
query_entry_2 = tk.Entry(root, textvariable=input_query_2, font=(text_font, text_size), bg=bgcolour[theme],
                         fg=fgcolour[theme])
query_entry_2.grid(row=2, column=1, columnspan=2, sticky='ew')
query_entry_2.bind('<Return>', go_enter)
enter_button = tk.Button(root, text="Go", font=(text_font, text_size), bg=buttonbg[theme], fg=fgcolour[theme],
                         command=go).grid(row=1, column=3, padx=paddingh, pady=paddingv, sticky='ew')


root.mainloop()
