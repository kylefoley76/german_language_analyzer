
import add_path
from general import *
import os
import time
import collins
import german4 as ge4
import german3 as ge3
from collections import defaultdict
import pyperclip, pyautogui

folder = '/users/kylefoley/codes/german/'




class running_translate:
    def __init__(self, kind = ''):
        spacy_api = ge4.load_spacy()
        #     str1 = """Wir glauben, daß diese Vorgänge nur empirisch-psychologisch
        # untersucht werden können und mit Logik wenig zu tun haben."""
        #     ge.use_spacy(str1,spacy_api)
        self.lemma2rank = pi.open_pickle(f'{folder}lemma2rank', 1)
        self.capi = collins.use_collins()

        lst = os.listdir(dwn_dir)
        pi.save_pickle(1, 'bool1')


        for x in lst:
            if x.endswith("_gerr.txt"):
                file = x
                break

        dname = file[:-8]
        try:
            dct = pi.open_pickle(f"{folder}temp_words/{dname}", 1)
            lword = list(dct.keys())[-1]
            oword = lword
        except:
            dct = {}
            oword = ""
            lword = ""

        done_words = dct.keys()
        if dct:
            done_words = set(y[0][1:-1] for y in dct.values() if y)

    def main_loop(self):
        # try:
        while pi.open_pickle('bool1'):
            start = time.time()
            lst1 = to.from_txt2lst(f'{dwn_dir}{file}', 1)
            found = 0
            give_up = 0
            for x in lst1:
                if found:
                    break
                lst2 = x.split()
                for word in lst2:
                    if ']' in word and word not in dct:
                        word = word.replace(chr(173), "")
                        oword = word
                        dct[oword] = []
                        found = 1
                        break
            end = time.time()
            if dct:
                cword = list(dct.keys())[-1]
                cword = re.sub(r'[\.,\!\?\";\'\*\]]', "", cword)
                if oword != lword:
                    while 1:
                        defn = dct.get(cword)
                        freq, tword = ge4.get_rank(lemma2rank, cword, spacy_api)
                        p(f'frequency for {tword}: {freq}')

                        if defn:
                            p('already looked up')
                            p(defn)
                            break
                        else:
                            item = collins.get_entry(cword, api, dct, done_words)
                            # dwd = use_dwds(cword)
                            dwd = 0
                            if not item:
                                item = []
                                # p('no entry')
                            else:
                                for rw in item:
                                    p(rw)

                            str1 = input('y to try again? x to give up ')
                            give_up = 0
                            if str1 == 'y':
                                cword = input('new word: ')
                            elif str1 == 'x':
                                give_up = 1
                                lword = list(dct.keys())[-1]
                                break
                            else:
                                break

                    if not give_up:
                        item.insert(0, f"*{cword}*")
                        if dwd:
                            p(dwd)
                            item.append('')
                            item.append('dwd')
                            item.append('')
                            item.append(dwd)
                        dct[oword] = item
                        time.sleep(.1)
                        lword = oword
            time.sleep(.5)
        # except:
        #     p ('error')

        pi.save_pickle(dct, f'{folder}temp_words/{dname}', 1)







def parse_subtitles(name):
    file = f'/users/kylefoley/downloads/{name}.txt'
    file2 = f'/users/kylefoley/downloads/{name}2.txt'
    lst = to.from_txt2lst(file, 1)
    lst1 = []
    for x in lst:
        if x and not x[0].isdigit():
            lst1.append(x)
    to.from_lst2txt(lst1, file2, 0, 1)




def from_xml2srt():
    src = f'{dwn_dir}download.txt'
    dest = f'{dwn_dir}download_ger.txt'
    lst = to.from_txt2lst(src)
    lst1 = []
    for x in lst:
        y = vgf.use_beautiful_soup(x, 1, 1)
        lst1.append(y)

    to.from_lst2txt(lst1, dest, 0, 1)



def strong_verb():
    file = f'{folder}strong_verbs.txt'
    lst = to.from_txt2lst_tab_delim(file, 1)
    child2verb = {}
    verb2child = {}
    for x in lst:
        parent = x[0]
        child1 = x[2]
        child2 = x[3]
        child2verb[child1] = parent
        child2verb[child2] = parent
    return child2verb


def temp15():
    file = f'{folder}wdg'
    lst1 = to.from_txt2lst(file, 1)
    time.sleep(2)
    while 1:
        pyautogui.hotkey('command', 'a')
        time.sleep(.5)
        pyautogui.hotkey('command', 'c')
        time.sleep(.5)
        b = pyperclip.paste()
        b = str(b)
        bt = sys.getsizeof(b)
        if bt < 700:
            p(f'incorrect copy')
            return 0
        else:
            lst = b.split('\n')
        lst1 += lst
        str2 = input('ready?, d for done')
        if str2 == 'd':
            break
        time.sleep(1)
        to.from_lst2txt(lst1, f'{folder}wdg')
    to.from_lst2txt(lst1, f'{folder}wdg')

