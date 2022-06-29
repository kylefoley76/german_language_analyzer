import add_path
from general import *
import os
import time
from collections import Counter
import collins
import shutil
import german4 as ge4
from other.filter_txt import extract_text2 as ex_txt

folder = '/users/kylefoley/codes/german/'


class excel_entry:
    def __init__(self, german):
        # self.date = 0
        # self.rank = 0
        # self.hist = ""
        self.german = german
        self.ignore = 0
        # self.sdef = ""
        # self.gcontext = ""
        # self.econtext = ""
        # self.lgcontext = ""
        # self.ldef = ""

    def __repr__(self):
        return self.german


def convert_nums(dct):
    lst = ['rank', 'excel', 'ignore', 'right']
    for x, y in dct.items():
        for z in lst:
            val = getattr(y, z)
            if val != None:
                setattr(y, z, int(val))


class get_def_from_excel:
    def __init__(self):
        self.ex_file = f'{folder}crude.xlsx'
        wb = ef.load_workbook_read(self.ex_file)
        ws = ef.get_sheet_read(wb, 'words')
        lcol = ef.get_last_col(ws, 1)
        kind = 0
        self.lst = ef.from_sheet_tpl_read(ws, 0, lcol)
        self.word2entry = {}
        self.get_cols()
        self.build_entries()
        convert_nums(self.word2entry)
        self.calc_rank()
        if kind:
            self.lemmatize()

    def get_cols(self):
        self.name2col = {}
        self.col2name = {}
        for e, x in en(self.lst[1]):
            if x:
                if x == 'algorithm':
                    break
                self.name2col[x] = e
                self.col2name[e] = x

    def build_entries(self):
        for entry in self.lst[2:]:
            name = self.get_ename(entry)
            if name:
                ins = excel_entry(name)
                for e, col in en(entry):
                    ecol_name = self.col2name.get(e)
                    if ecol_name:
                        if ecol_name == 'date' and col:
                            if type(col) == float:
                                col = ef.convert19002dt(int(col))
                        elif ecol_name == 'rank':
                            col = int(col)
                        setattr(ins, ecol_name, col)
                ins.excel = 1
                self.word2entry[name] = ins

        return

    def calc_rank(self):
        for entry in self.word2entry.values():
            hist = entry.hist
            if not hist:
                right = 1
            else:
                right = str(hist).count('1')
            entry.right = right
            if entry.hist:
                entry.hist = int(entry.hist)

    def get_ename(self, entry):
        num = self.name2col['german']
        return entry[num]

    def lemmatize(self):
        api = ge2.load_spacy()
        lemma2rank = pi.open_pickle(f'{folder}lemma2rank', 1)
        dct = {}
        for word, ins in self.word2entry.items():
            if " " not in word:
                _, lemma = ge4.get_rank(lemma2rank, word, api)
                if lemma != word:
                    self.add_context(lemma, dct, ins)

                    dct[lemma] = ins
                    ins.german = lemma
                    dct[word] = 0
                else:
                    dct[word] = ins
            else:
                dct[word] = ins
        self.word2entry = dct

    def add_context(self, lemma, dct, ins):
        item = dct.get(lemma)
        if item:
            if not item.gcontext and not ins.gcontext:
                pass
            elif not item.gcontext:
                pass
            elif not ins.gcontext:
                ins.gcontext = item.gcontext
            elif ins.gcontext != item.gcontext:
                ins.gcontext += " !! " + item.gcontext

    def print2excel(self):
        mcol = max(list(self.name2col.values()))
        ex_file2 = f'{folder}throw_away/crude.xlsx'
        shutil.copy2(self.ex_file, ex_file2)
        p('loading workbook')
        wb = ef.load_workbook_write(self.ex_file)
        word_sh = ef.get_sheet(wb, 'words')
        p('printing to excel')
        lst1 = [None] * mcol
        elst = [lst1]
        lst1 = [None] + list(self.name2col.keys())
        elst.append(lst1)

        for word, ins in self.word2entry.items():
            if hasattr(ins, 'excel') and ins.excel:
                if not ins:
                    wcol = self.name2col['german']
                    rcol = self.name2col['right']
                    lst2 = [None] * (rcol - 1)
                    lst3 = [None] * (wcol - rcol)
                    lst4 = [None] * (mcol - wcol)
                    word = word.replace('ß', 'ss')
                    lst1 = lst2 + [-2] + lst3 + [word] + lst4
                    assert len(lst1) == mcol + 1
                else:
                    lst1 = [None]
                    for k in self.name2col.keys():
                        val = getattr(ins, k)
                        if type(val) == str:
                            val = val.replace('ß', 'ss')
                        lst1.append(val)
                elst.append(lst1)

        for i in range(2500):
            elst.append([None] * mcol)

        ef.from_lst2sheet(word_sh, elst)
        p('now saving')
        wb.save(self.ex_file)
        ef.open_wb("crude.xlsx", folder)
        return


