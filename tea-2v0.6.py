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
winheight = 1000
winwidth = 1000
winx = 100
winy = 100
paddingh = 5
paddingv = 5
hint_text = "[abc] - one of the listed letters | . any character | * 0 or more | + 1 or more | ? optional | (a|b) a or b " \
            "| \Z end of string"
log_file = home_path + 'logs/tea-2' + datetime.now().strftime('%y-%m-%d') + '.txt'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
punctuation = {33: None, 34: None, 39: None, 40: None, 41: None, 42: None, 44: None, 45: None, 58: None, 59: None,
               94: None, 95: None, 96: None}
match_word = []


class TooltipBase(object):
    """abstract base class for tooltips"""

    def __init__(self, anchor_widget):
        """Create a tooltip.
        anchor_widget: the widget next to which the tooltip will be shown
        Note that a widget will only be shown when showtip() is called.
        """
        self.anchor_widget = anchor_widget
        self.tipwindow = None

    def __del__(self):
        self.hidetip()

    def showtip(self):
        """display the tooltip"""
        if self.tipwindow:
            return
        self.tipwindow = tw = Toplevel(self.anchor_widget)
        # show no border on the top level window
        tw.wm_overrideredirect(1)
        try:
            # This command is only needed and available on Tk >= 8.4.0 for OSX.
            # Without it, call tips intrude on the typing process by grabbing
            # the focus.
            tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w,
                       "help", "noActivates")
        except TclError:
            pass

        self.position_window()
        self.showcontents()
        self.tipwindow.update_idletasks()  # Needed on MacOS -- see #34275.
        self.tipwindow.lift()  # work around bug in Tk 8.5.18+ (issue #24570)

    def position_window(self):
        """(re)-set the tooltip's screen position"""
        x, y = self.get_position()
        root_x = self.anchor_widget.winfo_rootx() + x
        root_y = self.anchor_widget.winfo_rooty() + y
        self.tipwindow.wm_geometry("+%d+%d" % (root_x, root_y))

    def get_position(self):
        """choose a screen position for the tooltip"""
        # The tip window must be completely outside the anchor widget;
        # otherwise when the mouse enters the tip window we get
        # a leave event and it disappears, and then we get an enter
        # event and it reappears, and so on forever :-(
        #
        # Note: This is a simplistic implementation; sub-classes will likely
        # want to override this.
        return 20, self.anchor_widget.winfo_height() + 1

    def showcontents(self):
        """content display hook for sub-classes"""
        # See ToolTip for an example
        raise NotImplementedError

    def hidetip(self):
        """hide the tooltip"""
        # Note: This is called by __del__, so careful when overriding/extending
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            try:
                tw.destroy()
            except TclError:  # pragma: no cover
                pass


class OnHoverTooltipBase(TooltipBase):
    """abstract base class for tooltips, with delayed on-hover display"""

    def __init__(self, anchor_widget, hover_delay=1000):
        """Create a tooltip with a mouse hover delay.

        anchor_widget: the widget next to which the tooltip will be shown
        hover_delay: time to delay before showing the tooltip, in milliseconds

        Note that a widget will only be shown when showtip() is called,
        e.g. after hovering over the anchor widget with the mouse for enough
        time.
        """
        super(OnHoverTooltipBase, self).__init__(anchor_widget)
        self.hover_delay = hover_delay

        self._after_id = None
        self._id1 = self.anchor_widget.bind("<Enter>", self._show_event)
        self._id2 = self.anchor_widget.bind("<Leave>", self._hide_event)
        self._id3 = self.anchor_widget.bind("<Button>", self._hide_event)

    def __del__(self):
        try:
            self.anchor_widget.unbind("<Enter>", self._id1)
            self.anchor_widget.unbind("<Leave>", self._id2)  # pragma: no cover
            self.anchor_widget.unbind("<Button>", self._id3) # pragma: no cover
        except TclError:
            pass
        super(OnHoverTooltipBase, self).__del__()

    def _show_event(self, event=None):
        """event handler to display the tooltip"""
        if self.hover_delay:
            self.schedule()
        else:
            self.showtip()

    def _hide_event(self, event=None):
        """event handler to hide the tooltip"""
        self.hidetip()

    def schedule(self):
        """schedule the future display of the tooltip"""
        self.unschedule()
        self._after_id = self.anchor_widget.after(self.hover_delay,
                                                  self.showtip)

    def unschedule(self):
        """cancel the future display of the tooltip"""
        after_id = self._after_id
        self._after_id = None
        if after_id:
            self.anchor_widget.after_cancel(after_id)

    def hidetip(self):
        """hide the tooltip"""
        try:
            self.unschedule()
        except TclError:  # pragma: no cover
            pass
        super(OnHoverTooltipBase, self).hidetip()


