import add_path
from general import *
import spacy
from spacy_iwnlp import spaCyIWNLP
import time, requests, copy
from unidecode import unidecode
from collections import defaultdict

failure = 0
folder = '/users/kylefoley/codes/german/'
obra = chr(9001)
cbra = chr(9002)


def remove_end_hyphen():
    file = f'{dwn_dir}boll_billiarden_ger.txt'
    lst = to.from_txt2lst(file, 1)
    lst = vgf.elim_end_hyphen(lst)
    lst = [x.replace(";", "") for x in lst]
    to.from_lst2txt(lst, file)


class parse_collins:
    def __init__(self):
        pass

    def main(self, oword):
        dct = {
            "ä": 'a',
            "ö": 'o',
            "ü": "u"
        }
        word = oword.lower()
        for x, y in dct.items():
            word = word.replace(x, y)

        self.word = word
        word1 = oword
        b = 2
        done = 0
        multi = 0
        while 1:
            url = f"https://www.collinsdictionary.com/dictionary/german-english/{word}"
            self.lst, final_url = vgf.web_to_text2(url, 'html.parser', 1)
            if final_url != url:
                ridx = url.rindex('/')
                aword = final_url[ridx + 1:]
                if "_" in aword:
                    multi = 1
                    aword = aword[:-2]

            for x in self.lst:
                if x.startswith("Sorry, no results"):
                    p(f'no collins web entry for {oword}')
                    return []

                if x.startswith(f"English translation of"):
                    idx = len("English translation of ")
                    got_word = x[idx + 1:len(x) - 1].lower()
                    if not multi:
                        if got_word != word1:
                            p(f'{got_word} is different from {word1}')

                        done = 1
                        break

                    elif multi:
                        if got_word != word1:
                            word = f'{aword}_{b}'
                            b += 1
                            if b == 4:
                                p(f'failed to find {word1} in collins')
                                return '_3'
                            p(f'now trying {word}')
                        else:
                            done = 1

                        break
            else:
                p('did not find english translation')
                break

            if done:
                break
            time.sleep(.4)
        self.get_definition()
        return self.defn

    def get_definition(self):
        pos = ['NOUN', 'ADVERB', 'VERB', 'ADJECTIVE', 'CONJUNCTION', 'PREPOSITION']
        found = 0
        found2 = 0
        lst1 = []
        self.num = 1
        for e, x in en(self.lst):
            if 'German Easy Learning' in x:
                pass
            elif x.startswith('You may also like'):
                found2 = 1
                break
            elif not found and x.startswith('Credits'):
                found = 1
            elif 'googletag' in x:
                pass
            elif 'Full verb table' in x:
                pass

            elif 'Copyright' in x:
                pass
            elif 'Declension' in x:
                pass
            elif found:
                if x.startswith(chr(215)):
                    pass
                elif not bool(re.search(r'\S', x)):
                    pass
                else:
                    lst1.append(x)

        if not found2:
            p(f'failed to find end in {self.word}')

        if not lst1:
            p(f'failed to find start {self.word}')
        else:
            lst1.insert(0, f'<<<{self.word}>>>')
            lst1.insert(0, '__collins_web__')
        self.defn = lst1

    def cut_string(self, x, lst1):
        x = x.replace('\n', " ")
        x = x.strip()
        if bool(re.search(r'^\d+\.', x)):
            idx = x.index('.')
            num = int(x[:idx]) + 1
            while 1:
                num1 = str(num) + '.'
                try:
                    idx = x.index(num1)
                    x = x[:idx]
                    lst1.append(x)
                    num += 1

                except:
                    lst1.append(x)
                    break


def temp11():
    dct = pi.open_pickle(f'{folder}duden_parsed', 1)
    p('opened')
    for k, v in dct.items():
        for e, z in en(v):
            v[e] = z.replace(chr(160), " ")

    pi.save_pickle(dct, f'{folder}duden_filt', 1)


def similar_words(word, lst, main_lst, u):
    st = set(word)
    word2ratio = {}
    for e, x in en(lst):
        word2ratio[x] = similar_words2(st, word, x)

    word2ratio = sort_dct_val(word2ratio)
    words = []
    for k, v in word2ratio.items():
        if v > .45:
            if words:
                return words[0]
            return words
        elif len(words) > 0:
            main_lst.insert(u + 1, k)
            return words[0]
        else:
            words.append(k)


