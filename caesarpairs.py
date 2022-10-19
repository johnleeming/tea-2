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
text_size = 14
bgcolour = {'dark': 'black', 'light': 'white', 'alarm': 'red'}
fgcolour = {'dark': 'white', 'light': 'black', 'alarm': 'black'}
buttonbg = {'dark': 'darkgrey', 'light': 'lightgrey', 'alarm': 'darkgrey'}
theme = 'light'
winheight = 15 * text_size + 20
winwidth = 1000
rwinheight = 850 - winheight
winx = 100
winy = 0
rwiny = winy + winheight + 65
paddingh = 5
paddingv = 5
hint_text = "[abc] - one of the listed letters | . any character | * 0 or more | + 1 or more | ? optional | " \
            "(a|b) a or b | ^ beginning | $ end "
log_file = home_path + 'logs/tea-2.log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
punctuation = {33: None, 34: None, 39: None, 40: None, 41: None, 42: None, 44: None, 45: None, 58: None, 59: None,
               94: None, 95: None, 96: None}
match_word = []
match_list = []
is_error = False

greek_character_names = []
with open(home_path + 'tea-2/greek_characters.txt', 'r') as i_file:
    for line in i_file:
        greek_character_names.append(line[:-1])


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
    temp_list.sort(key=lambda x: x.lower())
    return temp_list, load_message


def check_word(list, word):
    try:
        ind = list.index(word)
    except Exception:
        ind = -1
    return ind


def contains_greek_character(w):
    for gr_ch in greek_character_names:
        if gr_ch in w:
            return True
    return False


def find_matches(query, list, min, max, ignore_punct, case_sense, start, end, n_words, c_gr_ch):
    start_time = datetime.now()
    matches = []
    no_matches = 0
    if start == -1:  # if nothing entered in start field, start from beginning
        start = 0
    if end == -1:  # if nothing entered in end field continue to end
        end = len(list)
    k = start
    while k < end:
        i = list[k]
        j = i
        if ignore_punct:
            j = j.translate(punctuation)
        if not case_sense:
            j = j.lower()
        words_in_i = i.count(' ') + 1
        if query.match(j) and (min <= len(j) <= max):
            if words_in_i == int(n_words):
                if c_gr_ch:
                    if contains_greek_character(j):
                        matches.append(i)
                        no_matches += 1
                else:
                    matches.append(i)
                    no_matches += 1
        k += 1
    end_time = datetime.now()
    time_taken = end_time - start_time
    return matches, no_matches, time_taken


def find_pairs(word, list):
    l_word = word.lower()
    l_word = l_word.translate(punctuation)
    test_word = ""
    pairs = []
    for i in range(1,25):
        for c in l_word:
            j = ord(c)- 96 + i
            if j > 26:
                j = j - 26
            test_word += chr(j + 96)
        if test_word in list:
            pairs.append(test_word)
    return pairs


def display_results(matches, no_matches, first, time_text, no_results_text):
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
                                               height=12, width=100)
    definition_box.grid(row=50, column=0, columnspan=4)
    i = 0
    while i > len(match_word):
        match_word[i].grid_forget()
        i += 1
    match_word.clear()
    root.update()
    if no_matches - first < 39:
        last = no_matches - 1
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


def display_error(error_message):
    global error_window
    error_state = tk.StringVar()
    error_window = tk.Toplevel()
    error_window.title('Error')
    error_window['bg'] = bgcolour[theme]
    error_window.geometry('%dx%d+%d+%d' % (winwidth / 4, winheight, winx + winwidth, winy))
    error_label = tk.Label(error_window, textvar=error_state, font=(text_font, text_size), bg=bgcolour[theme],
                           fg='red', wraplength=(winwidth / 4 - 10)).pack()
    logging.exception(error_message)
    error_state.set(error_message)