class Hovertip(OnHoverTooltipBase):
    "A tooltip that pops up when a mouse hovers over an anchor widget."
    def __init__(self, anchor_widget, text, hover_delay=1000):
        """Create a text tooltip with a mouse hover delay.

        anchor_widget: the widget next to which the tooltip will be shown
        hover_delay: time to delay before showing the tooltip, in milliseconds

        Note that a widget will only be shown when showtip() is called,
        e.g. after hovering over the anchor widget with the mouse for enough
        time.
        """
        super(Hovertip, self).__init__(anchor_widget, hover_delay=hover_delay)
        self.text = text

    def showcontents(self):
        label = scrolledtext.ScrolledText(self.tipwindow,
                      background=bgcolour[theme], relief=SOLID, borderwidth=1, font=(text_font, text_size-2))
        label.insert(1.0,self.text)
        label.pack()


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
    load_message = 'Using ' + os.path.basename(filename) + ' containing ' + str(len(temp_list)) + ' words.'
    return (temp_list, load_message)


def find_matches(query, list, min, max, ignore_punct):
    start_time = datetime.now()
    matches = []
    no_matches = 0
    if ignore_punct:
        for i in list:
            j = i.translate(punctuation)
            if query.match(j) and min <= len(j) <= max:
                matches.append(i)
                no_matches += 1
    else:
        for i in list:
            if query.match(i) and min <= len(i) <= max:
                matches.append(i)
                no_matches += 1
    end_time = datetime.now()
    time_taken = end_time - start_time
    return (matches, no_matches, time_taken)


def display_results(matches, no_matches, first):
    global match_word
    match_word.clear()
    match_tip = []
    if no_matches - first < 39:
        last = no_matches - 1
    else:
        last = first + 39
    i = 0
    while i <= last - first:
        column_no = int(i / 10)
        row_no = 20 + i - column_no * 10
        match_word.append(tk.Label(root, text=matches[first + i], font=(text_font, text_size), bg=bgcolour[theme],
                                   fg=fgcolour[theme], justify='left'))
        match_word[i].grid(row=row_no, column=column_no, sticky='ew')
        i += 1


def get_tooltips(matches, no_matches, first):
    global match_word
    tip_text = []
    if no_matches - first < 39:
        last = no_matches - 1
    else:
        last = first + 39
    i = 0
    while i <= last - first:
        tip_text.append(get_definition(matches[first + i]))
        Hovertip(match_word[i], tip_text[i], hover_delay=300)
        i += 1


def get_definition(word):
    try:
        response = subprocess.run(['dict', word, ], capture_output=True)
        if len(response.stdout) >0:
            definition = response.stdout
        else:
            definition = 'No definitions found.'
        logging.debug(response.stderr)
    except:
        definition = 'Lookup failed'
        logging.info(response.stderr)
    return definition


def go_enter(event):
    go()