def similar_words2(st, word, word2):
    b = 0
    st1 = copy.deepcopy(st)
    st2 = set(word2)
    for z in word2:
        if z in st1:
            st1.remove(z)
        else:
            b += 1
    for z in word:
        if z in st2:
            st2.remove(z)
        else:
            b += 1
    return b / (len(st) + len(word2))


def loop_cam_leo():
    global failure
    pi.save_pickle(1, 'bool2')
    file = f'{folder}duden_lookup'
    lst = to.from_txt2lst(file, 1)
    try:
        cambridge = pi.open_pickle(f'{folder}cambridge0', 1)
    except:
        cambridge = {}

    leo_lookup = to.from_txt2lst(f'{folder}leo_already')
    leo = pi.open_pickle(f'{folder}leo0', 1)

    ddspell = {}
    # ddspell = to.from_txt2dct_1d(f'{folder}ddspell')
    abandon = ['Pg']
    for x in abandon:
        if x in lst:
            lst.remove(x)
    lst = [x.replace('.', '') for x in lst]

    start = len(lst)
    for x in reversed(lst):
        start -= 1
        if x in cambridge:
            break

    vgf.backup('leo0.pkl', folder)
    vgf.backup('cambridge0.pkl', folder)

    for e, x in en(lst[start:]):
        f = e + start
        if f and f % 100 == 0:
            pi.save_pickle(leo, f'{folder}leo0', 1)
            pi.save_pickle(cambridge, f'{folder}cambridge0', 1)
            to.from_lst2txt(leo_lookup, f'{folder}leo_already')

        p(f'{f} of {len(lst)}')
        word = x
        lword = word
        cword = word
        alt_spell = ddspell.get(word, 0)
        try:
            if not pi.open_pickle('bool2'):
                break
            else:
                found = 0
                if word not in leo_lookup and word not in leo:
                    found = 1
                    leo_lookup.append(word)
                    try:
                        c = 0
                        while 1:
                            lins = base_form_w_leo()
                            bool1, bool2 = lins.main(lword, leo)
                            if bool1:
                                leo = lins.word2def
                                failure = 0
                                break
                            else:
                                if bool2 == -5:
                                    leo[word] = -5
                                    break
                                if bool2 == -6:
                                    p(f'attempt {c}')
                                    p('too many requests')
                                    time.sleep(60 * 20)
                                    if not pi.open_pickle('bool2'):
                                        break

                                if c: break
                                c += 1
                                if bool2 == -4:
                                    failure += 1
                                    if failure > 4:
                                        pi.save_pickle(0, 'bool2')
                                    elif failure > 3:
                                        time.sleep(5)

                                    elif failure > 2:
                                        p('sleep for 5 minutes')
                                        time.sleep(60 * 5)
                                        leo[word] = 0
                                        break

                                if bool2 < 0 and alt_spell:
                                    lword = alt_spell
                                    time.sleep(.5)
                                else:
                                    break
                    except:
                        if lword not in leo:
                            leo[lword] = 0

                if word not in cambridge:
                    found = 1
                    try:
                        while 1:
                            ins = use_cambridge()
                            lst1 = ins.main_uc(cword)
                            if lst1:
                                cambridge[word] = lst1
                                break
                            elif alt_spell == cword:
                                break
                            elif alt_spell:
                                cword = alt_spell
                                time.sleep(.5)
                            else:
                                break
                    except:
                        cambridge[word] = 0

        except EOFError:
            break
        if found:
            time.sleep(1)

    pi.save_pickle(leo, f'{folder}leo0', 1)
    to.from_lst2txt(leo_lookup, f'{folder}leo_already')
    pi.save_pickle(cambridge, f'{folder}cambridge0', 1)


