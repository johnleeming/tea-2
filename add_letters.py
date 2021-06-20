import os
import tkinter as tk
import logging

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
home_path = os.path.expanduser('~/')
log_file = home_path + 'logs/add_letters.log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
punctuation = {33: None, 34: None, 39: None, 40: None, 41: None, 42: None, 44: None, 45: None, 58: None, 59: None,
               94: None, 95: None, 96: None}


def add_letters(a, b):
    a_l = a.lower()
    b_l = b.lower()
    a_num = ord(a_l) - 96
    b_num = ord(b_l) - 96
    return chr(((a_num + b_num) % 26) + 96)


def display_results(s):
    global results_window
    results_window = tk.Toplevel()
    results_window.title('Result')
    results_window['bg'] = bgcolour[theme]
    results_window.geometry('%dx%d+%d+%d' % (winwidth, rwinheight, winx, rwiny))
    answer_label = tk.Label(results_window, text=s, font=(text_font, text_size), bg=bgcolour[theme],
                            fg=fgcolour[theme]).grid(row=10, column=0, columnspan=2, sticky='ew')


def go_enter(event):
    go()


def go():
    global results_window, error_window
    try:
        results_window.destroy()
    except Exception:
        pass
    try:
        error_window.destroy()
    except Exception:
        pass
    is_error = False
    error = ''
    let1 = input_let1.get().lower()
    let2 = input_let2.get().lower()
    if len(let1) > 1 or len(let2) > 1:
        error = 'One character only'
        is_error = True
    elif len(let1) == 0 or len(let2) == 0:
        error = 'Need a character in each box'
        is_error = True
    elif (1 > ord(let1) - 96 > 26) or (1 > ord(let2) - 96 > 26):
        error = 'No numbers or symbols'
        is_error = True
    if is_error:
        error_state = tk.StringVar()
        error_window = tk.Toplevel()
        error_window.title('Error')
        error_window['bg'] = bgcolour[theme]
        error_window.geometry('%dx%d+%d+%d' % (winwidth / 4, winheight, winx + winwidth, winy))
        error_label = tk.Label(error_window, textvar=error_state, font=(text_font, text_size), bg=bgcolour[theme],
                               fg='red', wraplength=(winwidth / 4 - 10)).pack()
        logging.exception('other error')
        error_state.set(error)
    else:
        display_results(add_letters(let1, let2))


root = tk.Tk()

root.title('Add Letters')
root['bg'] = bgcolour[theme]
root.geometry('%dx%d+%d+%d' % (winwidth, winheight, winx, winy))
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)
prompt = tk.Label(root, text='Enter two letters to add ', font=(text_font, text_size), bg=bgcolour[theme],
                  fg=fgcolour[theme])
prompt.grid(row=1, column=0, padx=paddingh, pady=paddingv)
input_let1 = tk.StringVar()
query_entry1 = tk.Entry(root, textvariable=input_let1, font=(text_font, text_size), bg=bgcolour[theme],
                        fg=fgcolour[theme])
query_entry1.grid(row=1, column=1, columnspan=1, sticky='ew')
input_let2 = tk.StringVar()
query_entry2 = tk.Entry(root, textvariable=input_let2, font=(text_font, text_size), bg=bgcolour[theme],
                        fg=fgcolour[theme])
query_entry2.grid(row=1, column=2, columnspan=1, sticky='ew')
query_entry2.bind('<Return>', go_enter)
enter_button = tk.Button(root, text="Go", font=(text_font, text_size), bg=buttonbg[theme], fg=fgcolour[theme],
                         command=go).grid(row=1, column=3, padx=paddingh, pady=paddingv, sticky='ew')


root.mainloop()