class get_from_txt(get_def_from_excel):
    def __init__(self):
        get_def_from_excel.__init__(self)
        file = f'{folder}all_def'
        self.lst = to.from_txt2lst(file, 1)
        self.all_def_lst = self.lst
        self.ignore_put = 0
        self.put_in_excel = 1
        self.phrases = []
        self.phrase2parent = {}


    def get_ignore(self):
        file = f'{folder}ignore'
        self.lst = to.from_txt2lst(file, 1)
        self.ignore_put = 1
        self.main_gft()

    def main_gft(self):
        lst = []
        self.word2known = {}
        self.word2unknown = {}
        first = 1
        self.unread = {}
        start = 0
        self.retry = 0

        for e, x in en(self.lst):
            x = x.strip()
            if x.startswith('zzz'):
                self.put_in_excel = 0
            elif x.startswith("$$"):
                start = 1
            elif not start:
                pass
            elif x.startswith("***"):
                if not first:
                    self.exent(lst, word)
                    self.retry = 0
                else:
                    first = 0
                lst = []
                if x.endswith('/'):
                    word = x[3:-4]
                    self.ignore = 1
                elif x.endswith('.'):
                    self.retry = 1
                    word = x[3:-4]
                else:
                    word = x[3:-3]
                    self.ignore = 0
                self.word = word

            else:
                lst.append(x)

        self.exent(lst, word)

        return

    def exent(self, lst, word):
        ins = excel_entry(word)
        ins.parent = ""
        ins.date = tf.today_dat()
        for e, x in en(lst):
            if x.startswith("@@"):
                x = x[2:]
                att = x[:x.index(":")]
                val = x[x.index(":") + 1:].strip()
                try:
                    if eval(val) == None:
                        val = None
                except:
                    pass
                try:
                    val = int(val)
                except:
                    pass

                setattr(ins, att, val)
            else:
                break

        if self.ignore or not self.put_in_excel:
            ins.ldef = lst[e:]
        elif self.retry:
            ins.ldef = []
            rank, _ = ge4.get_rank(self.lemma2rank, self.word, self.api, 0)
            self.tword2entry[self.word] = ins
            ins.rank = rank
            ins.excel = 0
            ins.ignore = 0

        else:
            if e < len(lst):
                ins.ldef = self.parse_def(lst[e:])

        if " " in word:
            ins.excel = 1

        elif self.ignore_put:
            ins.ignore = 1
            ins.excel = 0
        elif self.ignore:
            ins.right = 4
            ins.excel = 0
            ins.ignore = 1
        elif not self.put_in_excel:
            ins.excel = 0
        else:
            ins.excel = 1

        self.word2entry[word] = ins

    def parse_def(self, lst):
        if all(not bool(re.search(r'\S', x)) or not x for x in lst):
            return ""

        if self.put_in_excel:
            if self.word not in self.in_read_def:
                self.read_def.append(f'***{self.word}***')
                self.read_def += lst
                self.read_def.append('')

        lst1 = []
        lst2 = ['adj.']
        e = 0
        while e < len(lst):
            x = lst[e]
            x = x.strip()
            if 'AE' in x:
                bb = 8

            if '==' in x:
                x = re.sub(r'\(.+\)', '', x)
                x = x.replace('==', '')
            if bool(re.search(r'[^A-Z]AE$', x)) or \
                    bool(re.search(r'[^A-Z]AE[^A-Z]', x)):
                x = x.replace("AE", "")

            if 'rfl#' in x:
                x = x.replace('rfl#', ' rflv ')
                x = x.replace('  ', ' ')
            if ']]' in x:
                x = self.new_lookups(x)

            if 'ccc' in x:
                self.ignore = 1

            if "|" in x and not self.ignore_put:
                self.phrases.append(x)
                self.phrase2parent[x] = self.word

            elif ";:" in x:
                self.special_plurals(x)
            elif x and x[0] == ';':
                lst1.append(x.replace(';', "").strip())
            elif x.endswith('//'):
                str1 = f'{x} {lst[e+1]}'
                str1 = self.clean_word(str1)
                e += 1
                lst1.append(str1)

            elif ";" in x and not self.ignore_put:
                if self.word == 'erhalten':
                    bb = 8

                b = 1
                x = x.replace(';', "").strip()
                if any(y in lst[e + 1] for y in lst2):
                    b = 2
                str1 = f'{lst[e + b]} | {x}'
                self.phrases.append(str1)
                self.phrase2parent[str1] = self.word
                e += b
            e += 1

        if self.ignore:
            return lst
        lst3 = ex_txt(lst)
        lst3 += lst1
        lst3 = self.parse_collins_def(lst3)
        return " | ".join(lst3)

    def add_phrases(self):
        for str1 in self.phrases:
            lst = vgf.strip_n_split(str1, "|")
            ger = lst[0]
            eng = lst[1]
            parent = self.phrase2parent.get(str1)
            if not parent:
                bb = 8

            if ger not in self.word2entry:
                ins = excel_entry(ger)
                ins.rank = -1
                ins.date = tf.today_dat()
                ins.sdef = eng
                ins.excel = 1
                ins.ignore = 0
                ins.parent = parent
                self.add_atttribs(ins)
                self.word2entry[ger] = ins



    def special_plurals(self, x):
        x = x.replace('pl.', '')
        x = re.sub(r'[;:\.]', '', x)
        x = x.strip()
        self.plurals[x] = self.word


    def new_lookups(self, x):
        lst = x.split()
        x = x.replace(']]', '')
        for y in lst:
            if ']]' in y:
                y = y.replace(']]', '')
                y = self.clean_word(y)
                self.to_lookup[y] = [self.word, x]
        return x

    def parse_collins_def(self, lst):
        lst1 = []
        for e, x in en(lst):
            x = x.strip()
            if bool(re.search(r'^[a-h0-9]\s', x)):
                x = x[2:]
            lst1.append(x)
        return lst1

    def add_atttribs(self, exent):
        for y in self.name2col.keys():
            if not hasattr(exent, y):
                setattr(exent, y, "")
        return

    def sort_unread(self):
        dct = {x: int(y.rank) for x, y in self.word2entry.items()
               if hasattr(y, "excel") and not y.excel}
        return sort_dct_val(dct)

    def output2txt(self):
        shutil.copy(f'{folder}all_def.txt', f'{folder}throw_away/all_def.txt')
        all_def = []
        for x in self.all_def_lst:
            all_def.append(x)
            if x.startswith('$$'):
                break

        all_def.append('zzz')
        all_def.append('')
        e = 0
        dct = self.sort_unread()
        for word in dct.keys():
            exxent = self.word2entry[word]
            if hasattr(exxent, 'excel') and not exxent.excel \
                    and not exxent.ignore:
                all_def, e = self.output_txt2(all_def, e, exxent, word)

        to.from_lst2txt(all_def, f'{folder}all_def')
        vgf.open_txt_file(f'{folder}all_def')
        self.output_ignore()

    def output_txt2(self, all_def, e, exxent, word):
        all_def.append(f'$${e}')
        lst = [x for x in exxent.__dict__ if not x[:2] == '__']
        all_def.append(f"***{word}***")
        for att in lst:
            if att not in ['german', 'ldef']:
                val = getattr(exxent, att)
                all_def.append(f'@@{att}: {val}')
        all_def += exxent.ldef
        all_def.append('')
        e += 1
        return all_def, e

    def output_ignore(self):
        shutil.copy(f'{folder}ignore.txt', f'{folder}throw_away/ignore.txt')
        all_def = []
        e = 0
        for word, exxent in self.word2entry.items():
            if exxent.ignore == 1:
                all_def, e = self.output_txt2(all_def, e, exxent, word)

        to.from_lst2txt(all_def, f'{folder}ignore')
        vgf.open_txt_file(f'{folder}ignore')