def display_history(hist):
    global history_window
    hist_list = ''
    for h in hist:
        hist_list += h[0] + ' (' + h[1] +')' + '\n'
    history_window = tk.Toplevel()
    history_window.title('Query History')
    history_window['bg'] = bgcolour[theme]
    history_window.geometry('%dx%d+%d+%d' % (winwidth / 2, winheight, winx + winwidth, winy))
    history_box = scrolledtext.ScrolledText(history_window, background=bgcolour[theme], relief=SOLID, borderwidth=1,
                                            font=(text_font, text_size - 2), fg=fgcolour[theme], wrap='word',
                                            height=12, width=int(winwidth / 20))
    history_box.grid(row=50, column=0, columnspan=4)
    history_box.insert(1.0, hist_list)


def go_enter(event):
    go()


def go():
    start_no = 0
    global match_list, results_window, error_window, history, history_window
    try:
        history_window.destroy()
    except Exception:
        pass
    try:
        results_window.destroy()
    except Exception:
        pass
    try:
        error_window.destroy()
    except Exception:
        pass
    query = input_query.get()
    min_len = min_length.get()
    max_len = max_length.get()
    a_start = alpha_start.get()
    start_ind = check_word(word_list, a_start)
    n_words = num_words.get()
    if a_start != '' and start_ind == -1:
        display_error('Start word not in list, will start from beginning.')
    a_end = alpha_end.get()
    end_ind = check_word(word_list, a_end)
    if a_end != '' and end_ind == -1:
        display_error('End word not in list, will continue to end.')
    ignore_punct = ignore_punctuation.get()
    case_sensitivity = case_sensitive.get()
    contains_gr_ch = contains_greek_char.get()
    if not case_sensitivity:
        query = query.lower()
    try:
        re_query = re.compile(query)
        match_list, no_matches, search_time = find_matches(re_query, word_list, min_len, max_len, ignore_punct,
                                                           case_sensitivity, start_ind, end_ind, n_words,
                                                           contains_gr_ch)
        time_text = 'search took: ' + str(search_time.total_seconds()) + ' seconds'
        no_results_text = str(no_matches) + ' matches found'
        if no_matches > 40:
            no_results_text += ' (first 40 displayed)'
        match_list.sort()
        display_results(match_list, no_matches, start_no, time_text, no_results_text)
        result_str = str(no_matches)
    except re.error as error_message:
        display_error(error_message)
        result_str = 'Regex Error'
    except Exception:
        display_error('Something went wrong.')
        result_str = 'Other Error'
    history.append([query, result_str])
    display_history(history)


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
        match_word[button_no].config(relief="raised")


def end_prog(event):
    root.quit()


root = tk.Tk()

word_list, load_message = load_list(word_file)
history = []

root.title('Regex-based Word Search')
root['bg'] = bgcolour[theme]
root.geometry('%dx%d+%d+%d' % (winwidth, winheight, winx, winy))
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)

prompt = tk.Label(root, text='Enter Regex query: ', font=(text_font, text_size), bg=bgcolour[theme], fg=fgcolour[theme])
prompt.grid(row=0, column=0, padx=paddingh, pady=paddingv)
input_query = tk.StringVar()
query_entry = tk.Entry(root, textvariable=input_query, font=(text_font, text_size), bg=bgcolour[theme],
                       fg=fgcolour[theme])
query_entry.grid(row=0, column=1, columnspan=3, sticky='ew')
query_entry.focus()
hint_label = tk.Label(root, text=hint_text, font=(text_font, text_size - 2), bg=bgcolour[theme], fg=fgcolour[theme])
hint_label.grid(row=1, sticky='en', column=0, columnspan=4, padx=paddingh, pady=paddingv)

load_button_message = tk.StringVar()
load_button_message.set(load_message)
load_message_button = tk.Button(root, textvar=load_button_message, font=(text_font, text_size - 1), bg=buttonbg[theme],
                                fg=fgcolour[theme], command=choose_list)
load_message_button.grid(row=2, sticky='wn', column=0, columnspan=2, padx=paddingh, pady=paddingv)

case_sensitive = tk.BooleanVar()
case_sensitive_checkbox = tk.Checkbutton(root, text='Case Sensitive', variable=case_sensitive, onvalue=True,
                                         offvalue=False, font=(text_font, text_size), bg=bgcolour[theme],
                                         fg=fgcolour[theme])
case_sensitive_checkbox.grid(row=2, sticky='wn', column=2, padx=paddingh, pady=paddingv)

