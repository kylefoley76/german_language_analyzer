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


def clean_word(word):
    word = re.sub(r'[!\(\)\]\[\;\:,\}\{]', '', word)
    word = word.replace(obra, "")
    word = word.replace(cbra, "")
    return word


class duden_entry:
    def __init__(self, word):
        self.word = word
        self.pos = ""
        self.defs = []
        self.plurals = []
        self.genitivs = []
        self.genders = set()
        self.indeklinabel = 0
        self.plural_freq = ""
        self.ist = 0
        self.artikel_freq = ""
        self.herkunft = ''
        self.syllables = []
        self.abkurzung = ""
        self.unflektiert = 0

    def __repr__(self):
        return self.word


class duden_def:
    def __init__(self):
        # make sure each instance has a gender
        # indeklinabel, plural_freq, ist, artikel_freq
        self.defn = ""
        self.beispiel = []
        self.wendung = []
        self.gebrauch = ""
        self.herkunft = ''
        self.plurals = []
        self.genitivs = []
        self.indeklinabel = 0
        self.plural_freq = ""
        self.ist = 0
        self.artikel_freq = ""
        self.abkurzung = ""
        self.unflektiert = 0




class duden_verb:
    def __init__(self):
        self.pronouns = {
            'ich': 1,
            'du': 2,
            'wir': 1,
            'ihr': 2,
            'er/sie/es': 3,
            'sie': 3
        }

    def vparadigm(self, e, num):
        # mood (ind, konj, c = imp)
        # tense (n = present, p = preterite)
        # number (s = singular, p = present)
        # person (1,2,3)
        # partizip I = pt1
        # partizip II = pt2
        # infinitive = in

        self.cls.vparadigms = []
        card = '2nd ' if num > 0 else ""
        self.tense = 'Präsens'
        self.vdct = {}
        self.number = 'Singular'
        lpronoun = ""

        f = e
        while f < len(self.lst):
            x = self.lst[f]
            if x == 'Plural':
                self.number = 'Plural'
            elif x == 'Präsens':
                card = '2nd '
                self.vdct = {}
            elif x == 'Singular':
                self.number = 'Singular'
            elif x == 'Präteritum':
                self.tense = 'Präteritum'
            elif x == 'Partizip I':
                f += 1
                verb = self.lst[f]
                self.vdct[x] = vgf.strip_n_split(verb, ',')
            elif x == 'Partizip II':
                f += 1
                verb = self.lst[f]
                self.vdct[x] = vgf.strip_n_split(verb, ',')
            elif x == 'Anzeige':
                break
            elif x == 'Infinitiv mit zu':
                f += 1
                verb = self.lst[f]
                verb = verb.replace('zu ', '')
                self.vdct['infintive'] = vgf.strip_n_split(verb, ',')
                self.cls.vparadigms.append(self.vdct)
            elif x in ['Indikativ', 'Konjunktiv I',
                       'Konjunktiv II',
                       'Imperativ']:
                pass
            else:
                pronoun = ""
                if ' ' not in x:
                    self.mood = 'Imperativ'
                    verb = x
                else:
                    pronoun = x[:x.index(' ')]
                    verb = x[x.index(' ') + 1:]

                self.person = self.pronouns.get(pronoun, "")
                if not self.person:
                    self.mood = 'Imperativ'
                    verb = x
                else:
                    if pronoun == lpronoun:
                        self.mood = 'Konjunktiv'
                    else:
                        self.mood = 'Indikativ'
                kind = f'{card}{self.mood} {self.person} {self.tense} {self.number} of {self.aword}'
                kind = kind.replace('  ', ' ')
                verb = verb.replace('!', '')
                verb = vgf.strip_n_split(verb, ',')
                self.vdct[kind] = verb
                lpronoun = pronoun
                if self.mood != 'c':
                    if pronoun in ['wir', 'ihr', 'sie']:
                        if self.number != 'Plural':
                            bb = 8
                    if pronoun in ['ich', 'du', 'er/sie/es']:
                        if self.number != 'Singular':
                            bb = 8
            f += 1
        if card == '2nd ' and len(self.cls.vparadigms) == 1:
            self.cls.vparadigms.append(self.vdct)
        if card != '2nd ' and len(self.cls.vparadigms) == 0:
            self.cls.vparadigms.append(self.vdct)

        return f

    def verb_tests(self):
        if all(not self.aword.endswith(z) for z in self.modals):
            for x, y in self.vdct.items():
                if 'Indikativ 1 Präsens Singular' in x:
                    if not y[0][-1] == 'e' and " " not in y[0]:
                        p(self.aword, y)
                if 'Indikativ 1 Präsens Plural' in x and " " not in y[0]:
                    if not y[0] == self.aword:
                        p(self.aword, y)
                if 'Indikativ 3 Präsens Plural' in x and " " not in y[0]:
                    if not y[0] == self.aword:
                        p(self.aword, y)
                if x == 'Infinitiv' and " " not in y[0]:
                    if 'zu' not in y[0]:
                        p(self.aword, y)


