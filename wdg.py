import add_path
from general import *
import os
import time
import collins
import german4 as ge4
import german3 as ge3
from collections import defaultdict
import pyperclip, pyautogui
import copy
from parse_duden import duden_def, duden_entry

folder = '/users/kylefoley/codes/german/'


class plural_test:
    def __init__(self):
        pass

    def plural_test1(self):
        ## this tests whether a pluraltantum has a gender, passed
        ## no noun which has only one meaning and is a pluraltantum has a gender
        st = set()
        st1 = set()
        for x, y in self.dparsed.items():
            if self.is_noun(y):
                if not y.genders and not y.plural_freq == 'ns':
                    p(f'{x}')
                    st.add(x)
                elif y.plural_freq == 'ns' and not y.genders:
                    st1.add(x)

        return

    def plural_test2(self):
        ## this tests whether a noun is a pluraltantum in one
        # sense but not in another
        for x, y in self.dparsed.items():
            if self.is_noun(y):
                st = set()
                st.add(y.plural_freq)

    def temp20(self):

        st = set()
        for x, y in self.dparsed.items():
            if self.is_noun(y):
                if not y.artikel_freq:
                    y.artikel_freq = 'h'
                    if not y.genders and not y.plural_freq == 'ns':
                        p(f'{x}')
                        st.add(y)

        for x, y in self.dparsed.items():
            if self.is_noun(y):
                st2 = set()
                ofreq = y.artikel_freq
                # if not y.artikel_freq:
                #     y.artikel_freq = 'h'
                #     if not y.genders and not y.plural_freq == 'ns':
                #         p(f'{x}')
                #         st.add(y)

                if len(y.defs) > 1:
                    for defn in y.defs:
                        st2.add(defn.artikel_freq)
                        if not defn.artikel_freq:
                            defn.artikel_freq = 'h'
                            if hasattr(defn, 'genders') and \
                                    not defn.genders:
                                p(f'{x}')

    def get_odd_articles(self):
        self.plural_test1()
        self.pluralt = set()
        self.nplural = set()
        self.no_art = set()
        has_art = set()
        splural = set()

        lst = [self.pluralt, self.nplural, self.no_art]
        lst1 = ['ns', 'np', 'n']
        lst2 = ['plural_freq', 'plural_freq', 'artikel_freq']

        for x, y in self.dparsed.items():
            if y.pos and (y.pos[0] == 's' or y.pos == 'js'):
                for st, str1, att in zip(lst, lst1, lst2):
                    obj = getattr(y, att)
                    if obj == str1:
                        st.add(y.aword)
                    for defn in y.defs:
                        obj = getattr(defn, att)
                        if obj == str1:
                            st.add(y.aword)

        return

    def get_defective_plurals(self):
        for x, y in self.dparsed.items():
            if hasattr(y, 'nparadigm'):
                pass


class second_attempt:
    def __init__(self):
        pass

    def random_ending(self):
        dct1 = defaultdict(int)
        for x in self.all_words:
            if len(x) > 2:
                end = x[-3:]
                dct1[end] += 1

        dct1 = sort_dct_val_rev(dct1)
        b = 0
        c = 0
        for x, y in dct1.items():
            c += y
            b += 1
            if b > 50:
                break