def find_text(str1):
    lst = os.listdir(dwn_dir)
    for x in lst:
        if "." in x:
            b = x.rindex('.')
            name = x[:b]
            if name.endswith(str1):
                return name
    assert 0


def check_review():
    start = 0
    c = 60
    while 1:
        ins = review_text()
        leng = ins.rev_txt_step1(0)

        if not leng:
            ins.print_lists(start - 3)
            c = 0
            str2 = input('fixed? ')
        else:
            start = leng
            c = 60
            p('sleeping')

        time.sleep(c)


class review_text:
    def __init__(self):
        self.owords = set()
        self.tword2entry = {}


    def rev_txt_step1(self, un=1, file="", file2=""):
        """
        rules
        automatically focuses on the text which ends in gerr in the
            downloads section
        + must be the last character in a word, they inform the computer
            how many other words to skip over, so ++ would be skip over two words
        (compound word)* means the words between ( ) form a unit
        compound words cannot exist on two lines
        + cannot be on german words
        and * may come between commas and such because those characters are deleated any how
        a word cannot have an apostrophe in german

        """
        if not file:
            name = find_text("_gerr")
            self.sfile = name
            file = f"{dwn_dir}{name}.txt"
            file2 = f"{dwn_dir}{name[:-5]}_eng.txt"
            self.file = file

        ger = to.from_txt2lst(file, 1)
        eng = to.from_txt2lst(file2, 1)
        ger = [x for x in ger if bool(re.search(r'\S', x))]
        eng = [x for x in eng if bool(re.search(r'\S', x))]
        self.bracket_equal = 0
        self.chck_bra_equ(ger, eng)
        if self.bracket_equal:
            ewords, gwords = self.review_text2a(eng, ger)
        else:
            ewords, gwords, untrans = self.review_text2(eng, ger)

        self.check_gwords(gwords)
        self.rearrange(ewords)
        self.gwords = gwords
        self.ewords = ewords
        if not self.bracket_equal:
            self.untrans = untrans
            self.get_ucontext(ger, eng)

        if not len(ewords) == len(gwords):
            return 0
        else:
            return len(ewords)

    def review_text2a(self, eng, ger):
        gwords = []
        ewords = []
        self.gdct2line = {}
        self.edct2line = {}
        split_comp1 = ""
        split_comp2 = ""
        lang = 0
        for text, words in zip([ger, eng], [gwords, ewords]):
            for ln, x in en(text):

                if 'infolge' in str(x):
                    bb = 8

                beg1 = bool(re.search(r'\s;', x))
                beg2 = bool(re.search(r'\s\]', x))
                if beg1 and Counter(x).get(';') == 1:
                    split_comp1 = x[x.index(";"):].strip()

                elif beg2 and Counter(x).get(']') == 1:
                    split_comp2 = x[x.index("]"):].strip()

                elif (beg1 and Counter(x).get(';') > 1 or ";" in x) or \
                        (beg2 and Counter(x).get(']') > 1 or ']' in x):
                    lst1 = x.split()
                    ignore = 0
                    for idx, y in en(lst1):
                        if not bool(re.search(r'^;', y)) and ';' in y:
                            if not ignore:
                                if split_comp1:
                                    y = y[:y.index(';')]
                                    y = f'{split_comp1} {y}'
                                    split_comp1 = ""
                                if not lang:
                                    self.owords.add(y)
                                y = self.clean_word(y)
                                if ln == 189:
                                    bb = 8

                                context = self.get_context(y, ln, idx, text, lst1)
                                if not lang:
                                    scontext = self.already_has_context(y, context)
                                    words.append([y, scontext, context])
                                    self.gdct2line[len(words)] = ln
                                else:
                                    words.append([y, context])
                                    self.edct2line[len(words)] = ln

                            ignore = 0

                        elif not bool(re.search(r'^\]', y)) and ']' in y:
                            if not ignore:
                                if split_comp2:
                                    y = y[:y.index(']')]
                                    y = f'{split_comp1} {y}'
                                    split_comp2 = ""
                                if not lang:
                                    self.owords.add(y)
                                y = self.clean_word(y)

                                context = self.get_context(y, ln, idx, text, lst1)
                                if not lang:
                                    scontext = self.already_has_context(y, context)
                                    words.append([y, scontext, context])
                                    self.gdct2line[len(words)] = ln
                                else:
                                    words.append([y + "*", context])
                                    self.edct2line[len(words)] = ln

                            ignore = 0


                        elif bool(re.search(r'^(;|\])', y)):
                            i = x.index(y)
                            found = 0
                            for e, z in en(x[i + 1:]):
                                if z == ';' or z == ']':
                                    found = 1
                                    break
                            star = "*" if z == ']' else ""
                            if not found:
                                if bool(re.search(r'^;', y)):
                                    split_comp1 = x[i + 1:].strip()
                                elif bool(re.search(r'^\[', y)):
                                    split_comp2 = x[i + 1:].strip()

                            else:
                                comp = x[i + 1:e + i + 1]
                                ignore = 1
                                if not lang:
                                    self.owords.add(comp)
                                comp = self.clean_word(comp)
                                context = self.get_context(comp, ln, idx, text, lst1)
                                comp = comp.replace('ß', 'ss')
                                if not lang:
                                    scontext = self.already_has_context(comp, context)
                                    words.append([comp, scontext, context])
                                    self.gdct2line[len(words)] = ln
                                else:
                                    words.append([f"{comp}{star}", context])
                                    self.edct2line[len(words)] = ln

                        elif split_comp1:
                            split_comp1 += f' {y}'

                        elif split_comp2:
                            split_comp2 += f' {y}'

            lang += 1
        return ewords, gwords

    def review_text2(self, eng, ger):
        gwords = []
        ewords = []
        untrans = []
        self.gdct2line = {}
        self.edct2line = {}
        split_comp = ""
        lang = 0
        for text, words in zip([ger, eng], [gwords, ewords]):
            for ln, x in en(text):
                if not lang and len(gwords) > 257:
                    bb = 8

                if 'Kattrin schmeißt' in str(x):
                    bb = 8

                if "]" in x and not lang and not self.bracket_equal:
                    ulst = x.split()
                    for z in ulst:
                        if "]" in z:
                            untrans.append([z, len(gwords)])

                beg = bool(re.search(r'\s;', x))
                if beg and Counter(x).get(';') == 1:
                    split_comp = x[x.index(";"):].strip()

                elif beg and Counter(x).get(';') > 1 or ";" in x:
                    lst1 = x.split()
                    ignore = 0
                    for idx, y in en(lst1):
                        if not bool(re.search(r'^;', y)) and ';' in y:
                            if not ignore:
                                if split_comp:
                                    y = y[:y.index(';')]
                                    y = f'{split_comp} {y}'
                                    split_comp = ""
                                if not lang:
                                    self.owords.add(y)

                                if y.startswith('verlaß'):
                                    bb = 8
                                y = self.clean_word(y)

                                if ln == 189:
                                    bb = 8

                                context = self.get_context(y, ln, idx, text, lst1)
                                if not lang:
                                    if y == 'verla':
                                        bb = 8

                                    # scontext = self.already_has_context(y, context)
                                    words.append([y, "x", context])
                                    self.gdct2line[len(words)] = ln
                                else:
                                    words.append([y, context])
                                    self.edct2line[len(words)] = ln

                            ignore = 0

                        elif bool(re.search(r'^;', y)):
                            i = x.index(y)
                            found = 0
                            for e, z in en(x[i + 1:]):
                                if z == ';':
                                    found = 1
                                    break
                            if not found:
                                split_comp = x[i + 1:].strip()
                            else:
                                comp = x[i + 1:e + i + 1]
                                ignore = 1
                                if not lang:
                                    self.owords.add(comp)
                                comp = self.clean_word(comp)
                                context = self.get_context(comp, ln, idx, text, lst1)
                                if not lang:
                                    scontext = self.already_has_context(comp, context)
                                    words.append([comp, scontext, context])
                                    self.gdct2line[len(words)] = ln
                                else:
                                    words.append([comp, context])
                                    self.edct2line[len(words)] = ln

                        elif split_comp:
                            split_comp += f' {y}'

            lang += 1
        return ewords, gwords, untrans

    def chck_bra_equ(self, ger, eng):
        g = 0
        e = 0
        g1 = 0
        e1 = 0
        for w in ger:
            g += w.count(']')
        for w in eng:
            e += w.count(']')
        for w in ger:
            g1 += w.count(' ]')
        for w in eng:
            e1 += w.count(' ]')
        g = g - g1
        e = e - e1

        if e and e == g:
            self.bracket_equal = 1

        elif e and g != e:
            p('brackets are not right')
            assert 0

    def calc_progress(self):
        name = find_text("_gerr")
        file = f"{dwn_dir}{name}.txt"
        ger = to.from_txt2lst(file)
        ger = [x for x in ger if bool(re.search(r'\S', x))]

        all_words = []
        for x in ger:
            all_words += x.split()
            if 'yyy' in x:
                break

        tally = [0 if ";" in x else 1 for x in all_words]
        total = 0
        lst = []
        for e, x in en(tally):
            total += x
            if e and e % 500 == 0:
                lst.append(total)
                total = 0
        to.from_lst2txt(lst, f'{dwn_dir}tally')

    def already_has_context(self, word, str1):
        if word == 'lästigen':
            bb = 8

        if str1.count("{") == 1 and str1.count('}') == 1:
            o = str1.index('{')
            c = str1.index('}')
            w = str1.index(word)
            if o < w and w < c:

                return str1[o + 1:c]
            else:
                return 'x'

        elif str1.count("{") == 0 or str1.count('}') == 0:
            return 'x'
        else:
            w = str1.index(word)
            v = w
            while 1:
                x = str1[v]
                if x == '{':
                    break
                v -= 1

            y = w
            while 1:
                x = str1[y]
                if x == '}':
                    break
                y += 1

            return str1[v + 1:y]

    def get_ucontext(self, gtext, etext):
        untrans = []
        for lst in self.untrans:
            word = lst[0]
            if word == 'verlaß]':
                bb = 8

            loc = lst[1]
            for lang in range(2):
                if not lang:
                    dct = self.gdct2line
                    text = gtext
                else:
                    dct = self.edct2line
                    text = etext

                start = dct[loc]
                stop = dct[loc + 1]
                str1 = text[start]
                for i in range(start + 1, stop + 1):
                    str1 += f" {text[i]}"

                if not lang:
                    assert word in str1
                    iperc, sger_context, word = self.get_ucontext2(str1, word)
                else:
                    _, econtext, _ = self.get_ucontext2(str1, "", iperc)

            untrans.append([word, sger_context, econtext])
        self.untrans = untrans
        for lst in self.untrans:
            gword = lst[0]
            gsent = lst[1]
            esent = lst[2]
            self.gwords.append([gword, 'x', gsent])
            self.ewords.append(["", esent])

    def get_ucontext2(self, str1, word, iperc=0):
        gstr = str1
        lst = gstr.split()
        found = 0
        if not iperc:
            for idx, g in en(lst):
                if g == word:
                    found = 1
                    break
            assert found
            iperc = idx / len(lst)
            word = word.replace(']', "")
            word = self.clean_word(word)
        else:
            idx = int(iperc * len(lst))

        if idx - 20 > 0:
            start = 20
        else:
            start = 0
        if idx + 20 > len(lst):
            end = len(lst)
        else:
            end = 20
        begin = " ".join(lst[idx - start:idx])
        end = " ".join(lst[idx + 1:idx + end])
        sger_context = f"{begin} *{word}* {end}"
        return iperc, sger_context, word

    def get_context(self, word, ln, idx, text, lst1):
        start = idx - 10

        if word == 'ohne Verzug':
            bb = 8

        lst2 = jsonc(lst1)

        if start < 0 and ln > 0:
            beg = " ".join(lst1[:idx])
            e = ln - 1
            start = idx - 0
            tstart = start
            while tstart < 10 and ln > 0:
                lst1 = text[e].split()
                rem = 10 - start
                if rem > len(lst1):
                    start = 10 - tstart
                else:
                    start = rem
                str1 = " ".join(lst1[-start:])
                tstart += start
                beg = f"{str1} {beg}"
                e -= 1
        else:
            if start < 0:
                start = 0

            beg = lst1[start:idx]
            beg = " ".join(beg)

        lst1 = lst2
        stop = idx + 10
        spaces = word.count(' ')
        end = lst1[idx + 1 + spaces:stop]
        end = " ".join(end)
        if stop > len(lst1):
            stop = len(lst1) - idx

        if ln < len(text):
            e = ln + 1
            tstop = stop
            while tstop < 10 and e < len(text):
                lst1 = text[e].split()
                stop = 10 - stop
                if stop > len(lst1):
                    stop = len(lst1)
                str1 = " ".join(lst1[:stop])
                tstop += stop
                end = f"{end} {str1}"
                e += 1

        return f"{beg} *{word}* {end}"

    def print_lists(self, start):
        b = 0
        for e, g in zip(self.ewords, self.gwords):
            if b > start:
                p(e[0], g[0])
            b += 1

        return

    def clean_word(self, word):
        return re.sub(r'[\[\{\}\]\.\!\?,;\'\":\)\(//]', "", word)



    def nur_deutsch(self, file):
        self.only_german = []
        lst = to.from_txt2lst(file, 1)
        lst = [x for x in lst if bool(re.search(r'\S', x))]
        for e, x in en(lst):
            if bool(re.search(r'\S\]', x)):
                words = x.split()
                for f, word in en(words):
                    if bool(re.search(r'\S\]', word)):
                        self.owords.add(word)
                        beg = words[:f]
                        end = []
                        if f < len(words) - 1:
                            end = words[f + 1:]
                        j = e - 1
                        while len(beg) < 10:
                            beg = lst[j].split() + beg
                            j -= 1
                        beg = beg[-10:]
                        beg = " ".join(beg)
                        j = e + 1
                        while len(end) < 10:
                            end = end + lst[j].split()
                            j += 1
                        end = end[:10]
                        end = " ".join(end)
                        word = self.clean_word(word)
                        context = f"{beg} *{word}* {end}"
                        self.only_german.append([word, context])

        return

    def cut_list(self, lst):
        lst1 = to.from_txt2lst(f'{folder}last_words')
        word1 = lst1[0]
        word2 = lst1[1]
        b = 0
        for x, y in zip(lst[:-1], lst[1:]):
            if x[0] == word1 and y[0] == word2:
                break
            b += 1
        lst2 = [lst[-2][0], lst[-1][0]]
        to.from_lst2txt(lst2, f'{folder}last_words')

        return lst[b + 2:]

    def check_gwords(self, gwords):
        found = 0
        for x in gwords:
            if "+" in x[0]:
                p(f'{x[0]} cannot have a + in it')
                found = 1
        if found:
            assert 0

    def rearrange(self, lst):
        e = 0
        while e < len(lst):
            lst1 = lst[e]
            word = lst1[0]
            if word == 'stemmed*+':
                bb = 8

            cnt = Counter(word).get("+", 0)
            if cnt:
                nword = word.replace("+", "")
                lst2 = [nword, lst1[1]]
                lst.insert(e + 1 + cnt, lst2)
                del lst[e]
            e += 1

        return lst