def loop_duden():
    global failure
    pi.save_pickle(1, 'bool1')
    file = f'{folder}duden_lookup'
    lst = to.from_txt2lst(file, 1)
    try:
        lst2 = pi.open_pickle(f'{folder}duden0', 1)
        dct = lst2[0]
        other_words = lst2[1]
        vgf.backup('duden0.pkl', folder)
        duden_already = set(to.from_txt2lst(f'{folder}duden_already', 1))
        word2duden = pi.open_pickle(f'{folder}word2duden0', 1)
        # ddspell = to.from_txt2dct_1d(f'{folder}ddspell')

    except:
        dct = {}
        other_words = {}
        duden_already = set()
        word2duden = {}

    ddspell = {}
    abandon = ['Coupé', 'Erdmassen', 'Duden', 'Buffet', 'Pg']
    for x in abandon:
        if x in lst:
            lst.remove(x)

    for x, y in dct.items():
        if not y:
            p(x)

    lst = [x.replace('.', '') for x in lst]
    lst = [x.replace(' ', '_') for x in lst]

    e = 0
    while e < len(lst):
        t = lst[e]
        x = ddspell.get(t, t)
        if x not in dct and t not in duden_already:
            if e and e % 500 == 0:
                pi.save_pickle([dct, other_words], f'{folder}duden0', 1)
                to.from_dct2txt_1d(ddspell, f'{folder}ddspell')
                to.from_lst2txt(duden_already, f'{folder}duden_already')
                pi.save_pickle(word2duden, f'{folder}word2duden0', 1)

            p(f'{e} of {len(lst)} {x}')
            word = x
            try:
                if not pi.open_pickle('bool1'):
                    break
                else:
                    try:
                        b = 0
                        while 1:
                            ins = use_duden()
                            bool1 = ins.main_ud(word, dct, word2duden)
                            if ins.other_words:
                                other_words[x] = ins.other_words

                            if bool1 == 429:
                                p(f'too many requests in duden')
                                break
                            if bool1 == 1:
                                if b > 0:
                                    ddspell[x] = word
                                dct = ins.duden_dct
                                duden_already.add(word)
                                break
                            else:
                                duden_already.add(word)
                                if b:
                                    break
                                word = similar_words(x, ins.other_words, lst, e)
                                if not word:
                                    break

                            b += 1
                    except:
                        p(f'general failure in {x}')
                        dct[x] = 0
            except EOFError:
                break
        e += 1

    pi.save_pickle([dct, other_words], f'{folder}duden0', 1)
    to.from_dct2txt_1d(ddspell, f'{folder}ddspell')
    to.from_lst2txt(duden_already, f'{folder}duden_already')
    pi.save_pickle(word2duden, f'{folder}word2duden0', 1)


class parse_cambridge:
    def __init__(self):
        self.dct = pi.open_pickle(f'{folder}cambridge_filt', 1)
        self.dct = pi.open_pickle(f'{folder}cambridge0', 1)
        p('opened')
        self.dct1 = {}
        self.errors = {}
        self.dspell = {}
        self.sspell = {}
        self.missed = {}
        self.word2freq = pi.open_pickle(f'{folder}word2freq', 1)
        self.ewords = set()
        b = 0
        for self.oword, self.lst in self.dct.items():
            if type(self.lst) == int:
                self.errors.setdefault('i', []).append(self.oword)
                self.dct1[self.word] = self.lst
            else:
                self.lword = self.oword.lower()
                self.lword = unidecode(self.lword)
                self.lword = self.lword.replace('.', '')
                self.check_cam()
                self.extract()
            b += 1
            vgf.print_intervals(b, 500)
        # self.get_head_word()
        self.analyse_errors()
        pi.save_pickle(self.dct1, f'{folder}cambridge_filt', 1)

    def analyse_errors(self):

        dct2 = {}
        for x in self.errors['x']:
            dct2[x] = self.word2freq.get(x, 0)

        dct2 = sort_dct_val(dct2)
        to.from_dct2txt_1d(dct2, f'{folder}cambridge_missing')

        return

    def get_head_word(self):
        self.key2entries = {}

        obj = defaultdict(int)
        i = 0
        j = 0
        pos = ['noun', 'adverb', 'adjective', 'verb', 'conjunction',
               'preposition', 'pronoun']

        for x, y in self.dct1.items():
            oword = self.adjust_word(x)
            for z in y:
                first_word = z
                for w in pos:
                    if f" {w} " in z or f' [{w}] ' in z:
                        sec_word = z[:z.index(" ")]
                        sec_word2 = self.adjust_word(sec_word)

                        if sec_word2 != oword:
                            j += 1
                            if j < 500:
                                p(oword)
                                p(z)
                        break

                # if " " in z:
                #     first_word = z[:z.index(" ")]
                # entry = first_word
                # first_word = self.adjust_word(first_word)
                # if oword == first_word:
                #     self.key2entries.setdefault(x, []).append(z)
                #     i += 1
                #     # if i < 500:
                #     #     p (z)
                #     lst = z.split()
                #     for w in lst:
                #         obj[w] += 1

        obj = sort_dct_val_rev(obj)
        return

    def adjust_word(self, got):
        got = got.lower()
        got = unidecode(got)
        got = got.replace('.', '')
        got = re.sub(r'\(.*\)', '', got)
        if '/' in got:
            got = got[:got.index('/')]
        return got

    def extract(self):
        if self.stop != len(self.lst):
            pass
        else:
            if self.oword not in self.ewords:
                self.errors.setdefault('s', []).append(self.oword)

        lst1 = self.lst[self.start:self.stop]
        lst1 = [x for x in lst1 if bool(re.search(r'[a-zA-Z]', x))]
        if self.start != 0:
            self.dct1[self.oword] = lst1
        else:
            if self.oword not in self.ewords:
                self.errors.setdefault('b', []).append(self.oword)
            # self.missed[self.oword] = lst1

    def check_cam(self):
        self.start = 0
        self.stop = len(self.lst)
        for e, x in en(self.lst):
            if x.startswith("Translation of") and 'German' in x:
                self.start = e
                l = len("Translation of ")
                idx = x.index('Translation')
                m = x.index('German')
                got = x[idx + l:m - 3].strip()
                ogot = got
                got = got.lower()
                got = unidecode(got)
                got = got.replace('.', '')
                got = re.sub(r'\(.*\)', '', got)
                if '/' in got:
                    got = got[:got.index('/')]

                if got.lower() != self.lword:
                    rat = similar_words2(set(self.lword), self.lword, got)
                    rat = round(rat, 1)
                    if rat >= .4:
                        self.dspell[self.oword] = [ogot, got, self.lword, rat]
                    else:
                        self.sspell[self.oword] = [ogot, got, self.lword, rat]



            elif x.startswith("Translation of"):
                p(f'failed rule {self.oword}')
                assert 0

            if self.start and x.startswith('Browse'):
                self.stop = e
                return

        else:
            self.ewords.add(self.oword)
            self.errors.setdefault('x', []).append(self.oword)


