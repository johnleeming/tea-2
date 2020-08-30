import urllib.request
import string
import os

home_path = os.path.expanduser('~/')
output_file = home_path + 'word_lists/new_list.txt'
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

url_base = 'https://en.wikipedia.org/wiki/List_of_biblical_names_starting_with_'
output_list = []
temp_list =[]
for c in string.ascii_uppercase:
    print(c)
    try:
        request = urllib.request.Request(url_base + c, headers = hdr)  # The assembled request
        response = urllib.request.urlopen(request)
        data = str(response.read())
        lines = data.split(r'\n')
        for line in lines:
            temp = line.replace(r'\t','')
            temp = temp.replace('<strong>', '')
            if temp[0:4] =='<li>':
                temp_list = temp.split('>')
                b=0
                while b < len(temp_list) -1:
                    if temp_list[b][0] == c:
                        name = temp_list[b].replace('</a','')
                        print(name)
                    b += 1
                output_list.append(name)
    except:
        print('error with ' + url_base + c)

with open(output_file, 'a') as out:
    for n in output_list:
        out.writelines(n+'\n')