class get_all_words(review_text):
    def __init__(self):
        review_text.__init__(self)
        self.all_words = []

    def get_atts(self):
        self.to_lookup = {}
        self.in_read_def = set()
        self.api = ge4.load_spacy()
        self.lemma2rank = pi.open_pickle(f'{folder}lemma2rank', 1)
        self.deleted = set(to.from_txt2lst(f'{folder}deleted', 1))
        self.plurals = to.from_txt2dct_1d(f'{folder}plurals')
        self.read_def = to.from_txt2lst(f'{folder}read_def',1)

        for x in self.read_def:
            if x.startswith('***'):
                y = x.replace('*', '')
                self.in_read_def.add(y)

        return






    def txt_abb(self, x):
        if x.startswith('kafka'):
            x = x[:len('kafa_po')]
        else:
            x = x[:4]

        dct = {
            "boll": "BUHZ",
            'brec': "MCIK",
            "der_": "VERR",
            "die_": "FJSV",
            "goet": "GP",
            'mann': "TIV",
            'gras': 'BT',
            'kafka_p': "PRZ",
            'kafka_s': "SCH",
            'kafka_l': "BAV",
            'popp': "FDL",
        }
        return dct[x]

    def all_texts(self):
        self.get_atts()
        lst = os.listdir(f'{folder}read_texts')

        for x in lst:
            if x[0] != '.' and x.endswith('_gerr.txt'):
                eng = x[:-9] + "_eng.txt"
                eng = f"{folder}read_texts/{eng}"
                ger = f"{folder}read_texts/{x}"
                txt = self.txt_abb(x)
                if txt == 'MCIK':
                    bb = 8

                if not os.path.exists(eng):
                    self.nur_deutsch(ger)
                    for w, c in self.only_german:
                        self.all_words.append([w, c, "", "", txt])
                else:
                    self.rev_txt_step1(0, ger, eng)
                    for e, g in zip(self.ewords, self.gwords):
                        lst1 = [g[0], g[2], e[0], e[1], txt]
                        self.all_words.append(lst1)

        return

    def prepare_look_up(self):
        for e, lst in en(self.all_words):
            oword = lst[0]
            self.owords.add(oword)
            lgcontext = lst[1]
            sdef = lst[2]
            econtext = lst[3]
            self.lgcontext = lgcontext
            self.econtext = econtext
            txt = lst[4]
            if " " not in oword:
                rank, gword = ge4.get_rank(self.lemma2rank, oword, self.api)
            else:
                rank = -1
                gword = oword
            ins = self.word2entry.get(gword)
            if not ins and gword not in self.deleted:
                p(f"new entry {e} {gword}")
                ins = excel_entry(gword)
                ins.date = tf.today_dat()
                ins.rank = rank
                ins.gcontext = lgcontext
                ins.econtext = econtext
                ins.txt = txt
                ins.excel = 0
                ins.sdef = sdef
                self.add_atttribs(ins)
                self.tword2entry[gword] = ins

            elif ins:
                for b in ["lgcontext", 'econtext']:
                    val = getattr(self, b)
                    if val:
                        num = self.same_context(ins, val, b)
                        if num == 2:
                            setattr(ins, b, val)
                        elif num == 0:
                            pass
                        else:
                            setattr(ins, b, num)
                            if b == 'lgcontext':
                                p(f'new context {e} {gword}')
                                p(ins.lgcontext)
                                if not ins.sdef:
                                    p(f'new short def {e} {gword}')
                                    p(sdef)
                                    ins.sdef = sdef

                                elif ins.sdef and sdef not in ins.sdef:
                                    ins.sdef += f", {sdef}"
                                    p(f'new short def {e} {gword}')
                                    p(ins.sdef)

                            if ins.excel:
                                ins.right = -8
                            elif ins.ignore:
                                ins.ignore = 0
                                ins.excel = 0
                            if not ins.txt:
                                ins.txt = txt
                            else:
                                if txt not in ins.txt:
                                    ins.txt = f'{ins.txt}, {txt}'

        return

    def same_context(self, ins, str1, att):
        val = getattr(ins, att)
        if not val:
            return 2
        val1 = re.sub(r'[\{\}\*]', '', val)
        str2 = re.sub(r'[\{\}\*]', '', str1)
        val1 = set(val1.split())
        str2 = set(str2.split())
        minus = str2 - val1
        if not minus:
            return 0
        elif len(minus) / len(str2) < .2:
            return 0
        str3 = f'{val} !! {str1}'
        return str3




