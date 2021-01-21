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
log_file = home_path + 'logs/batch_definitions.log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
source_file = home_path + 'answers.txt'
punctuation = {32: None, 33: None, 34: None, 39: None, 40: None, 41: None, 42: None, 44: None, 45: None, 58: None,
               59: None, 91: None, 94: None, 95: None, 96: None}
match_word = []
match_list = []
hover_tip = []
is_error = False


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

temp_list = []
with open(source_file, 'r') as input_file:
    for line in input_file:
        temp_list.append(line[:-1].lower())

temp_words = []
word_list = []
for line in temp_list:
    temp_words = line.split(',')
    for w in temp_words:
        word = str(w.translate(punctuation))
        if word not in word_list:
            word_list.append(word)

word_list.sort()
for w in word_list:
    defn = str(get_definition(w))
    if defn.find('music') >= 0 or defn.find('instrument') >= 0:
        print(w, defn)