class compounds:
    def __init__(self):
        self.fugen = ['ens', 'er', 'es', 'en', 'ns', 's', 'e', 'n']
        self.prefixes = to.from_txt2lst(f'{folder}prefixes')
        self.prefixes = [x[:-1] for x in self.prefixes if x.endswith('-') and x[0].islower()]
        self.prefixes = vgf.sort_lst_by_len(self.prefixes, 1)

    def main_loop(self):
        self.wrong = {}
        by_stem = {}
        by_prefix = {}
        by_oword = {}
        right = {}
        for word, final in self.comp2final.items():
            initial = word[:len(word) - len(final)]
            bool1, initial2 = self.main_co2(initial)
            if not bool1:
                self.wrong[word] = final
            elif bool1 == 1:
                right[word] = [initial2, final]
            elif bool1 == 2:
                by_stem[word] = [initial2, final]
            elif bool1 == 3:
                by_prefix[word] = [initial2, final]
            elif bool1 == 4:
                by_oword[word] = [initial2, final]

        self.by_fugen()
        self.ana_wrong()
        return

    def main_co(self, word, final, verb):
        initial = word[:len(word) - len(final)]
        bool1, _ = self.main_co2(initial, 1, verb)
        if bool1:
            return 1

        if not verb:
            for fug in self.fugen:
                if initial.endswith(fug) and initial != fug:
                    word1 = initial[:-len(fug)]
                    bool1, _ = self.main_co2(word1, 0, verb)
                    if bool1 in [1, 2, 4]:
                        return 1

    def triples(self, initial):
        for x, y in self.by_len_wi.items():
            if initial.endswith(x):
                b = len(initial)
                c = b - 2
                for i in range(2, c, -1):
                    pass




    def main_co2(self, initial, prefix=1, verb=0):
        if verb:
            initial = initial.capitalize()
        linitial = initial.lower()

        if prefix and linitial in self.prefixes:
            return 3, initial
        # elif initial in self.nouns and not verb:
        #     return 1, initial
        elif not verb and initial in self.only_initials:
            return 4, initial
        elif linitial in self.adjectives:
            return 5, initial
        elif linitial in self.prepositions:
            return 5, initial

        return 0, initial

    def by_fugen(self):
        self.by_fug = {}
        self.still_wrong = {}
        for word, final in self.wrong.items():
            initial = word[:len(word) - len(final)]

            for fug in self.fugen:
                if initial.endswith(fug) and initial != fug:
                    word1 = initial[:-len(fug)]
                    bool1, initial = self.main(word1, 0)
                    if bool1 in [1, 2, 4]:
                        self.by_fug[word] = [initial, final]
                        break
            else:
                self.still_wrong[word] = [initial, final]
        return

    def ana_wrong(self):
        st = set(y[0] for x, y in self.still_wrong.items())
        by_fug = set()
        still_wrong = set()
        for word in st:
            for fug in self.fugen:
                if word.endswith(fug):
                    word1 = word[:-len(fug)]
                    bool1, words = self.main(word1)
                    if bool1 in [1, 2, 4]:
                        by_fug.add(word)
                    else:
                        still_wrong.add(word)

        return


    def triple_compunds(self):
        st = set(x for x in self.all_simples if len(x) > 7)
        triples = {}
        still_simple = set()
        for word in st:
            st1 = self.comp2poss.get(word)
            if st1:
                for final in st1:
                    initial = word[:len(word) - len(final)]


                else:
                    still_simple.add(word)


