import tkinter as tk
from datetime import datetime
import re
import os

home_path =  os.path.expanduser('~/')
word_file = 'word_lists/wlist_match12.txt'


def load_list(filename):
    temp_list = []
    with open (home_path + filename, 'r') as input_file:
        for line in input_file:
            temp_list.append(line[:-1])
    print(filename + ' words: ' + str(len(temp_list)))
    return(temp_list)

def find_matches(query, list):
    start_time = datetime.now()
    matches = []
    for i in list:
        if query.match(i):
            matches.append(i)
    end_time = datetime.now()
    time_taken = end_time - start_time
    return(matches, time_taken)

word_list = load_list(word_file)
input_query = input('Enter Regex Query:')
re_query = re.compile(input_query)

match_list, search_time = find_matches(re_query,word_list)

if len(match_list) > 0:
    print(str(len(match_list)) + ' matches found')
    print(match_list)
else:
    print('No match found')
print('search took: ' + str(search_time.total_seconds()) + ' seconds')
#root = tk.Tk()