class read_text(get_all_words, get_from_txt):
    def __init__(self):
        get_from_txt.__init__(self)
        get_all_words.__init__(self)

    def main_rt(self, tlookup=0):
        self.get_atts()
        self.main_gft()
        self.get_ignore()
        self.add_phrases()
        self.get_deleted_entries()
        self.check_words_defn()
        if tlookup:
            self.temp_output()
        else:
            self.prepare_look_up()
            pi.save_pickle(self.tword2entry, f'{folder}throw_away/twords', 1)
            pi.save_pickle(self.word2entry, f'{folder}throw_away/word2entry', 1)
            self.save_deleted_entries()
            self.handle_dbracket()
            self.defn_words()
            self.combine_dct()
            pi.save_pickle(self.word2entry, f'{folder}throw_away/word2entry', 1)
            p('combined')
            self.sort_unread()
            self.output2txt()
            self.output_ignore()
            self.print2excel()

    def check_words_defn(self):
        self.rev_txt_step1(0)
        txt = self.txt_abb(self.sfile)
        for e, g in zip(self.ewords, self.gwords):
            lst1 = [g[0], g[2], e[0], e[1], txt]
            self.all_words.append(lst1)

    def handle_dbracket(self):
        for word, lst in self.to_lookup.items():
            parent = lst[0]
            sent = lst[1]
            rank, word = ge4.get_rank(self.lemma2rank,word, self.api)
            ins = excel_entry(word)
            ins.rank = rank
            ins.excel = 0
            ins.ignore = 0
            ins.lgcontext = sent
            ins.parent = parent
            ins.date = tf.today_dat()
            self.add_atttribs(ins)
            self.tword2entry[word] = ins
        return


    def defn_words(self):
        debug = 0
        b = 0
        self.capi = collins.use_collins()
        for word, ins in self.tword2entry.items():
            p(f'{b} of {len(self.tword2entry)} {word}')
            if " " not in word:
                if debug:
                    ins.ldef = self.defn_words2(word)
                else:
                    try:
                        ins.ldef = self.defn_words2(word)
                        ins.ldef = [x.replace(';','') for x in ins.ldef]
                    except:
                        p(f'error in {word}')
                time.sleep(1)
            b += 1

    def defn_words2(self, word):
        ldef = []
        lins = ge4.base_form_w_leo()
        bool1, bool2 = lins.main(word)
        if bool1:
            ldef += lins.defn
            lins.chain.insert(0, word)
            lst = lins.chain
        else:
            lst = [word]

        for e, word in en(lst):
            lst2 = collins.get_entry(word, self.capi, {}, set())
            if not lst2:
                cins = ge4.parse_collins()
                ldef += cins.main(word)
            ldef += lst2
            dins = ge4.use_dwds(word)
            ldef += dins.transform_word()
            if e + 1 == len(lst):
                break
            time.sleep(.5)

        return ldef

    def combine_dct(self):
        self.word2entry = merge_2dicts(self.word2entry, self.tword2entry)

    def save_deleted_entries(self):
        dct = merge_2dicts(self.word2entry, self.tword2entry)
        st = self.deleted | set(dct.keys())
        try:
            shutil.copy2(f'{folder}deleted', f'{folder}throw_away/deleted')
            shutil.copy2(f'{folder}plurals', f'{folder}throw_away/plurals')
            shutil.copy2(f'{folder}read_def', f'{folder}throw_away/read_def')
        except:
            pass
        to.from_lst2txt(st, f'{folder}deleted')
        to.from_dct2txt_1d(self.plurals, f'{folder}plurals')
        to.from_lst2txt(self.read_def, f'{folder}read_def')


    def get_deleted_entries(self):
        st = set(to.from_txt2lst(f'{folder}deleted'))
        self.deleted = st - set(self.word2entry.keys())

    def temp_output(self):
        lst = []
        lst.append([None]*5)
        for g, e in zip(self.gwords, self.ewords):
            eword = e[0]
            if "*" not in eword:
                gword = g[0]
                gcontext = g[2]
                econtext = e[1]
                lst.append([None, gword, gcontext, eword, econtext])

        ex_file2 = f'{folder}throw_away/crude.xlsx'
        shutil.copy2(self.ex_file, ex_file2)
        p('loading workbook')
        wb = ef.load_workbook_write(self.ex_file)
        word_sh = ef.get_sheet(wb, 'temp')
        p('printing to excel')
        ef.from_lst2sheet(word_sh, lst)
        p('now saving')
        wb.save(self.ex_file)
        ef.open_wb("crude.xlsx", folder)


# order definitions
# method for taking def from txt to excel
# method for taking word from txt directly to excel


args = vgf.get_arguments()
# args = [0, 'gft']


if args[1] == 'cp':
    ins = review_text()
    ins.calc_progress()
elif args[1] == 'rt':
    ins = read_text()
    ins.main_rt()
elif args[1] == 'cr':
    check_review()
