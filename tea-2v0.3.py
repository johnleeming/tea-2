import tkinter as tk
from datetime import datetime
import re
import os
import subprocess

home_path =  os.path.expanduser('~/')
word_file = 'word_lists/wlist_match3.txt'

def call_ripgrep(query):
    start_time = datetime.now()
    call = 'rg -c ' + query + ' ' + home_path+word_file
    print(call)
    result = subprocess.run(call, capture_output=True, text=True, shell = True)
    print(result)
    count = int(result.stdout[:-1])
    print(count)
    if count > 0:
        result = subprocess.run(['rg', query, home_path+word_file], capture_output=True, text=True, shell = True)
        matches = str(result.stdout)
    else:
        matches = 'No results found'
    end_time = datetime.now()
    time_taken = end_time - start_time
    return(matches, count, time_taken)


def find_matches(query, list):
    start_time = datetime.now()
    matches = []
    for i in list:
        if query.match(i):
            matches.append(i)
    end_time = datetime.now()
    time_taken = end_time - start_time
    return(matches, time_taken)

# word_list = load_list(word_file)
input_query = input('Enter Regex Query:')
rg_query = '^'+input_query+'\\Z'
print(rg_query)
#re_query = re.compile(input_query)

match_list, count, search_time = call_ripgrep(rg_query)

if count > 0:
    print(str(count) + ' matches found')
    print(match_list)
else:
    print('No match found')
print('search took: ' + str(search_time.total_seconds()) + ' seconds')
#root = tk.Tk()