ignore_punctuation = tk.BooleanVar()
punctuation_checkbox = tk.Checkbutton(root, text='Ignore Punctuation', variable=ignore_punctuation, onvalue=True,
                                      offvalue=False, font=(text_font, text_size), bg=bgcolour[theme],
                                      fg=fgcolour[theme])
punctuation_checkbox.grid(row=2, sticky='wn', column=3, padx=paddingh, pady=paddingv)
punctuation_checkbox.select()

min_length_label = tk.Label(root, text='Minimum length: ', font=(text_font, text_size), bg=bgcolour[theme],
                            fg=fgcolour[theme])
min_length_label.grid(row=4, column=0, padx=paddingh, pady=paddingv, sticky='ew')
min_length = tk.IntVar()
min_length.set(3)
min_length_entry = tk.Entry(root, textvariable=min_length, font=(text_font, text_size), bg=bgcolour[theme],
                            fg=fgcolour[theme])
min_length_entry.grid(row=4, column=1, padx=paddingh, pady=paddingv, sticky='ew')

max_length_label = tk.Label(root, text='Maximum length: ', font=(text_font, text_size), bg=bgcolour[theme],
                            fg=fgcolour[theme])
max_length_label.grid(row=4, column=2, padx=paddingh, pady=paddingv, sticky='ew')
max_length = tk.IntVar()
max_length.set(12)
max_length_entry = tk.Entry(root, textvariable=max_length, font=(text_font, text_size), bg=bgcolour[theme],
                            fg=fgcolour[theme])
max_length_entry.grid(row=4, column=3, padx=paddingh, pady=paddingv, sticky='ew')

alpha_start_label = tk.Label(root, text='Alphabetic start: ', font=(text_font, text_size), bg=bgcolour[theme],
                             fg=fgcolour[theme])
alpha_start_label.grid(row=5, column=0, padx=paddingh, pady=paddingv, sticky='ew')
alpha_start = tk.StringVar()
alpha_start_entry = tk.Entry(root, textvariable=alpha_start, font=(text_font, text_size), bg=bgcolour[theme],
                             fg=fgcolour[theme])
alpha_start_entry.grid(row=5, column=1, padx=paddingh, pady=paddingv, sticky='ew')
alpha_end_label = tk.Label(root, text='Alphabetic End: ', font=(text_font, text_size), bg=bgcolour[theme],
                           fg=fgcolour[theme])
alpha_end_label.grid(row=5, column=2, padx=paddingh, pady=paddingv, sticky='ew')
alpha_end = tk.StringVar()
alpha_end_entry = tk.Entry(root, textvariable=alpha_end, font=(text_font, text_size), bg=bgcolour[theme],
                           fg=fgcolour[theme])
alpha_end_entry.grid(row=5, column=3, padx=paddingh, pady=paddingv, sticky='ew')

num_words_label = tk.Label(root, text='Number of words:', font=(text_font, text_size), bg=bgcolour[theme],
                           fg=fgcolour[theme])
num_words_label.grid(row=6, column=0, padx=paddingh, pady=paddingv, sticky='ew')
num_words = tk.IntVar(value=1)
num_words = tk.Entry(root, textvariable=num_words, font=(text_font, text_size), bg=bgcolour[theme], fg=fgcolour[theme])
num_words.grid(row=6, column=1, padx=paddingh, pady=paddingv, sticky='ew')

contains_greek_char = tk.BooleanVar()
contains_greek_char_checkbox = tk.Checkbutton(root, text='Contains Greek', variable=contains_greek_char, onvalue=True,
                                              offvalue=False, font=(text_font, text_size), bg=bgcolour[theme],
                                              fg=fgcolour[theme])
contains_greek_char_checkbox.grid(row=6, sticky='wn', column=2, padx=paddingh, pady=paddingv)

enter_button = tk.Button(root, text="Go", font=(text_font, text_size), bg=buttonbg[theme], fg=fgcolour[theme],
                         command=go).grid(row=6, column=3, padx=paddingh, pady=paddingv, sticky='ew')
root.bind('<Return>', go_enter)
root.bind('<Escape>', end_prog)
root.mainloop()