class use_cambridge:
    def __init__(self):
        pass

    def main_uc(self, word):
        self.oword = word
        url = f'https://dictionary.cambridge.org/dictionary/german-english/{self.oword}'
        time.sleep(1)
        self.other_words = []
        self.lsts = []
        lst, bool1 = vgf.web_to_text2(url, 'lxml', 1)

        return lst


class use_conjugator:
    def __init__(self):
        words = to.from_txt2lst(f'{folder}need_paradigm')
        word2paradigm = {}
        self.dparse = pi.open_pickle(f'{folder}duden_parsed', 1)
        self.word2duden = to.from_txt2lst_tab_delim(f'{folder}word2duden', 1)
        self.word2duden = {x: eval(y) for x, y in self.word2duden}
        self.temp13()
        sys.exit()
        self.get_pronouns()
        self.parse_conjugator2()
        for word in words:
            self.word = word
            p(word)
            url = f'https://konjugator.reverso.net/konjugation-deutsch-verb-{word}.html'
            lst = vgf.web_to_text2(url)
            self.parse_conjugator(lst)
            self.print_conj()
            word2paradigm[self.word] = self.paradigm
            pi.save_pickle(word2paradigm, f'{folder}word2paradigm', 1)
            for x in self.word2duden[self.word]:
                self.dparse[x].vparadigms = [self.paradigm]
            time.sleep(2)
        pi.save_pickle(self.dparse, f'{folder}duden_parsed', 1)


    def temp12(self, words):
        lst1 = []
        for word in words:
            lst = self.word2duden[word]
            for x in lst:
                ins = self.dparse[x]
                part = ins.vparadigms[0]['Partizip II'][0]
                lst2 = [x, part]
                lst1.append(lst2)
        to.from_lst2txt_tab_delim(lst1, f'{folder}temp12')
        vgf.open_txt_file(f'{folder}temp12')

    def temp13(self):
        lst = to.from_txt2lst_tab_delim(f'{folder}temp12')
        for obj in lst:
            word = obj[0]
            part = obj[1:]
            if type(part) == str:
                part = [part]
            dct = self.dparse[word]
            dct.vparadigms[0]['Partizip II'] = part
            p (part)
        pi.save_pickle(self.dparse, f'{folder}duden_parsed',1)



    def get_pronouns(self):
        self.pronouns = {
            'ich ': 1,
            'du ': 2,
            'wir ': 1,
            'ihr ': 2,
            'er/sie/es ': 3,
            'Sie ': 3
        }

    def parse_conjugator(self, lst):
        for x in lst[0]:
            if x.startswith('IndikativPr'):
                self.parse2(x)
                return
        assert 0

    def print_conj(self):
        for x, y in self.paradigm.items():
            p(x, y)
        p('')

    def parse_conjugator2(self):
        lst1 = ['ich ', 'du ', 'er/sie/es ', 'wir ', 'ihr ', 'Sie ',
                ]
        tpl = [
            ('IndikativPräsens', 1, 'Indikativ', 'Präsens'),
            ('Präteritum', 5, 'Indikativ', 'Präteritum'),
            ('Futur I', 4),
            ('Perfekt', 0),
            ('Plusquamperfekt', 0),
            ('Futur II', 0),
            ("Konjunktiv IPräsens", 6, 'Konjunktiv', 'Präsens'),
            ('Futur I', 4),
            ('Perfekt', 0),
            ('Konjunktiv IIFutur II', 0),
            ('Präteritum', 6, 'Konjunktiv', 'Präteritum'),
            ('Futur I', 4),
            ('Plusquamperfekt', 0),
            ('Futur II', 0),
            ('Imperativ Präsens', 0, 'Imperativ', 'Präsens'),
            ('PartizipPräsens', 2, 'Partizip I'),
            ('Perfekt', 2, 'Partizip II'),
            ('InfinitivPräsens', 2, 'yy'),
            ('Perfekt', 0),
            ('zu + Infinitiv', 2, 'Infinitiv')
        ]
        lst2 = []
        for tp in tpl:
            if tp[1] in [1, 5, 6]:
                lst2.append(tp)
                for x in lst1:
                    lst2.append((x))
            elif tp[1] == 2:
                lst2.append(tp)
            elif tp[1] in [0, 4]:
                lst2.append(tp)

        self.tpl = lst2
        return

    def parse2(self, str1):
        paradigm = {}
        e = 0
        f = 0
        doublei = 0
        person = ""
        lperson = "ich "
        number = "Singular"
        lmood = ""
        ltense = ""
        mood = "Indikativ"
        tense = "Präsens"
        lnumber = "Singular"

        while f < len(self.tpl):
            if f == 18:
                bb = 8
            obj = self.tpl[f]
            if type(obj) == str:
                target = obj
                person = self.pronouns[target]
                if target in ['ich ', 'du ', 'er/sie/es ']:
                    lnumber = number
                    number = 'Singular'
                else:
                    lnumber = number
                    number = 'Plural'
                kind = 3

            else:
                target = obj[0]
                kind = obj[1]

                if kind in [1, 2, 4, 5, 6]:
                    lmood = mood
                    ltense = tense
                    if kind in [1, 5, 2, 6]:
                        mood = obj[2]
                        if kind != 2:
                            tense = obj[3]

            while e < len(str1):
                b = len(target)
                lett = str1[e:e + b]
                if lett == target:
                    target = target.strip()
                    to_add = str1[:e].strip()
                    str1 = str1[e + b:]
                    if f == 43:
                        paradigm['infinitiv mit zu'] = [str1]
                        self.paradigm = paradigm
                        return

                    e = 0
                    if kind == 4:
                        bb = 8
                    elif kind == 1:
                        bb = 8

                    if kind in [1, 3, 4, 5]:
                        if f > 1:
                            tmood = mood
                            ttense = tense
                            if target != 'ich' or doublei:
                                if kind in [4, 5]:
                                    tmood = lmood
                                    ttense = ltense

                                value = f'{tmood} {lperson} {ttense} {lnumber} of {self.word}'
                                paradigm.setdefault(value, []).append(to_add)
                        if target == 'Sie':
                            f, doublei = self.double_ich(e, f, str1)
                        else:
                            doublei = 0

                        lperson = person
                    elif kind == 2:
                        if f == 39:
                            pass
                        else:
                            paradigm.setdefault(lmood, []).append(to_add)

                    f += 1
                    break
                else:
                    e += 1
        assert 0
        return

    def double_ich(self, e, f, str1):
        nxt = self.tpl[f + 1][0]
        while 1:
            lett = str1[e:e + 4]
            lett2 = str1[e:e + len(nxt)]
            if lett == 'ich ':
                return f - 6, 1
            elif lett2 == nxt:
                return f, 0
            e += 1