class duden_grammatik(duden_verb):
    def __init__(self):
        duden_verb.__init__(self)

    def is_nparadigm(self, e, debug=0):
        if self.word == 'Mut':
            bb = 8
        s = 0
        pl = 0
        for f, ln in en(self.lst[e:e + 4]):
            if ln.startswith('Starke Beugung'):
                return 0

            if ln == 'Präsens':
                return 0
            if ln == 'Singular':
                s = 1
            elif 'ohne Plural' in ln:
                pl = 0
            elif ln == 'Plural':
                pl = 1
            elif ln == 'Nominativ':
                k = 1
                if not pl and s:
                    k = 0
                if pl and not s:
                    k = -1
                if not s and not pl:
                    assert 0
                return self.get_nparadigm(f + e + 1, k)

        else:
            return 0

    def steigerung(self, ln, e):
        if "Steigerungsformen: " in ln:
            idx = ln.index('Steigerungsformen') + len('Steigerungsformen')
            if ":" in ln:
                idx += 1

            ln = ln[idx:]
            ln = ln.replace(ellip, "")
            self.ins.steigerung = vgf.strip_n_split(ln, ',')
            if len(self.ins.steigerung) == 3:
                if 'am ' in self.ins.steigerung[2]:
                    self.ins.steigerung[2] = self.ins.steigerung[2][3:]

            return e
        elif 'Positiv' in self.lst[e + 1]:
            po = self.lst[e + 2]
            ko = self.lst[e + 4]
            su = self.lst[e + 6]
            if 'am ' in su:
                su = su[3:]

            self.ins.steigerung = [po, ko, su]
            assert po == self.aword
            return self.adj_para(e + 8)
        else:
            assert 0

    def parse_grammar(self, e):
        e, ln = self.iterate(e)
        self.keywords = ['Genitiv', 'ohne Plural', 'unflektiert',
                         'indeklinabel', 'Plural selten', 'meist im Plural',
                         'ohne Artikel', 'Plural:', 'Singular selten',
                         'Pluraletantum', 'meist Singular', 'meist Plural',
                         'mit Dativ', 'zeitlich', 'modal', 'mit Akkusativ',
                         'Perfektbildung mit „hat“', 'Perfektbildung mit „ist“',
                         'Plural meist', 'Plural auch', 'Plural nur']

        bool1 = self.is_nparadigm(e)
        if bool1:
            return bool1

        if self.word == 'gut':
            bb = 8

        gens = []
        plus = []
        lowest = 0
        for f, ln in en(self.lst[e:e + 4]):
            lst1 = vgf.strip_n_split(ln, ';')
            for x in lst1:
                if 'ohne Plural' in x:
                    self.cls.plural_freq = 'np'
                    lowest = f
                elif x == 'indeklinables Adjektiv':
                    self.cls.indeklinabel = 1
                    lowest = f
                elif x in ['Plural meist', 'meist im Plural', 'meist Plural', 'Singular selten']:
                    self.cls.plural_freq = 'mp'
                    lowest = f
                elif x in ['meist Singular', 'meist im Singular', 'Plural selten', 'Singular meist']:
                    self.cls.plural_freq = 'ms'
                    lowest = f
                elif x in ['Pluraletantum', 'ohne Singular']:
                    self.cls.plural_freq = 'ns'
                    lowest = f
                elif x == 'Perfektbildung mit „ist“':
                    self.cls.ist = 1
                    lowest = f
                elif x == 'Perfektbildung mit „hat“ oder „ist“':
                    self.cls.ist = 2
                    lowest = f
                elif 'meist ohne Artikel' in x:
                    self.cls.artikel_freq = 'mn'
                    lowest = f
                elif 'unflektiert' in x:
                    self.cls.unflektiert = 1
                    lowest = f
                elif 'ohne Artikel' in x:
                    self.cls.artikel_freq = 'n'
                    lowest = f
                elif bool(re.search(r'^Genitiv (Singular|Plural)', x)):
                    lowest = f
                elif x.startswith('Genitiv'):
                    gens, plus = self.gen_plu(ln)
                    lowest = f
                elif x.startswith('Genitiv'):
                    self.gen_plu(x)
                    lowest = f
                elif 'Plural' in x:
                    lst7 = self.parse_plural(x)
                    if lst7:
                        plus += lst7
                    lowest = f

        if gens:
            self.cls.genitivs = gens
        if plus:
            self.cls.plurals = plus

        for f, ln in en(self.lst[e:e + 4]):
            if ln == 'Präsens':
                return self.vparadigm(f + e + 1, 0)
            elif 'Starke Beugung' in ln:
                return self.adj_para(e + f + 1)
            elif 'Steigerungsformen' in ln:
                if self.aword in ['ladylike', 'täglich']:
                    return f + e
                return self.steigerung(ln, f + e)

        return lowest + e

    def compound_plural(self, x):
        lst = self.aword.split()
        lst1 = []
        for x in lst:
            lst1 += self.adjust_plural(x)

        return lst1

    def adjust_plural(self, x):
        str1 = ""
        str2 = ""
        str3 = ''
        str4 = ''
        str5 = x
        if x.endswith('us'):
            str1 = f"{x[:-2]}i"
            str2 = f"{x[:-2]}ora"
            str4 = f"{x[:-2]}era"
            str3 = f"{x[:-2]}en"
            str6 = f"{x[:-2]}ier"
            str7 = f"{x[:-2]}er"  #
            str8 = f"{x[:-2]}e"  #
            return [str5, str1, str2, str3, str4, str6, str7, str8]
        if x.endswith('o'):
            str1 = f"{x[:-1]}is"
            str2 = f"{x[:-1]}en"
            str3 = f"{x[:-1]}i"
        if x.endswith('um'):
            str1 = f"{x[:-2]}as"
            str2 = f"{x[:-2]}en"
            str3 = f"{x[:-2]}a"
        if x.endswith('a'):
            str1 = f"{x[:-1]}en"
            str2 = f"{x[:-1]}e"
        if x.endswith('eau'):
            str1 = f"{x}x"
        if x.endswith('al'):
            str1 = f"{x[:-1]}ux"
        if x.endswith('is'):
            str1 = f"{x[:-1]}en"
            str3 = f"{x[:-2]}en"
            str2 = f"{x[:-1]}des"
        if x.endswith('on'):
            str1 = f"{x[:-2]}en"
        if x.endswith('e'):
            str1 = f"{x[:-1]}ien"
            str2 = f"{x[:-1]}i"
        if x.endswith('os'):
            str1 = f"{x[:-1]}i"
            str2 = f"{x[:-1]}den"  #
            str3 = f"{x[:-1]}en"  #
            str4 = f"{x[:-2]}en"  #
        if x.endswith('ex'):
            str1 = f"{x[:-2]}izes"
        elif x.endswith('anx'):
            str1 = f"{x[:-1]}gen"  #
        elif x.endswith('x'):
            str1 = f"{x[:-1]}c"
            str2 = f"{x[:-1]}z"  #
        if x.endswith('en'):
            str1 = f"{x[:-2]}ina"
        if x.endswith('ans'):
            str1 = f"{x[:-1]}ten"
            str2 = f"{x[:-1]}tien"
            str3 = f"{x[:-1]}zien"  #
            str4 = f"{x[:-1]}tia"  #
        if x.endswith('ens'):
            str1 = f"{x[:-1]}zien"
            str2 = f"{x[:-1]}tia"  #
        if x.endswith('as'):
            str1 = f"{x[:-2]}anten"
            str2 = f"{x[:-2]}antien"
            str3 = f"{x[:-2]}ata"

        if str4:
            return [str5, str1, str2, str3, str4]
        if str3:
            return [str5, str1, str2, str3]
        if str2:
            return [str5, str1, str2]
        if str1:
            return [str5, str1]
        return [str5]

    def parse_plural(self, x):
        if x.count(' ') - 1 == self.aword.count(' ') and \
                x.startswith('Plural'):
            b = len('Plural: ') if x.startswith('Plural:') else len('Plural ')
            str1 = x[b:]
            return [str1]

        tword, x = self.parse_gp(x)

        x = x.replace(',', '')
        return self.parse_gp2(tword, x, 1)

    def gen_plu(self, x):
        x = x.strip()
        if x.count(' ') - 2 == self.aword.count(' '):
            str1 = x[len('genitiv: der '):]
            str1 = clean_word(str1)
            return [str1], []
        elif ',' in x and x.count(' ') - 3 == self.aword.count(' '):
            lst = vgf.strip_n_split(x, ",")
            gen = lst[0]
            plu = lst[1]
            str1 = gen[len('genitiv: der '):]
            str1 = clean_word(str1)
            return [str1], [plu]

        # tword, x = self.parse_gp(x)
        tword = self.aword
        lst = vgf.strip_n_split(x, ',')
        genetivs = []
        plurals = []
        for e, y in en(lst):
            lst5 = self.parse_gp2(tword, y, e)
            if not e:
                genetivs = lst5
            else:
                if lst5:
                    plurals += lst5

        return genetivs, plurals

    def parse_gp(self, x):
        tword = self.aword
        if ' ' in self.aword:
            tword = self.aword.replace(' ', '_')
        x = x.replace(self.aword, tword)
        return tword, x

    def parse_gp2(self, tword, y, plural=0):
        needed = 0
        compounds = []
        if plural:
            if " " in self.aword:
                y = y.replace('_', ' ')
                needed = self.aword.count(' ') + 1
                twords = self.compound_plural(self.aword)
            else:
                twords = self.adjust_plural(tword)
        else:
            if ' ' in tword:
                needed = self.aword.count(' ') + 1
                twords = tword.split()
            else:
                twords = [tword]

        lst5 = []
        lst1 = y.split()
        f = 0

        while f < len(lst1):
            word = lst1[f]
            if '[' in word:
                g, h = self.parse_bracket(word)
                lst1[f] = g
                lst1.insert(f, h)
                f += 1
            f += 1
        for word in lst1:
            if not plural:
                uword = word
            else:
                uword = self.remove_umlaut(word)

            if any(word.startswith(t) for t in twords) or \
                    any(uword.startswith(t) for t in twords):
                word = clean_word(word)
                if " " in self.aword:
                    compounds.append(word)
                    if len(compounds) == needed:
                        word = " ".join(compounds)
                        lst5.append(word)
                        compounds = []
                else:
                    lst5.append(word)

        return lst5

    def parse_bracket(self, str1):
        gen1 = re.sub(r'[\[\]]', '', str1)
        gen2 = re.sub(r'\[.*\]', '', str1)
        return gen1, gen2

    def remove_umlaut(self, str1):
        dct = {
            "ä": 'a',
            "ö": 'o',
            "ü": "u",
            'Ö': "O",
            "Ü": 'U',
            'Ä': 'A'
        }
        i = len(str1) - 1
        for let in reversed(str1):
            if let in dct.keys():
                leta = dct[let]
                str1 = replace_at_i(i, str1, leta)
                break

            i -= 1

        return str1

    def adj_para(self, e):
        lst = ['Artikelwort', 'Maskulinum Femininum Neutrum',
               'Dativ', 'Akkusativ', 'Genitiv', 'Nominativ',
               'kein', 'Adjektiv', 'Artikel'
               ]

        gender = 'm'
        casen = 0
        cases = ['n', 'g', 'd', 'a']
        dct = {}

        kind = 's'  # s = strong, w = weak, m = mixed
        for f, x in en(self.lst[e:]):
            if x.startswith('Schwache Beugung'):
                kind = 'w'
            elif x.startswith('Gemischte Beugung'):
                kind = 'm'
            elif x in ['der', 'das', 'dem', 'den', 'des', 'die']:
                pass
            elif x in ['Info', 'Aussprache']:
                assert 0
            elif x == 'Singular':
                pass
            elif x == 'Plural':
                gender = 'p'
            elif x == 'Maskulinum':
                gender = 'm'
            elif x == 'Femininum':
                gender = 'f'
            elif x == 'Neutrum':
                gender = 'n'
            elif any(x == z for z in lst):
                pass
            elif x.startswith('kein'):
                pass
            else:
                case = cases[casen]
                str1 = f"{kind}{case}{gender}"
                dct[str1] = x
                casen += 1
                if kind == 'm' and gender == 'p' and casen == 4:
                    break

                if casen == 4:
                    casen = 0

        self.cls.aparadigm = dct
        return f + e


    def base_nparadigm(self):
        dct = {
            'ns': "",
            'gs': "",
            'ds': "",
            'as': "",
            'np': "",
            'gp': "",
            'dp': "",
            'ap': "",
        }
        return dct

    def get_nparadigm(self, e, plural=1):
        if plural == 1:
            self.ins.nparadigm = {
                'ns': self.lst[e],
                'gs': self.lst[e + 3],
                'ds': self.lst[e + 6],
                'as': self.lst[e + 9],
                'np': self.lst[e + 1],
                'gp': self.lst[e + 4],
                'dp': self.lst[e + 7],
                'ap': self.lst[e + 10],
            }
            e += 10
        elif not plural:
            self.ins.nparadigm = {
                'ns': self.lst[e],
                'gs': self.lst[e + 2],
                'ds': self.lst[e + 4],
                'as': self.lst[e + 6],
                'np': "",
                'gp': "",
                'dp': "",
                'ap': "",
            }
            e += 6
        elif plural == -1:
            self.ins.nparadigm = {
                'ns': "",
                'gs': "",
                'ds': "",
                'as': "",
                'np': self.lst[e],
                'gp': self.lst[e + 2],
                'dp': self.lst[e + 4],
                'ap': self.lst[e + 6],
            }
            e += 6
        lst = ['der', 'die', 'das', 'den', 'des', 'dem']
        for x, y in self.ins.nparadigm.items():
            if y:
                if " " in y:
                    fword = y[:y.index(" ")]
                    if fword in lst:
                        y = y[y.index(' ') + 1:]
                        self.ins.nparadigm[x] = y
        for x, y in self.ins.nparadigm.items():
            y = re.sub(r'[\[\]]', '', y)
            self.ins.nparadigm[x] = vgf.strip_n_split(y, ',')

        ignore = ['Heuriger', 'Ballaststoff']
        if self.aword not in ignore:

            assert self.aword in self.ins.nparadigm['ns'] or \
                   self.aword in self.ins.nparadigm['np']
        return e






