import urllib.request
import string
import os
import unicodedata
import unidecode

home_path = os.path.expanduser('~/')
output_file = home_path + 'word_lists/new_list.txt'
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

url_base = 'https://en.wikipedia.org/wiki/List_of_musical_instruments'
word_list = []
temp_list = []

request = urllib.request.Request(url_base, headers = hdr)  # The assembled request
response = urllib.request.urlopen(request)
data = str(response.read(), encoding='utf-8')
lines = data.split('\n')
lastline = False
for line in lines:
    temp = line.replace(r'\t','')
    temp = temp.replace('<strong>', '')
    if lastline and temp[0:4] == '<td>':
        temp_list = temp.split('>')
        if len(temp_list) > 2:
            b=2
            name = temp_list[b].replace('</a','')
            name = unidecode.unidecode(name)
        else:
            name = temp_list[1]
            name = unidecode.unidecode(name)
        name.replace('  ',' ')
        x = name.find('(')
        if x > 0:
            name = name[0:x-1]
        print(name, x)
        word_list.append(name)
    if temp[0:4] == '<tr>':
        lastline = True
    else:
        lastline = False

word_list.sort()
print(len(word_list))
output_list = []
for word in word_list:
    if word not in output_list:
        output_list.append(word)
print(len(output_list))

with open(output_file, 'a') as out:
    for n in output_list:
         out.writelines(n+'\n')