class use_duden:
    def __init__(self):
        pass

    def main_ud(self, word, dct, word2duden):
        global failure
        self.oword = word
        self.duden_dct = dct
        word = self.change_word(word)

        url = f'https://www.duden.de/suchen/dudenonline/{self.oword}'
        headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) '
                                 'AppleWebKit/537.51.2 (KHTML, like Gecko) '
                                 'Version/7.0 Mobile/11D257 Safari/9537.53'}

        time.sleep(1)
        self.other_words = []
        self.lsts = []

        b = 0
        while 1:
            response = requests.get(url, headers=headers)

            if response.status_code == 429:
                p('too many requests')
                return 429

            if response.status_code != 200:
                b += 1
                p(f'response {response.status_code}')
                time.sleep(5)
            else:
                break
            if b > 1:
                return

        html = response.text
        self.word = word
        html = html.split('\n')
        l = len("rechtschreibung/")
        found = 0
        limit = 0
        for x in html:
            if 'Zum vollständigen Artikel' in x:
                idx = x.index('rechtschreibung')
                end = x.index('Zum vollständigen')
                word1 = x[idx + l:end - 2]
                if limit > 7:
                    break

                if self.meets_conditions(word, word1):
                    found = 1
                    limit += 1
                    word2duden.setdefault(self.oword, []).append(word1)
                    p(word1)
                    url1 = f'https://www.duden.de/rechtschreibung/{word1}'
                    time.sleep(1)
                    b = 0
                    while 1:
                        if b > 2:
                            return
                        lst, _ = vgf.web_to_text2(url1, 'lxml', 1)
                        if lst:
                            break
                        else:
                            time.sleep(2)
                            b += 1

                    if type(lst) == list:
                        self.duden_dct[word1] = lst
                    else:
                        p(f'no list in {self.word}')
                        failure += 1

                else:
                    self.other_words.append(word1)

        if not found:
            p(f'no entry for {word}')
            if self.other_words:
                p(f'but has {self.other_words}')
            return 0
        return 1

    def meets_conditions(self, word, word1):
        if word1 in self.duden_dct:
            return 0

        if self.umlaut:
            i = 2
        else:
            i = 1

        for x in range(i):
            if word1 == word:
                return 1
            if word1.startswith(f'{word}_'):
                return 1

            if word1 == word.lower():
                return 1
            if word1.startswith(f'{word.lower()}_'):
                return 1
            word = self.uword

    def change_word(self, word):
        self.umlaut = 0
        if 'ß' in word:
            self.umlaut = 1

        word = self.oword.replace('ß', 'sz')
        self.uword = self.oword.replace('ß', 'ss')
        dct = {
            'Ä': 'Ae',
            'Ö': 'Oe',
            'Ü': "Ue",
            'ä': 'ae',
            'ö': 'oe',
            'ü': 'ue'
        }
        for x, y in dct.items():
            word = word.replace(x, y)
        return word


