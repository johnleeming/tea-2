import tkinter as tk
from datetime import datetime
import re
import os

home_path =  os.path.expanduser('~/')
word_file = 'word_lists/wlist_match12.txt'
word_list = []
match_list = []

def load_list(filename):
    with open (home_path + filename, 'r') as input_file:
        for line in input_file:
            word_list.append(line[:-1])
    print(filename + ' words: ' + str(len(word_list)))

load_list(word_file)
input_query = input('Enter Regex Query:')
query = re.compile(input_query)

start_time = datetime.now()
for i in word_list:
    if query.match(i):
        match_list.append(i)
end_time = datetime.now()
search_time = end_time - start_time

if len(match_list) > 0:
    print(str(len(match_list)) + ' matches found')
    print(match_list)
else:
    print('No match found')
print('search took: ' + str(search_time.total_seconds()) + ' seconds')
#root = tk.Tk()