class analyze_wdg(compounds):
    def __init__(self):
        compounds.__init__(self)
        self.comp2final = {}
        self.comp2poss = {}
        self.abb_gen = {
            'der': 'm',
            'die': 'f',
            'das': 'n'
        }

    def main_wdg(self):
        file = f'{folder}wdg'
        self.lst = to.from_txt2lst(file, 1)
        self.lst = list(set(x.strip() for x in self.lst if bool(re.search(r'\S', x))))
        self.wdg_words = []

        for x in self.lst:
            if ',' in x:
                idx = x.index(',')
                suffix = x[idx + 1:]
                suffix = suffix.strip()
                word = x[:idx]
                self.wdg_words.append([word, suffix])
            else:
                x = x.strip()
                self.wdg_words.append([x, ""])

        self.fix_words()

        return

    def fix_words(self):
        dct = {}
        b = 0
        for word, suff in self.wdg_words:
            if word[-1].isdigit():
                word = word[:-1]
                b += 1
            if word in self.word2freq:
                suff1 = dct.get(word)
                if not suff1 and suff:
                    dct[word] = suff
                elif not suff and suff1:
                    dct[word] = suff1
                elif not suff and not suff1:
                    dct[word] = ""
                elif suff1 == suff:
                    dct[word] = suff

                elif suff1 != suff:
                    dct[word] = f'{suff}, {suff1}'
                    p(f'{word} {suff}, {suff1}')

        self.wdg_words = dct
        to.from_dct2txt_1d(self.wdg_words, f'{folder}wdg_words')

    def all_nouns(self):
        self.wdg_words = to.from_txt2dct_1d(f'{folder}wdg_words')
        self.nouns = {}

        for x, y in self.wdg_words.items():
            if bool(re.search(r'^(der|die|das)', y)) or \
                    bool(re.search(r'(der|die|das)$', y)):
                lst = []
                for k, v in self.abb_gen.items():
                    if k in y:
                        lst.append(v)

                self.nouns[x] = lst

        pi.save_pickle(self.nouns, f'{folder}nouns', 1)

    def add_words(self):
        self.nouns['Mädchen'] = {'n'}
        self.eless = set(x[:-1] for x in self.nouns if x[-1] == 'e')
        self.enless = set(x[:-2] for x in self.nouns if x[-2:] == 'en')
        for x in ['Beamten', 'Giro', 'Gams', "Gurgel"]:
            self.duden_genitivs.add(x)

        ini = [self.duden_plurals, self.duden_genitivs, self.eless,
               self.everbs, self.stems, self.dactors, self.enless]
        finals = [self.duden_plurals,
                  self.everbs, self.stems, self.dactors]

        self.only_initials = set(self.nouns.keys())
        self.only_finals = set(self.nouns.keys())

        for st in ini:
            self.only_initials |= st
            for z in st:
                if len(z) > 2 or z == 'Öl':
                    assert z[0].isupper()
                    self.only_initials.add(z)

        for st in finals:
            self.only_finals |= st
            for z in st:
                if len(z) > 2 or z == 'Öl':
                    assert z[0].isupper()
                    self.only_finals.add(z)

        assert 'Mädchen' in self.only_initials
        e_adj = set(x[:-1] for x in self.adjectives if x[-1] == 'e')
        en_adj = set(x + 'n' for x in self.adjectives if x[-1] == 'e')
        en_add = set(x + 'en' for x in self.adjectives if x[-1] != 'e')
        self.adjectives = self.adjectives | e_adj | en_add | en_adj
        for x in ['soft', 'interzonen', 'spezial', 'pyrrhus',
                  'höchst', 'vorder']:
            self.adjectives.add(x)

        return

    def load_data_wdg(self, kind):
        if kind in ['s3', 'co', 'mad', 'ado']:
            self.word2freq = pi.open_pickle(f'{folder}word2freq', 1)
            self.everbs = set(to.from_txt2lst(f'{folder}everbs'))
            self.nouns = pi.open_pickle(f'{folder}duden_nouns', 1)
            self.nouns = {x: y for x, y in self.nouns.items() if len(x) > 2
                          or x == 'Öl'}
            self.duden_plurals = pi.open_pickle(f'{folder}duden_plurals', 1)
            if kind != 'ado':
                self.duden_genitivs = pi.open_pickle(f'{folder}duden_genitivs', 1)
            self.dparsed = pi.open_pickle(f'{folder}duden_parsed', 1)
            self.dactors = set(to.from_txt2lst(f'{folder}actors'))
            self.word2duden = to.from_txt2dct_1d(f'{folder}word2duden')
            for x, y in self.word2duden.items():
                self.word2duden[x] = eval(y)
            self.gen_suff = to.from_txt2lst(f'{folder}gender_suffix', 1)
            self.nouns['Mädchen'] = set('n')
            self.nouns['Parmäne'] = set('f')
            self.adjectives = set()
            for word, ins in self.dparsed.items():
                if ins.pos and ins.pos == 'j':
                    self.adjectives.add(ins.aword)

            self.stems = set(to.from_txt2lst(f'{folder}stems'))
            self.get_prepositions()

        if kind == 'co':
            self.compounds = to.from_txt2lst(f'{folder}compounds')
            self.comp2final = to.from_txt2dct_1d(f'{folder}comp2final')
        if kind == 'mad':
            self.pos_dct = to.from_txt2dct_1d(f'{folder}duden_pos')

    def get_prepositions(self):
        self.prepositions = set()
        for word, ins in self.dparsed.items():
            if ins.pos and ins.pos in ['pp', 'a']:
                self.prepositions.add(ins.aword)
        self.prepositions = self.prepositions - set(self.prefixes)

    def ana_comp(self):
        self.load_data_wdg('co')
        self.add_colors()
        self.main_loop()

    def add_colors(self):
        lst = ['Rot', 'Grün', 'Schwarz', 'Blau', 'Gelb',
               'Braun', 'Rosa', 'Weiß', 'Grau']
        self.nouns['Orange'] = {'f', 'n'}
        self.nouns['Purpur'] = {'m'}
        self.nouns['Gymnast'] = {'m'}  # in wdg but did not get scraped
        for x in lst:
            self.nouns[x] = set('n')

    def is_noun(self, y):
        if y.pos and (y.pos[0] == 's' or y.pos == 'js'):
            return 1

    def step3(self, kind='s3'):
        if kind != 'ad':
            self.load_data_wdg(kind)
        self.add_colors()
        self.onouns = len(self.nouns)
        self.suff2gen = {}
        for x in self.gen_suff:
            if x.startswith('zzz'):
                break
            if x and ' ' in x:
                x = x.strip()
                idx = x.index(' ')
                suff = x[1:idx]
                str1 = x[idx + 1:]
                idx1 = str1.index(' ')
                gen = str1[:idx1]
                if "/" in gen:
                    gen = gen.split('/')
                    gen = [self.abb_gen[y] for y in gen]
                    self.suff2gen[suff] = gen

                elif 'aber:' in gen:
                    idx2 = str1.index('aber:')
                    str2 = str1[idx2 + 5:]
                    idx3 = str2.index(' ')
                    gen = self.abb_gen[gen]
                    gen1 = str2[:idx3].strip()
                    gen1 = self.abb_gen[gen1]
                    self.suff2gen[suff] = [gen, gen1]
                else:
                    gen = self.abb_gen[gen]
                    self.suff2gen[suff] = [gen]

        self.suff2gen = vgf.sort_dct_keys_by_len(self.suff2gen, 1)

    def step4(self):  # reg = 17503
        self.add_words()
        self.suff2noun = {}
        self.regular = {}
        self.within_dct = {}
        self.just_nouns = set(self.nouns.keys())
        self.cat_by_suff(self.just_nouns, self.regular)
        self.cat_by_suff(self.only_finals, self.within_dct)
        return

    def cat_by_suff(self, st, dct):
        b = 0
        for x in st:
            for suff in self.suff2gen.keys():
                if x.endswith(suff):
                    dct.setdefault(suff, set()).add(x)
                    break
            else:
                dct.setdefault("var", set()).add(x)

            vgf.print_intervals(b, 500)
            b += 1
        return

    def iser(self, x):
        if x.endswith('er'):
            z = f'{x}in'
            if z in self.word2freq:
                return True

    def remove_umlaut(self, str1):
        dct = {
            'Ä': 'A',
            'Ö': 'O',
            'Ü': 'U',
            'ä': 'a',
            'ö': 'o',
            'ü': 'u'
        }
        c = len(str1) - 1
        for d in reversed(str1):
            g = dct.get(d)
            if d in ['e', 'i'] and not str1[-2:] == 'er':
                return str1
            if g:
                str1 = replace_at_i(c, str1, g)
                return str1
            c -= 1

        return str1

    def isin(self, x):
        if x.endswith('in'):
            if bool(re.search(r'(ein|uin|ain)$', x)):
                return 0
            else:
                z = x[:-2]
                w = x[:-2] + 'e'
                u = x[:-2] + 'er'
                y = self.remove_umlaut(x[:-2])
                t = y + 'e'
                lets = [z, w, u, y, t]
                if any(b in self.nouns for b in lets):
                    return 1

    def get_verbal_nouns(self):
        vn = set()
        nvn = set()
        dct1 = {'m': 0, 'f': 0, 'n': 0, 'z': 0}
        dct2 = {'m': 0, 'f': 0, 'n': 0, 'z': 0}
        for x in self.simples['en']:
            lst = self.word2duden.get(x.lower())
            found = 0
            if lst:
                for y in lst:
                    ins = self.dparsed[y]
                    if ins.pos and ins.pos[0] == 'v':
                        vn.add(x)
                        gens = self.nouns.get(x)
                        for gen in gens:
                            dct1[gen] += 1
                        found = 1
                        break

            if not found:
                nvn.add(x)
                gens = self.nouns.get(x)
                for gen in gens:
                    dct2[gen] += 1

    def prepare_simples(self):
        self.simples = {}
        self.compounds = {}
        for suff in self.regular.keys():
            self.simples[suff] = {}
            self.compounds[suff] = {}
            for i in range(2, 33):
                self.simples[suff][i] = set()
                self.compounds[suff][i] = set()

    def step5_loop(self):
        self.by_len = {}
        self.by_len_wi = {}

        self.prepare_simples()
        for x, y in self.regular.items():
            # x = 'var'
            # y = self.regular[x]
            wst = self.within_dct[x]
            self.by_len = self.step5(y, x, self.by_len)
            self.by_len_wi = self.step5(wst, x, self.by_len_wi, 0)

            if x == 'var':
                self.simples['var'][2] = {"Öl"}
                self.by_len[2] = {"öl": {'Öl'}}
                assert 'Wind' in self.by_len[4]['ind']
            self.step6(x)
            self.by_len = {}
            self.by_len_wi = {}

        self.check_step6()
        return

    def step5(self, lst, suff, dct4, first=1):
        lst = vgf.sort_lst_by_len(lst)
        start = len(lst[0])
        stop = len(lst[-1]) + 1
        for k in lst:
            l = len(k)
            st = dct4.get(l)
            if not st:
                dct4[l] = {k}
            else:
                dct4[l].add(k)

        if first:
            for i in range(start, start + 2):
                st = dct4.get(i)
                if st:
                    self.add2dict(self.simples, suff, i, st)

        return self.len_by_end(dct4)

    def len_by_end(self, dct4, verb=0):
        c = 3 if not verb else 4
        new_dct = {}
        for x, y in dct4.items():
            d = c
            if x == 3 and verb:
                d = 3
            dct = {}
            for z in y:
                end = z[-d:].lower()
                dct.setdefault(end, set()).add(z)
            new_dct[x] = dct
        return new_dct

    def step6(self, suff, verb=0):
        start = list(self.by_len.keys())[0]
        for num, dct in self.by_len.items():
            if num > start + 1:
                p(f'{suff} {num}')
                for end, st in dct.items():
                    end1 = end[1:]
                    for self.word in st:
                        # word = 'Sprechtheater'
                        self.step6b(end, end1, num, suff, verb)

        return

    def step6b(self, end, end1, num, suff, verb):
        for n in range(num - 2, 1, -1):
            obj = self.by_len_wi.get(n)
            if obj:
                if n == 2:
                    st1 = obj.get(end1, set())
                else:
                    st1 = obj.get(end, set())

                for k in st1:
                    if self.word == 'Freiluftmuseum' and \
                            k == 'Museum':
                        bb = 8

                    self.tword = k
                    if self.word.endswith(k.lower()):
                        if self.main_co(self.word, k, verb):
                            self.comp2final[self.word] = k
                            if self.word in self.comp2poss:
                                del self.comp2poss[self.word]
                            self.add2dict(self.compounds, suff, num, {self.word})
                            return
                        else:
                            self.comp2poss.setdefault(self.word, set()).add(k)

        self.add2dict(self.simples, suff, num, {self.word})

    def check_step6(self):
        assert 'Wind' in self.simples['var'][4]
        assert 'Mut' in self.simples['var'][3]
        assert 'Wehmut' not in self.simples['var'][6]
        assert 'Not' in self.simples['var'][3]
        assert 'Seenot' not in self.simples['var'][6]
        assert 'Zimtöl' not in self.simples['var'][6]

    def add2dict(self, dct, suff, l, st):
        st1 = dct[suff][l]
        st1 |= st

    def decompose_dcts(self):
        b = 0
        for dct in [self.simples, self.compounds]:
            dct1 = {}
            st1 = set()
            for x, y in dct.items():
                st = set()
                for k, v in y.items():
                    st |= v
                dct1[x] = st
            for x, y in dct1.items():
                st1 |= y

            dct = dct1
            if not b:
                self.simples = dct
                self.all_simples = st1
            else:
                self.all_compounds = st1
                self.compounds = dct
            b += 1

    def step7(self):
        pure_in = to.from_txt2lst(f'{folder}pure_in')
        pure_in = set(x[:-1] for x in pure_in if "*" in x)
        self.decompose_dcts()

        self.simples['in'] = self.simples['in'] - pure_in
        self.simples['in*'] = pure_in
        st4 = set()
        st5 = set()
        for x in self.simples['er']:
            if self.iser(x):
                st4.add(x)
        for x in self.simples['in']:
            if self.isin(x):
                st5.add(x)
        assert "Bataillonsführer" not in self.simples['er']
        self.simples['er'] = self.simples['er'] - st4
        self.simples['in'] = self.simples['in'] - st5
        self.simples['er*'] = st4
        self.simples['in*'] = st5

    def s8_ext_ge2(self):
        lst = ['lass', 'ose', 'use', 'e', 'var']
        self.simples['Ge'] = set()
        for x in lst:
            st = self.simples[x]
            to_remove = set()
            for z in st:
                if z[:2] == 'Ge':
                    self.simples['Ge'].add(z)
                    to_remove.add(z)
            for w in to_remove:
                st.remove(w)

    def test_awdg(self):
        lst = ['Trübsinn', 'Sehkraft', 'Exerzierplatz', 'Verhaltensnorm',
               'totenkopf', 'Namensschild', 'Himbeergeschmack', 'Violinkonzert',
               'Vorderrad', 'Zwischentext', 'Höchstgewinn', 'Pfingstmontag',
               'Förderunterricht', 'Dummenfang', 'Schmetterball', 'Operationsbasis',
               'Abfuhr', 'Rausschmiss','Spezialfach, Interzonenzug',
               'botanisiertrommel','Mädchenherz','Beamtenrecht']

        for x in lst:
            if x in self.all_simples:
                p(f'{x} should not be in simples')
        to.from_lst2txt(self.simples['var'],f'{folder}temp20')
        vgf.open_txt_file(f'{folder}temp20')
        return

    def research_ge(self, by_perc):
        dct3 = {'er*': ['m'], 'in*': ['f']}
        percent = lambda x, y: int(round(x / (x + y), 2) * 100)
        dct1 = {}
        dct2 = {}
        for x, y in by_perc.items():
            if y != 100:
                st = self.simples[x]
                if x not in ['er*', 'in*']:
                    target = self.suff2gen.get(x)
                else:
                    target = dct3.get(x)

                right = 0
                wrong = 0
                right2 = 0
                wrong2 = 0
                perc1 = -1
                perc2 = -1

                for z in st:
                    if z.startswith('Ge'):
                        gens = self.nouns.get(z)
                        lst2 = [z, gens]
                        for gen in gens:
                            if gen == 'n':
                                right += 1
                            else:
                                wrong += 1
                            if gen in target:
                                right2 += 1
                            else:
                                wrong2 += 1

                        dct1.setdefault(x, []).append(lst2)
                if right + wrong > 0:
                    perc1 = percent(right, wrong)
                if right2 + wrong2 > 0:
                    perc2 = percent(right2, wrong2)

                dct2[x] = [perc1, perc2, right + wrong]

    def count_simples(self):
        b = len(self.all_simples)
        c = len(self.all_compounds)
        p(f'{b} simples {c} compounds')
        total_nouns = b + c
        p(f'{total_nouns} should equal {self.onouns}')
        p(f'various {len(self.simples["var"])}')
        self.stats()
        self.prepare_ana_comp()
        return

    def prepare_ana_comp(self):
        to.from_lst2txt(self.all_compounds, f'{folder}compounds')
        to.from_dct2txt_1d(self.comp2final, f'{folder}comp2final')
        pi.save_pickle(self.comp2poss, f'{folder}comp2poss', 1)

    def output_file(self):
        c = 0
        for dct in [self.simples, self.compounds]:
            sst = []
            for x, y in dct.items():
                f = 20 if c else 10

                if len(y) > f:
                    for i, z in en(y):
                        if i > f:
                            break
                        if c:
                            if len(z) < 17:
                                sst.append([z, self.comp2final[z]])
                        else:
                            sst.append(z)
                else:
                    if not c:
                        sst += list(y)
                    else:
                        for z in y:
                            if len(z) < 17:
                                sst.append([z, self.comp2final[z]])

            if not c:
                to.from_lst2txt(sst, f"{folder}test_simples")
                vgf.open_txt_file(f"{folder}test_simples")
            else:
                to.from_lst2txt_tab_delim(sst, f"{folder}test_compounds")
                vgf.open_txt_file(f"{folder}test_compounds")
            c += 1

    def simple_score(self, corr_num):
        right2 = 0
        right3 = 0
        dct3 = {'er*': ['m'], 'in*': ['f'], 'Ge': ['n']}
        wrong = 0
        for x, y in corr_num.items():
            if x not in ['er*', 'in*', 'Ge']:
                suff = self.suff2gen[x]

            else:
                suff = dct3.get(x)

            if len(suff) == 2:
                right2 += y[0]  # 755
            else:
                right3 += y[0]  # 7646
            wrong += y[1]

        total = right2 + right3 + wrong  # 10699, real total 16162
        # len(self.all_simples)
        allpos = total * 3
        eliminated = right2 + (right3 * 2)
        to_eliminate = allpos - total
        perc_elim = int(round(eliminated / to_eliminate, 2) * 100)
        p(f'simples eliminated {perc_elim}')
        self.compound_stats()

    def compound_stats(self):
        exac = 0
        subset = 0
        superset = 0
        wrong = 0
        intersection = 0
        total = 0
        dct = {}
        lst = ['duden_plurals', 'everbs', 'stems', 'dactors']
        dct_gen = {x: defaultdict(int) for x in lst}
        other = set()
        stems_wo_gen = set()
        stems_wo_gen2 = {x:{} for x in lst}
        odd_plurals = defaultdict(int)
        odd_plurals2 = {}

        for x in self.all_compounds:
            gens = self.nouns[x]
            ifinal = self.comp2final.get(x)
            if ifinal:
                cgens = self.nouns.get(ifinal)
                if not cgens:
                    stems_wo_gen.add(ifinal)
                    for y in lst:
                        st = getattr(self, y)
                        if ifinal in st:
                            obj = stems_wo_gen2.get(y)
                            lst3 = list(gens)
                            lst3.sort()
                            tpl = tuple(lst3)
                            obj.setdefault(ifinal, set()).add(tpl)
                            dct.setdefault(y, set()).add(ifinal)
                            for gen in gens:
                                dct_gen[y][gen] += 1
                            if y == 'duden_plurals':
                                if "z" not in gens:
                                    odd_plurals.setdefault(ifinal, set()).add(tpl)
                                    odd_plurals2.setdefault(ifinal, []).append(x)

                            break
                    else:
                        other.add(ifinal)

                else:
                    total += 1
                    if cgens == gens:
                        exac += 1
                    elif cgens.issubset(gens):
                        subset += 1
                    elif cgens.issuperset(gens):
                        superset += 1
                    elif cgens & gens:
                        intersection += 1
                    else:
                        wrong += 1
        exact = int(round(exac / total, 2) * 100)
        almost = int(round((exac + subset) / total, 2) * 100)
        almost2 = int(round((exac + subset + superset + intersection) / total, 2) * 100)
        p(f"""
        exact: {exact}
        almost: {almost}
        almost2: {almost2}
        """)
        p (f'stems without gender {len(stems_wo_gen)}')
        for x, y in dct_gen.items():
            p(x, y)

        # exact = 89, almost = 90, almost2 = 95
        # 90 ,90 96
        # 93 ,93 98
        # 94 94 99
        # same score as second time
        # exact = 28599 total 32049
        # complete score, sright 16047 stotal 32324
        return

    def one_syll(self):
        syl1 = {'m': 0, 'f': 0, 'n': 0}
        oth = {'m': 0, 'f': 0, 'n': 0}
        nrule = set()
        nrule2 = set()
        rule = set()
        for x in self.simples['var']:
            if not x.startswith('Ge') and not x.endswith('öl'):
                lst = self.word2duden[x]
                obj = self.dparsed[lst[0]]
                syl = len(obj.syllables)
                gens = obj.genders
                if syl == 1 and \
                        bool(re.search(r'[^aeiouöäü]$', x)):
                    if 'f' in gens or 'n' in gens:
                        nrule.add(x)
                    else:
                        rule.add(x)

        ## syl = 676, 130, 202  67% masculine
        ## syl2 = 640, 120, 178, not begin with vowel
        ## other = 614 233 442

    # 16162 simples, 35777 compounds, 51939 total, 55711 nouns
    # 95 categories, 3152 various
    # various 2583
    # 13416 simples, 38523compounds
    # 13393 simples, 38523compounds
    # 13441 simples, 38523compounds
    # 18716 simples, 33254compounds, various 3978
    # 16888 simples, 35105 compounds, various 3300
    # 16567 simples, 35426 compounds, various 3169
    # 16420 simples, 35466 compounds, various 3099
    # 50, 71, 82, 87, 85, 87

    def stats(self):
        correctness = {}
        corr_num = {}
        dct3 = {'er*': ['m'], 'in*': ['f'], 'Ge': ['n']}
        suff_stats = {}
        for x, y in self.simples.items():
            if not x == 'var':
                dct = {'m': 0, 'f': 0, 'n': 0, 'z': 0, 'p': 0, 'x': 0}
                if x not in ['er*', 'in*', 'Ge']:
                    target = self.suff2gen.get(x)
                else:
                    target = dct3.get(x)

                right = []
                wrong = []
                for z in y:
                    gens = self.nouns[z]
                    for gen in gens:
                        dct[gen] += 1
                    if len(target) == 1:
                        if set(target) == set(gens):
                            right.append(z)
                        else:
                            wrong.append(z)
                    else:
                        if gens.issubset(set(target)):
                            right.append(z)
                        else:
                            wrong.append(z)
                suff_stats[x] = dct
                correctness[x] = [right, wrong]
                corr_num[x] = [len(right), len(wrong)]

        by_perc = {}
        by_num = {}
        for x, y in corr_num.items():
            by_num[x] = y[0] + y[1]
            try:
                perc = int(round(y[0] / (y[0] + y[1]), 2) * 100)
                by_perc[x] = perc
            except:
                by_perc[x] = 0

        by_perc = sort_dct_val_rev(by_perc)
        by_num = sort_dct_val_rev(by_num)
        for x, y in by_perc.items():
            p(x, y)

        p("""
        by number
        """)

        for x, y in by_num.items():
            p(x, y)
        self.simple_score(corr_num)
        return

        # for x, y in suff_stats.items():
        #     p(f'{x} {y["m"]} {y["f"]} {y["n"]}')

    def research(self):
        dct = {}
        for x in ['eis', 'uis', 'ais', 'is']:
            dct[x] = defaultdict(int)
        for x in self.simples['is']:
            gens = self.nouns.get(x)
            if bool(re.search(r'(e|u|a)is$', x)):
                for k, v in dct.items():
                    if x.endswith(k):
                        for gen in gens:
                            dct[k][gen] += 1
            else:
                for gen in gens:
                    dct['is'][gen] += 1

    def temp17(self):
        lst = to.from_txt2lst(f'{folder}no_rule')
        dct = {}
        for x in lst:
            if x and x != 'zzz':
                if "?" in x:
                    y = x[:-2]
                else:
                    y = re.sub(r'[\*\|]', '', x)
                dct[y] = x
        dct1 = {}
        for x, y in dct.items():
            if x != y:
                dct1[x] = y
        dct2 = {}
        for x, y in dct1.items():
            dct2[x] = self.nouns.get(x)

    def eval_actors(self, x):

        dct1 = {}
        right = []
        wrong = []
        st = set()
        for x, y in self.comp2final.items():
            if y in self.dactors:
                gen = self.nouns.get(x)
                if gen:
                    if gen == {'m'}:
                        right.append(x)
                    else:
                        wrong.append(x)
                        st.add(y)

    def get_herkunft(self):
        b = 0
        dct1 = {
            'griechisch': 'g',
            'latein': 'l',
            'französich': 'f',
            'englisch': 'e',
            'amerikanisch': 'e',
            'spanisch': 's',
            'italienisch': 'i',
            'deutsch': 'd'}

        self.word2herkunft = {}
        self.lang2gender = {}
        self.lang2sent = {}
        self.lang2num = {}
        for x, y in dct1.items():
            self.lang2num[x] = {'m': 0, 'f': 0, 'n': 0}

        no_herkunft = set()
        for y in st3:
            lst1 = word2duden[y]
            lst2 = []
            for x in lst1:
                obj = self.dparse[x]
                if obj.herkunft and obj.pos and (obj.pos[0] == 's' or obj.pos == 'js'):
                    for l, a in dct1.items():
                        if l in obj.herkunft.lower():
                            gen = obj.genders
                            d = [obj.aword, gen]
                            g = [obj.aword, obj.herkunft]
                            self.lang2sent.setdefault(l, []).append(g)
                            self.lang2gender.setdefault(l, []).append(d)
                            for ge in gen:
                                self.lang2num[l][ge] += 1

                            break
                    else:
                        no_herkunft.add(x)

    def prepare_lookup(self):
        kind = 'reg_'
        self.simples3 = pi.open_pickle(f'{folder}{kind}simples3', 1)
        word2freq = pi.open_pickle(f'{folder}word2freq', 1)
        simples2 = {}
        freq = []
        rare = []
        obvious = ['keit', 'heit', 'ness', 'ismus', 'tät', 'schaft']

        for x, y in self.simples3.items():
            dct = {}
            for z in y:
                if all(not z.endswith(v) for v in obvious):
                    dct[z] = word2freq[z]
            dct = sort_dct_val(dct)
            l = len(dct)
            t = int(l * .4)
            lst = list(dct.keys())
            freq += lst[:t]
            rare += lst[t:]

        if kind:
            lst2 = to.from_txt2lst(f'{folder}duden_lookup')
            lst2 += freq + rare
        else:
            lst2 = freq + rare

        to.from_lst2txt(lst2, f'{folder}duden_lookup')

    def prepare_non_nouns(self):
        word2freq = pi.open_pickle(f'{folder}word2freq', 1)
        self.wdg_words = to.from_txt2dct_1d(f'{folder}wdg_words')
        self.all_words = set(self.wdg_words.keys())
        already = to.from_txt2lst(f"{folder}duden_lookup")
        rem = self.all_words - set(already)
        dct = {}
        for x in rem:
            if len(x) > 1:
                b = word2freq.get(x)
                if b:
                    dct[x] = b
        dct = sort_dct_val(dct)
        lst = list(dct.keys())
        already += lst
        to.from_lst2txt(already, f"{folder}duden_lookup")