class parse_duden(duden_grammatik):
    def __init__(self):
        duden_grammatik.__init__(self)
        self.kind = ''
        self.dwords = pi.open_pickle(f'{folder}duden_filt', 1)
        self.word2freq = pi.open_pickle(f'{folder}word2freq', 1)
        self.duden_freq = to.from_txt2lst(f'{folder}duden_freq')
        self.duden_freq = [x[:-1] for x in self.duden_freq if "*" in x]
        self.pos_dct = to.from_txt2dct_1d(f'{folder}duden_pos')
        lst = to.from_txt2lst(f'{folder}duden_notes')
        self.duden_notes = [x[:-1] for x in lst if "*" in x]
        self.nump = 0
        if self.kind == 'tverb':
            self.test_verb()
        elif self.kind == 'tpos':
            self.testpos()
        elif self.kind == 'tnoun':
            self.test_noun_decl()
        elif self.kind == 'gram':
            self.grammatik_ana()
        elif self.kind == 'adj':
            self.temp16()
        elif self.kind == 'rb':
            self.res_bedeut()

        self.main_pd()

    def test_noun_decl(self):
        fails = {}
        noun2para = {}
        self.para2 = {}
        for self.word, self.lst in self.dwords.items():
            on = 0
            self.get_aword(self.lst[0])
            if self.word == 'Wortart':
                pass
            else:
                for e, x in en(self.lst[:-1]):
                    if on and x == 'Grammatik':
                        bool1 = self.deter_paradigm(e + 2)
                        if not bool1:
                            fails[self.aword] = self.lst
                        elif bool1 == 2:
                            self.para2[self.aword] = self.line
                        else:
                            noun2para[self.word] = self.ins.nparadigm
                        break

                    if x.startswith('Wortart') and \
                            self.lst[e + 1].startswith('Substantiv'):
                        on = 1
                else:
                    if on:
                        fails[self.aword] = self.lst

        for x, y in self.para2.items():
            p(x)
            p(y)
            p('')

        return

    def num_vparadigm(self):
        b = 0
        c = 0
        for x, y in self.word2cls.items():
            if y.pos and y.pos[0] == 'v':
                b += 1
                if hasattr(y, 'vparadigm'):
                    c += 1
        p (b)
        p (c)


    def grammatik_ana(self):
        dct1 = {}
        dct5 = {}
        dct3 = defaultdict(int)
        dct4 = defaultdict(int)
        st4 = set()
        self.keywords = ['Genitiv', 'ohne Plural', 'unflektiert',
                         'indeklinabel', 'Plural selten', 'meist im Plural',
                         'ohne Artikel', 'Plural:', 'Singular selten',
                         'Pluraletantum', 'meist Singular', 'meist Plural',
                         'mit Dativ', 'zeitlich', 'modal', 'mit Akkusativ',
                         'Perfektbildung mit „hat“', 'Perfektbildung mit „ist“',
                         'Plural meist', 'Plural auch', 'Plural nur']

        for self.word, self.lst in self.dwords.items():
            on = 0
            self.get_aword(self.lst[0])
            if self.word == 'Wortart':
                pass
            else:
                for e, x in en(self.lst[:-1]):
                    if x.startswith('vgl.'):
                        bb = 8

                    if x.startswith('Grammatik'):
                        if self.lst[e + 1] not in ['INFO', 'Info']:
                            self.grammatik_ana2(e, dct1, dct3)
                        else:
                            self.grammatik_ana2(e + 1, dct5, dct4)

        dct3 = sort_dct_val_rev(dct3)
        dct4 = sort_dct_val_rev(dct4)
        return

    def recut(self):
        stoppers = ["Weitere Vorteile", 'Sie sind öfter',
                    'Wussten Sie schon']

    def res_bedeut(self):  # delete soon
        dct = defaultdict(int)
        dct2 = defaultdict(int)
        dct3 = {}
        lst4 = []
        lst = ['Beispiel', 'Wendung', 'Gebrauch',
               'Herkunft', 'Grammatik', 'Kurzform',
               'Kurzwort']

        lst3 = ['Abkürzung', 'Kurzform', 'Kurzwort']

        # for x in lst:
        #     dct3[x] = [defaultdict(int), defaultdict(int)]

        # dct1 = defaultdict(int)
        # for self.word, self.lst in self.dwords.items():
        #     if self.word != 'Bedeutung':
        #         on = 0
        #         found = 0
        #         b = 0
        #         # self.word = "Agent_Provocateur"
        #         # self.lst = self.dwords[self.word]
        #         self.get_aword(self.lst[0])
        #         for e, x in en(self.lst[:-1]):
        #             for z in lst3:
        #                 if x.startswith(z):
        #
        #                     end = e+3 if len(self.lst) > e + 3 else len(self.lst)
        #                     begin = e-5 if e > 5 else 0
        #                     dct3.setdefault(z, []).append(self.lst[begin:end])
        #

        # dct1 = sort_dct_val_rev(dct1)
        lst5 = []
        for self.word, self.lst in self.dwords.items():
            for e, x in en(self.lst[:-1]):
                if x.startswith('Kurzform für') \
                        and len('kurzform fur') < len(x):
                    lst5.append(x)
                if x.startswith('Kurzwort für') \
                        and len('kurzwort fur') < len(x):
                    lst5.append(x)

        bb = 8

        #     x = self.copyright(x)
        #
        # if on and x == 'Anzeige':
        #     break
        #
        # if on:
        #     for y in lst:
        #         if y in x and not x.startswith(y):
        #             lst4.append(x)
        #             break
        #
        #
        #     for y in lst:
        #         if x.startswith(y):
        #             dct3[y][0][prev] += 1
        #             dct3[y][1][prev2] += 1
        #             break
        #
        #
        #
        # if x.startswith('Bedeutung'):
        #     on = 1

        # for x, y in dct3.items():
        #     y[0] = sort_dct_val_rev(y[0])
        #     y[1] = sort_dct_val_rev(y[1])

        # Gebrauch,

        return

    def temp16(self):
        genitiv = []
        ogenitiv = []
        ogenitiv2 = []
        pluo = []
        dct4 = {}
        b = 0
        for self.word, self.lst in self.dwords.items():
            on = 0
            # self.word = "Agent_Provocateur"
            # self.lst = self.dwords[self.word]
            self.get_aword(self.lst[0])
            b += 1
            c = 0
            # if b > 30_000:
            #     break

            for e, x in en(self.lst[:-1]):
                if self.word == 'Ort_Platz_Stelle_Ortschaft' \
                        and e == 68:
                    bb = 8
                d = 0
                if x.startswith('Grammatik'):
                    z, oln = self.iterate(e)
                    if not self.is_nparadigm(e + 1, 1):
                        d += 1
                        lst1 = vgf.strip_n_split(oln, ';')
                        gens = []
                        plus = []
                        for ln in lst1:
                            if bool(re.search(r'^Genitiv (Singular|Plural)', ln)):
                                ogenitiv.append(ln)
                            elif ln.startswith('Genitiv'):
                                gens, plus = self.gen_plu(ln)
                                genitiv.append(ln)
                                b += 1
                            elif 'Genitiv' in ln:
                                ogenitiv2.append(ln)
                            elif ln in ['Pluraletantum', 'Plural selten']:
                                pass
                            elif 'Plural' in ln:
                                lst7 = self.parse_plural(ln)
                                if lst7:
                                    plus += lst7
                                pluo.append(ln)
                                c += 1

                        if gens or plus:
                            dct4[self.word + str(d)] = [self.aword, gens, plus, oln]

        # for x, y in dct4.items():
        #     if " " not in y[0] and 'ohne Plural' not in y[3]:
        #         if 'Genitiv' in y[3] and not y[1]:
        #             p(y[0])
        #             p(y[3])
        #             p(y[1])
        #             p(y[2])
        #             p("")
        #         elif "Plural" in y[3] and not y[2]:
        #             p(y[0])
        #             p(y[3])
        #             p(y[1])
        #             p(y[2])
        #             p("")

        for x, y in dct4.items():
            if " " in y[0] and 'ohne Plural' not in y[3]:
                if 'Genitiv' in y[3] and not y[1]:
                    p(y[0])
                    p(y[3])
                    p(y[1])
                    p(y[2])
                    p("")
                elif "Plural" in y[3] and not y[2]:
                    p(y[0])
                    p(y[3])
                    p(y[1])
                    p(y[2])
                    p("")

        for x, y in dct4.items():
            # if ' ' in y[0]:
            p(y[0])
            p(y[3])
            p(y[1])
            p(y[2])
            p("")

        return

    def grammatik_ana2(self, e, dct1, dct3):
        w = self.lst[e + 1]
        lst3 = vgf.strip_n_split(w, ';')
        for y in lst3:
            str1 = f'{self.aword} - {y}'
            for key in self.keywords:
                if key in str1:
                    dct1.setdefault(key, []).append(str1)
                    break
            else:
                dct3[y] += 1
                dct1.setdefault('other', []).append(str1)

    def get_atts(self):
        pos = []

    def get_line_pass(self):
        self.line_pass = set()
        self.pos = []
        for x in self.duden_freq:
            if x[-1] == '*':
                self.line_pass.add(x[:-1])
            elif x[-1] == '#':
                self.pos.append(x[:-1])

    def freq_words(self):
        dct = defaultdict(int)
        for x, y in self.dwords.items():
            for z in y:
                dct[z] += 1
        dct = sort_dct_val_rev(dct)
        dct1 = vgf.split_dct(dct, 0, 200)
        lst = list(dct1.keys())
        to.from_lst2txt(lst, f'{folder}duden_freq')

    def main_pd(self):
        self.num = 0
        ignore = ['Dr__j__u_', 'Aktiven', 'Kaskadeur']
        self.word2cls = {}
        for self.word, self.lst in self.dwords.items():
            if not self.word in ignore and self.num > -1:
                # self.word = 'gehen'
                # self.lst = self.dwords[self.word]
                self.handle_lst()
                self.word2cls[self.word] = self.ins
                # self.print_pd()
            self.num += 1
            vgf.print_intervals(self.num, 100)
        self.num_vparadigm()
        pi.save_pickle(self.word2cls, f'{folder}duden_parsed',1)
        return

    def print_pd(self, bool1 = 0):
        if len(self.ins.defs) > 2 or bool1:
            self.nump += 1
            p(self.word)
            p('')
            for x in self.ins.total_meaning:
                p(x)

            p('')
            p(self.ins.word, self.ins.aword)
            p(self.ins.pos)

            if self.ins.genders:
                p(f'GENDER: {self.ins.genders}')
            if hasattr(self.ins, 'vparadigm'):
                for x, y in self.ins.vparadigm.items():
                    p(x, y)
            if hasattr(self.ins, 'nparadigm'):
                for x, y in self.ins.nparadigm.items():
                    p(x, y)
            if hasattr(self.ins, 'aparadigm'):
                for x, y in self.ins.aparadigm.items():
                    p(x, y)
            if hasattr(self.ins, 'steigerung'):
                p(f'steigerung: {self.ins.steigerung}')

            if self.ins.syllables:
                p(f'SYLLABLES {self.ins.syllables}')
            if self.ins.plurals:
                p('PLURALS')
                p(self.ins.plurals)
            if self.ins.genitivs:
                p('GENITIVS')
                p(self.ins.genitivs)
            if self.ins.herkunft:
                p('HERKUNFT')
                p(self.ins.herkunft)
            if self.ins.indeklinabel:
                p(f'INDEKLINABEL')
            if self.ins.unflektiert:
                p(f'UNFLEKTIERT')
            if self.ins.abkurzung:
                p(f'ABKURZUNG {self.ins.abkurzung}')
            if self.ins.plural_freq:
                p(f'PLURAL FREQUENCY {self.ins.plural_freq}')
            if self.ins.ist:
                if self.ins.ist == 1:
                    p('IS AUXILLIARY')
                else:
                    p('DUAL AUXILLIARY')
            if self.ins.artikel_freq:
                p(f'ARTICLE FREQUENCY: {self.ins.artikel_freq}')

            p('')

            if hasattr(self.ins, 'defs'):
                for defn in self.ins.defs:
                    p('DEFINITION')
                    p(defn.defn)
                    if defn.gebrauch:
                        p('GEBRAUCH')
                        p(defn.gebrauch)
                    if defn.genitivs:
                        p('GENITIVS')
                        p(defn.genitivs)
                    if defn.plurals:
                        p('PLURALS')
                        p(defn.plurals)

                    if defn.beispiel:
                        p('BEISPIEL')
                        for x in defn.beispiel:
                            p(x)
                    if defn.wendung:
                        p('WENDUNGEN')
                        for x in defn.wendung:
                            p(x)
                    if defn.herkunft:
                        p('HERKUNFT')
                        p(defn.herkunft)
                    if defn.indeklinabel:
                        p(f'INDEKLINABEL')
                    if defn.unflektiert:
                        p(f'UNFLEKTIERT')
                    if defn.abkurzung:
                        p(f'ABKURZUNG {defn.abkurzung}')
                    if defn.plural_freq:
                        p(f'PLURAL FREQUENCY {defn.plural_freq}')
                    if defn.ist:
                        if defn.ist == 1:
                            p('IS AUXILLIARY')
                        else:
                            p('DUAL AUXILLIARY')
                    if defn.artikel_freq:
                        p(f'ARTICLE FREQUENCY: {defn.artikel_freq}')
                    p('')

        if self.nump > 65:
            if not bool1:
                self.view_ab()


            bb = 8

    def view_ab(self):
        for x, y in self.word2cls.items():
            if y.abkurzung:
                self.ins = y
                self.print_pd(1)
            elif any(z.abkurzung for z in y.defs):
                self.ins = y
                self.print_pd(1)

        return


    def copyright2(self):
        for e, x in en(self.lst):
            if chr(169) in x:
                self.lst[e] = self.copyright(x)
        self.lst = [x for x in self.lst if x]

    def copyright(self, x):
        lst = ['Beispiel', 'Wendung', 'Gebrauch',
               'Herkunft', 'Grammatik', 'Kurzform',
               'Kurzwort']
        for y in lst:
            if y in x:
                idx = x.index(y)
                return x[idx:]
        return 0

    def par_abk(self, x, e):
        idx = len('abkurzung')
        if len(x) > idx:
            if ':' in x:
                idx += 1
            str1 = x[idx:].strip()
            self.cls.abkurzung = str1
        else:
            if "." in self.lst[e + 1] or \
                    len(self.lst[e+1]) < 4:
                self.cls.abkurzung = self.lst[e + 1]
                return e + 1
        return e

    def par_kurz(self, x, e):
        idx = len('kurzform fur')
        if len(x) > idx:
            if ':' in x:
                idx += 1
            str1 = x[idx:].strip()
            if self.cls.abkurzung:
                self.cls.abkurzung += ' ' + str1
            else:
                self.cls.abkurzung = str1
            return e
        else:
            str1 = self.lst[e+1]
            if self.cls.abkurzung:
                self.cls.abkurzung += ' ' + str1
            else:
                self.cls.abkurzung = str1
            return e + 1

    def get_aword(self, x):
        l = len('worterbuch')
        idx = x.index('Wörter')
        self.aword = x[idx + 3 + l:]
        self.aword = self.aword.replace(chr(174), '')
        self.aword = re.sub(r'[\[\]]', '', self.aword)

    def handle_lst(self):
        self.ins = duden_entry(self.word)
        # self.get_total_meaning()
        self.get_aword(self.lst[0])
        self.ins.aword = self.aword
        self.defn = duden_def()
        self.cls = self.defn
        self.lst = [x.strip() for x in self.lst if x and bool(re.search(r'[a-zA-Z]', str(x)))]
        self.copyright2()
        e = 1
        if self.word == 'Bau':
            bb = 8

        while e < len(self.lst) - 1:
            x = self.lst[e]
            nxt = self.lst[e + 1]

            if x.startswith('Wortart'):
                e = self.get_pos(e)

            elif x.startswith('Bedeutung'):
                c = re.findall(r'\d', x)
                meanings = "".join(c)
                if meanings:
                    meanings = int(meanings)
                else:
                    meanings = 1
                self.ins.meanings = meanings
                e = self.handle_meaning(e)

            elif x.startswith('Worttrennung'):
                e = self.get_syllables(e)

            elif x.startswith('Grammatik'):
                self.cls = self.ins
                e = self.parse_grammar(e)

            elif x.startswith('Abkürzung'):
                self.cls = self.ins
                e = self.par_abk(x, e)

            elif x.startswith('Kurzwort') or\
                    x.startswith('Kurzform'):
                self.cls = self.ins
                e = self.par_kurz(x, e)

            elif x.startswith('Synonyme zu'):
                e, x = self.iterate(e)
                self.ins.synonyms = x

            elif x.startswith('Herkunft'):
                if x.endswith('ungeklärt'):
                    self.ins.herkunft = 'ungeklärt'
                else:
                    e, x = self.iterate(e)
                    self.ins.herkunft = self.lst[e]

            e += 1

        return 1

    def get_pos(self, e):
        e, ln = self.iterate(e)
        if ln.startswith('Substantiv'):
            self.ins.pos = 's'
            self.get_genders(e)
        elif ln.startswith('substantiviertes'):
            self.ins.pos = 'js'
            self.get_genders(e)

        else:
            self.ins.pos = self.pos_dct[ln]
        return e

    def get_genders(self, e):
        if 'ohne Artikel' in self.lst[e]:
            return

        gens = {'Neutrum': 'n', 'maskulin': 'm',
                'Feminin': 'f', 'Pluralwort': 'p',
                'Maskulin': 'm', 'feminin': "f", "pluralwort": 'p',
                'neutrum': 'n'}
        ln = self.lst[e]
        lst = []
        for x, y in gens.items():
            if x in ln:
                lst.append(y)
        assert lst
        self.ins.genders = lst
        self.ins.gen_info = ln

    def get_syllables(self, e):
        e, ln = self.iterate(e)
        self.ins.syllables = ln.split('|')
        return e

    def get_total_meaning(self):
        lst = []
        for x in self.lst:
            if x not in self.duden_freq:
                lst.append(x)
        self.ins.total_meaning = lst

    def handle_meaning(self, e):
        e, x = self.iterate(e)
        self.mean = duden_def()
        self.cls = self.mean
        mean_stoppers = ['Anzeige']
        password = ['Info']
        stoppers = ['beispiel', 'wendung']
        kind = 'bedeutung'

        while e < len(self.lst):
            prev = self.lst[e - 1]
            x = self.lst[e]
            if e == len(self.lst) - 1:
                nxt = ""
            else:
                nxt = self.lst[e + 1]
            if self.word == 'Ost_Himmelsrichtung_frueher':
                bb = 8
            if e in [17,99]:
                bb = 8

            if any(x in y for y in password):
                pass

            elif any(x.startswith(v) for v in mean_stoppers):
                self.ins.defs.append(self.mean)
                return e

            elif x.startswith('Gebrauch'):
                if kind in stoppers:
                    self.add_def(prev, kind)
                e, x = self.iterate(e)
                self.mean.gebrauch = x
                kind = 'gebrauch'

            elif x.startswith("Grammatik"):
                if kind in stoppers:
                    self.add_def(prev, kind)
                e = self.parse_grammar(e)
                kind = 'grammatik'

            elif x.startswith('Abkürzung'):
                e = self.par_abk(x, e)
                kind = 'abkurzung'

            elif x.startswith('Kurzwort') or \
                    x.startswith('Kurzform'):
                e = self.par_kurz(x, e)
                kind = 'abkurzung'

            elif x.startswith('Herkunft'):
                if kind in stoppers:
                    self.add_def(prev, kind)
                if x.endswith('ungeklärt'):
                    self.ins.herkunft = 'ungeklärt'
                else:
                    self.ins.herkunft = self.lst[e + 1]
                    e += 1
                kind = 'herkunft'

            elif x.startswith('Wendungen, Redens'):
                if kind == 'wendung':
                    self.add_def(prev, 'wendung')
                e, x = self.iterate(e)
                kind = 'wendung'
                self.mean.wendung.append(x)

            elif x.startswith("Beispiel"):
                if kind in stoppers:
                    self.add_def(prev, kind)
                e, x = self.iterate(e)
                kind = 'beispiel'
                self.mean.beispiel.append(x)

            elif kind.startswith('bedeutung'):
                self.add_def(x, kind)
                kind = 'bedeutung2'

            elif kind in ['gebrauch', 'herkunft', 'grammatik']:
                if nxt.startswith('Beispiel') or \
                        nxt.startswith('Wendungen, Re'):
                    self.add_def(x, kind)
                    kind = 'bedeutung3'

            elif kind == 'beispiel':
                self.mean.beispiel.append(x)

            elif kind == 'wendung':
                self.mean.wendung.append(x)

            elif kind == 'abkurzung':
                self.mean.abkurzung += ' ' + x

            else:
                assert 0

            e += 1

        self.ins.defs.append(self.mean)
        return e

    def iterate(self, e):
        if e == len(self.lst) - 1:
            return e, self.lst[e]
        e += 1
        if self.lst[e] in ['Info', 'INFO']:
            e += 1
        return e, self.lst[e]

    def add_def(self, x, kind):
        if self.mean.defn:
            if kind == 'bedeutung2':
                self.mean.defn += f" {x}"
                return
            elif kind == 'bedeutung3':
                self.ins.defs.append(self.mean)
            elif kind == 'grammatik':
                self.ins.defs.append(self.mean)
            elif self.mean and hasattr(self.mean, kind):
                if kind in ['beispiel', 'wendung']:
                    lst = getattr(self.mean, kind)
                    del lst[-1]
                self.ins.defs.append(self.mean)
            else:
                assert 0

        self.mean = duden_def()
        self.mean.defn = x
        self.cls = self.mean

    def test_verb(self):
        self.modals = ['können', 'sollen', 'wollen', 'dürfen',
                       'müssen', 'mögen', 'sein', 'tun', 'wissen']
        self.ignore = ['Praesens']
        self.alt = set()
        b = 0
        self.verb2par = {}
        on = 0
        for self.word, self.lst in self.dwords.items():
            self.get_aword(self.lst[0])

            if not self.word in self.ignore:
                c = 0
                on = 0
                if self.word == 'hauen':
                    bb = 8

                lst = []
                num = 0
                for e, x in en(self.lst):
                    if x == 'Präsens':
                        self.vparadigm(e + 5, num)
                        lst.append(self.vdct)
                        num += 1
                if lst:
                    self.verb2par[self.aword] = lst

            b += 1
        return