def temp16():
    file = f'{folder}wdg'
    lst = to.from_txt2lst(file, 1)
    file1 = f'{folder}wdg1'
    on = 1
    just_on = 0
    lst1 = []
    last_word = ""
    for e, x in en(lst):
        if e == 16:
            bb = 8
        if 'Moppel' in x:
            bb = 8

        if x == 'DWDS-Logo':
            on = 0
            just_on = 0
        elif 'w \tx' in x:
            on = 1
            just_on = 1

        elif chr(8594) in x:
            on = 1
            just_on = 1
        elif chr(8592) in x:
            pass

        elif x.startswith('Zitationshilfe') and not last_word.startswith('Zi'):
            on = 0
            just_on = 0
        elif x.startswith('BBAW-Logo'):
            on = 1
            just_on = 1
        elif on and x:
            lst1.append(x)
            # if just_on:
            #     p (f'{last_word} {x}')
            just_on = 0
            last_word = x

    lst1 = [x.strip() for x in lst1]
    # lst1.sort()
    # for x, y in zip(lst1[:-1], lst1[1:]):
    #     if bool(re.search(r'^[a-z],\sdas', y)):
    #         p (x, y)

    lst1 = list(set(lst1))
    p (len(lst1))
    lst1.sort()
    to.from_lst2txt(lst1, file1)

    return






class build_corpus():
    def __init__(self):
        pi.save_pickle(1, 'bool1')
        self.dir1 = f'{folder}dcorp/'
        # self.word2lemma = pi.open_pickle(f'{folder}word2lemma', 1)
        self.word2freq = defaultdict(int)
        self.lemma2freq = defaultdict(int)
        # self.lemma2freq = pi.open_pickle(f'{folder}lemma2freq', 1)
        # self.child2verb = strong_verb()
        # self.unknown_lemmas = defaultdict(int)

        # self.unknown_lemmas = pi.open_pickle(f'{folder}unknown_lemmas',1)
        # self.research()
        # self.get_multinet()
        self.nlp = ge4.load_spacy()
        self.bc_step1()
        self.bc_step3()

    def research(self):
        self.unknown_lemmas = sort_dct_val_rev(self.unknown_lemmas)

    def bc_step1(self, sent=0):
        b = 0
        self.kind = 'just_words'
        for dir2 in os.listdir(self.dir1):
            # if not dir2[0] == '.' and '2019' in dir2:
            if not dir2[0] == '.' and pi.open_pickle('bool1'):
                sdir = f'{self.dir1}{dir2}'
                for file in os.listdir(sdir):
                    file1 = f'{sdir}/{file}'
                    if 'words' in file and not sent:
                        p (file1)
                        lst = to.from_txt2lst_tab_delim(file1)
                        self.bc_words(lst)
                        # self.bc_step2(lst)
                    elif 'sentences' in file and sent:

                        b += 1
                        p(file)
                        self.file = file
                        self.file_num = b
                        lst = to.from_txt2lst_tab_delim(file1)
                        self.bc_step2a(lst)


    def bc_step2a(self, lst):
        for e, sent in en(lst):
            vgf.print_intervals(e, 100, self.file_num, 1_000_000)
            try:
                if len(sent) > 1:
                    doc = self.nlp(sent[1])
                    for x in doc:
                        if bool(re.search(r'\d', x.text)):
                            pass
                        else:
                            lemma1 = x.lemma_
                            lemma2 = x._.iwnlp_lemmas
                            if lemma2:
                                lemma3 = lemma2[0]
                            else:
                                lemma3 = lemma1

                            if x.pos_ == 'NOUN':
                                str2 = 'N'
                            elif x.pos_ == 'VERB':
                                str2 = 'V'
                            elif x.pos_ == 'ADJ':
                                str2 = 'J'
                            elif x.pos_ == 'ADV':
                                str2 = 'A'
                            elif x.pos_ == 'PROPN':
                                str2 = 'P'
                            else:
                                str2 = 'O'
                            word = f'{lemma3}*{str2}'
                            self.lemma2freq[word] += 1
            except:
                p(f'error in {self.file} - {sent[1]}')

    def bc_step2(self, lst):
        if len(lst[0]) == 4:
            b = 3
        else:
            b = 2

        for x in lst:
            word = str(x[1])
            freq = x[b]
            if not bool(re.search(r'\d', word)) and not " " in word:

                lemma = self.word2lemma.get(word, 0)
                if type(freq) != int:
                    try:
                        freq = int(freq)
                    except:
                        freq = 0

                if lemma:
                    self.lemma2freq[lemma] += freq
                else:
                    self.unknown_lemmas[word] += freq


    def bc_words(self, lst):
        if len(lst[0]) == 4:
            b = 3
        else:
            b = 2

        for x in lst:
            try:
                word = str(x[1])
                freq = int(x[b])
                self.word2freq[word] += freq
            except:
                p (f'{x[1]} {x[b]} type error')


    def bc_step3(self):
        pi.save_pickle(self.word2freq, f'{folder}word2freq', 1)
        #pi.save_pickle(self.lemma2freq, f'{folder}lemma2freq', 1)
        # p (f'unknown lemmas {len(self.unknown_lemmas)}')
        # pi.save_pickle(self.unknown_lemmas, f'{folder}unknown_lemmas', 1)
        p ('done')


args = vgf.get_arguments()
if eval(not_execute_on_import):
    if args[1] == 'rt':
        running_translate()
    elif args[1] == 'ps':
        parse_subtitles(args[2])
    elif args[1] == 't15':
        temp15()