def go():
    start_no = 0
    query = input_query.get()
    min_len = min_length.get()
    max_len = max_length.get()
    ignore_punct = ignore_punctuation.get()
    error_state = tk.StringVar()
    error_label = tk.Label(root, textvar=error_state, font=(text_font, text_size), bg=bgcolour[theme],
                           fg='red').grid(row=1, column=2, sticky='ew')
    try:
        error_state.set(' ')
        re_query = re.compile(query)
        match_list, no_matches, search_time = find_matches(re_query, word_list, min_len, max_len, ignore_punct)
        time_text = 'search took: ' + str(search_time.total_seconds()) + ' seconds'
        solution_time_label = tk.Label(root, text=time_text, font=(text_font, text_size), bg=bgcolour[theme],
                                       fg=fgcolour[theme]).grid(row=10, column=0, columnspan=2, sticky='ew')
        no_results_text = str(no_matches) + ' matches found'
        if no_matches > 40:
            no_results_text += ' (first 40 displayed)'
        no_results_label = tk.Label(root, text=no_results_text, font=(text_font, text_size), bg=bgcolour[theme],
                                    fg=fgcolour[theme]).grid(row=10, column=2, columnspan=2, sticky='ew')
        display_results(match_list, no_matches, start_no)
    except:
        logging.exception('regex error: ' + query)
        error_state.set('Not valid REGEX')
    if no_matches > 0:
        get_tooltips(match_list, no_matches, start_no)


root = tk.Tk()

word_list, load_message = load_list(word_file)
print(load_message)
root.title('Regex-based Word Search')
root['bg'] = bgcolour[theme]
root.geometry('%dx%d+%d+%d' % (winwidth, winheight, winx, winy))
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
load_button_message = tk.StringVar()
load_button_message.set(load_message)
load_message_button = tk.Button(root, textvar=load_button_message, font=(text_font, text_size), bg=buttonbg[theme],
                                fg=fgcolour[theme], command=choose_list)
load_message_button.grid(row=0, sticky='wn', column=0, columnspan=3, padx=paddingh, pady=paddingv)
ignore_punctuation = tk.BooleanVar()
punctuation_checkbox = tk.Checkbutton(root, text='Ignore Punctuation', variable=ignore_punctuation, onvalue=True,
                                      offvalue=False, font=(text_font, text_size), bg=bgcolour[theme],
                                      fg=fgcolour[theme])
punctuation_checkbox.grid(row=0, sticky='wn', column=3, padx=paddingh, pady=paddingv)
prompt = tk.Label(root, text='Enter Regex query: ', font=(text_font, text_size), bg=bgcolour[theme], fg=fgcolour[theme]) \
    .grid(row=1, column=0, padx=paddingh, pady=paddingv)
input_query = tk.StringVar()
query_entry = tk.Entry(root, textvariable=input_query, font=(text_font, text_size), bg=bgcolour[theme],
                       fg=fgcolour[theme])
query_entry.grid(row=1, column=1, sticky='ew')
query_entry.bind('<Return>', go_enter)
enter_button = tk.Button(root, text="Go", font=(text_font, text_size), bg=buttonbg[theme], fg=fgcolour[theme],
                         command=go).grid(row=1, column=3, padx=paddingh, pady=paddingv, sticky='ew')
min_length_label = tk.Label(root, text='Minimum length: ', font=(text_font, text_size), bg=bgcolour[theme],
                            fg=fgcolour[theme]) \
    .grid(row=2, column=0, padx=paddingh, pady=paddingv, sticky='ew')
min_length = tk.IntVar()
min_length.set(3)
min_length_entry = tk.Entry(root, textvariable=min_length, font=(text_font, text_size), bg=bgcolour[theme],
                            fg=fgcolour[theme]).grid(row=2, column=1, padx=paddingh, pady=paddingv, sticky='ew')
max_length_label = tk.Label(root, text='Maximum length: ', font=(text_font, text_size), bg=bgcolour[theme],
                            fg=fgcolour[theme]) \
    .grid(row=2, column=2, padx=paddingh, pady=paddingv, sticky='ew')
max_length = tk.IntVar()
max_length.set(12)
max_length_entry = tk.Entry(root, textvariable=max_length, font=(text_font, text_size), bg=bgcolour[theme],
                            fg=fgcolour[theme]).grid(row=2, column=3, padx=paddingh, pady=paddingv, sticky='ew')
hint_label = tk.Label(root, text=hint_text, font=(text_font, text_size - 2), bg=bgcolour[theme], fg=fgcolour[theme]) \
    .grid(row=3, sticky='wn', column=0, columnspan=4, padx=paddingh, pady=paddingv)

root.mainloop()