class use_dwds:
    def __init__(self, word):
        url = f"https://www.dwds.de/wb/{word}"
        url = f"https://www.duden.de/rechtschreibung/Zug_Wagenreihe_Kolonne_Kraft"
        self.lst, _ = vgf.web_to_text2(url, 'html.parser', 1)
        self.word = word

    def transform_word(self):
        lst3 = [self.word, self.word.capitalize()]
        if "ss" in self.word:
            lst4 = [lst3[0], lst3[1]]
            for g in lst3:
                lst4.append(g.replace("ss", 'ß'))
        else:
            lst4 = lst3

        for self.word in lst4:
            final = self.main_dwds()
            if final:
                return final

        return []

    def main_dwds(self):
        lst = self.lst
        final = []
        for e, y in en(lst):
            if f'Kein Eintrag zu {self.word}' in y:
                return []
            if 'Bedeutungsübersicht' in y:
                ostr = y
                idx = y.index('Bedeutungsübersicht') + 1
                y = y[idx + len("Bedeutungsübersicht "):]
                if 'Bedeutung' not in y:
                    p(f'no Bedeutung in {self.word}')

                final, y = self.parse_uberblick(y)
                lst3 = self.parse_bedeut(y)
                final += lst3
                break

            elif "Bedeutung" in y and 'Schreibung' in y:
                pass
            elif "Bedeutung" in y and len(y) <= len("Bedeutungen"):
                pass
            elif 'Bedeutung' in y or 'Bedeutungen' in y:
                ostr = y
                if 'Bedeutungen' in y:
                    idx = y.index('Bedeutungen')
                    y = y[idx + len('Bedeutungen'):]
                else:
                    idx = y.index('Bedeutung')
                    y = y[idx + len('Bedeutung'):]
                final = self.parse_numbers(y, 0)
                lst1 = []
                for str1 in final:
                    b, c = self.parse_beispiel(str1)
                    if b:
                        lst1.append(c)
                        lst1 += b
                    else:
                        lst1.append(c)
                final = lst1
                break

        if final:
            final.insert(0, f'{self.word}')
            final.insert(0, '__dwds__')

        return final

    def parse_uberblick(self, str1):
        lst2 = ["Bedeutungen", "Bedeutung", 'Kollokationen:']
        str2 = ""
        str3 = ""
        for x in lst2:
            if x in str1:
                idx = str1.index(x)
                str2 = str1[:idx].strip()
                str3 = str1[idx + len(x):]
                str3 = str3.strip()
                break

        str2 = self.convert_rnum(str2)
        lst = self.parse_numbers(str2)
        return lst, str3

    def convert_rnum(self, str2):
        if bool(re.search(r'I\..+II\.', str2)):
            for x in range(20, 0, -1):
                rn = vgf.int2roman(x)
                str2 = str2.replace(f'{rn}.', f"{x}.")
        return str2

    def parse_bedeut(self, str1):
        lst2 = []
        str1 = self.convert_rnum(str1)
        lst = self.parse_numbers(str1)
        for x in lst:
            lst1, defn = self.parse_beispiel(x)
            if lst1:
                lst2.append(defn)
                lst2 += lst1
            else:
                lst2.append(defn)

        return lst2

    def parse_beispiel(self, x):
        for y in ['Beispiele:', 'Beispiel:', 'Beispiele', 'Beispiel']:
            if y in x:
                lst1 = x.split(y)
                defn = lst1[0]
                x = lst1[1]
                break
        else:
            return 0, x

        lst = []
        x = re.sub(r'\[.*?\]', "", x)
        str1 = x
        d = 0
        for b, c in zip(x[:-1], x[1:]):
            if b.islower() and c.isupper():
                str2 = str1[:d + 1]
                lst.append(str2)
                str1 = str1[d + 1:]
                d = -1
            d += 1
        if bool(re.search(r'\d\sweitere Beispiele', str1)):
            idx = str1.index('weitere Beispiele')
            str2 = str1[:idx - 2]
            str1 = str1[idx + len('weitere Beispiele'):]
            lst.append(str2)

        lst.append(str1)
        return lst, defn

    def parse_numbers(self, str2, space=1):
        str5 = r'\.'
        lst = []
        num = 2
        while 1:
            if bool(re.search(r'\D' + str(num) + str5, str2)):
                b = re.search(r'\D' + str(num) + str5, str2)
                idx = b.regs[0][0] + 1
                str4 = str2[:idx]
                str2 = str2[idx:]
                lst.append(str4)
                num += 1
            else:
                break
        lst.append(str2)
        return lst


def prepare_test():
    file = f'{folder}test'
    file1 = f'{folder}test1'
    lst = to.from_txt2lst(file, 1)
    lst1 = []
    for x in lst:
        if x.startswith('DEAREST'):
            pass
        elif x.startswith('FRANZ'):
            pass
        elif not bool(re.search(r'\D', x)):
            pass
        else:

            lst1 += x.split()
            if len(lst1) > 10_000:
                break

    for e, x in en(lst1):
        if e and e % 2000 == 0:
            lst1[e] = f'{x} {e}'

    to.from_lst2txt(lst1, file1)
    vgf.open_txt_file(file1)


def grade_test():
    file = f'{folder}test'
    lst = to.from_txt2lst(file, 1)
    wrong = 0
    found = 0
    total = 0
    for e, x in en(lst):
        if x.startswith('zzz'):
            break
        elif x.startswith('yyy'):
            found = 1
        elif bool(re.search(r'[\[\/]', x)):
            wrong += 1
        if found:
            total += 1
    perc = (total - wrong) / total
    perc *= 100
    perc = round(perc, 1)
    p(f'{total} {perc}')


def get_rank(lemma2rank, word, api, uspacy=1):
    word = re.sub(r'[^a-zA-ZäÄüÜöÖß\-]', "", word)
    if uspacy:
        word = use_spacy(word, api, 0)
    word = word.replace('ß', 'ss')
    word = word.lower()
    c = f"{chr(8211)}{chr(8208)}{chr(8210)}{chr(8222)}"
    word = re.sub("[" + c + "]", "-", word)
    return lemma2rank.get(word, 4_000_000), word


def load_spacy():
    nlp = spacy.load('de_core_news_sm')
    iwnlp = spaCyIWNLP(
        lemmatizer_path='/users/kylefoley/codes/venv/lib/python3.8/site-packages/spacy/data/IWNLP.Lemmatizer_20181001.json')
    nlp.add_pipe(iwnlp)
    return nlp


def use_spacy(str1, nlp, sent=1):
    doc = nlp(str1)
    lst = []
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
            lst.append(lemma3)

    if not sent:
        if not lst:
            return ""
        return lst[0]
    else:
        return lst


class parse_leo:
    def __init__(self):
        self.dct = pi.open_pickle(f'{folder}leo0', 1)
        bb = 9
        b = 0
        for x, y in self.dct.items():
            if type(y) == int:
                pass
            else:
                b += 1
        p(b)


class base_form_w_leo:
    def __init__(self):
        pass

    def main(self, word, word2def):
        found_root_form = 0
        get_out = 0
        oword = word
        self.word2def = word2def
        self.defn = []
        self.chain = [oword]
        il = 0
        while 1:
            c = 0
            while 1:
                url = f"https://dict.leo.org/german-english/{word}"
                self.lst, furl = vgf.web_to_text2(url, 'xml', 0)
                if furl == 404:
                    return 0, -5
                if furl == 429:
                    p('too many requests')
                    time.sleep(60 * 10)
                    return 0, -6

                if not furl:
                    c += 1
                    time.sleep(5)
                    if c > 1:
                        return 0, -4
                else:
                    break

            for e, x in en(self.lst):
                if 'Recent lookups' in x:
                    il += 1
                    if il > 7:
                        p(f'{oword} caught in infinite loop in leo')
                        p(self.chain)
                        return 0, -2
                    str1 = x
                    if 'we found no matches for you' in x or \
                            'Leider konnten wir zu Ihrem Suchbegriff' in x:
                        p(f'{oword} no leo entry')
                        return 0, -1

                    if 'Possible base forms' in str1 or get_out:
                        b = len(f'Possible base forms for "{word}"')
                        idx = str1.index('Possible base forms')
                        word = str1[idx + b:].strip()
                        x = word
                        word = word[:30]
                        for y in ['sich ', 'der ', 'die ', 'das ']:
                            if word.startswith(y):
                                word = word[len(y):].strip()
                                break
                        if " " in word:
                            word = word[:word.index(' ')]
                        if word in self.chain:
                            found_root_form = 1
                        if word in self.word2def:
                            found_root_form = 1
                        else:
                            self.chain.append(word)

                    else:
                        found_root_form = 1
                    self.parse_line(x)
                    self.additional_lines(e)
                    p(f'leo found {word}')
                    self.word2def[word] = self.defn
                    break
            else:
                p(f'{oword} does not fit pattern')
                return 0, -3

            if found_root_form:
                break
            time.sleep(1)

        self.final_word = word
        return 1, 1

    def additional_lines(self, e):
        lst1 = ['Verbs', 'Adjectives', 'Nouns', 'Phrases', 'Examples']
        for x in self.lst[e + 1:]:
            if x.startswith("Requires Javascript"):
                pass
            elif 'LEO Dictionary Team' in x:
                break
            elif any(x.startswith(y) for y in lst1):
                self.parse_line(x)
            elif x.startswith('Definitions'):
                for z in ['Examples', 'Phrases / Collocations']:
                    if z in x:
                        idx = x.index(z)
                        str1 = x[idx:]
                        self.parse_line(str1)
                        break

    def parse_bracket(self, str1):
        b = 0
        for e, x in en(str1[:-2]):
            if x == '|':
                if b % 2 == 0:
                    str1 = replace_at_i(e, str1, "(")
                    str1 = replace_at_i(e - 1, str1, " ")
                    str1 = replace_at_i(e + 1, str1, " ")
                else:
                    str1 = replace_at_i(e - 1, str1, " ")
                    str1 = replace_at_i(e, str1, ")")
                b += 1
        return str1

    def parse_line(self, str1):
        str2 = 'Grammar::Discussions::'
        str3 = '::Similar::Related::'
        if str2 in str1:
            idx = str1.index(str2)
            str1 = str1[idx + len(str2):]
        elif str3 in str1:
            idx = str1.index(str3)
            str1 = str1[idx + len(str3):]
        if 'Other actions' in str1:
            idx = str1.index('Other actions')
            str1 = str1[:idx]
        str1 = self.parse_bracket(str1)
        lst1 = str1.split(chr(160))
        self.defn += lst1
        return


args = vgf.get_arguments()

if args[1] == 'ld':
    loop_duden()
elif args[1] == 'lcl':
    loop_cam_leo()
elif args[1] == 't':
    temp11()
elif args[1] == 'dwds':
    use_dwds('x')
elif args[1] == 'gt':
    grade_test()
