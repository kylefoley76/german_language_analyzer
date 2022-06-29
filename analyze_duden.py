import add_path
from general import *
import spacy
from spacy_iwnlp import spaCyIWNLP
import time, requests, copy
from unidecode import unidecode
from collections import defaultdict
import parse_duden as pd
from wdg import analyze_wdg

failure = 0
folder = '/users/kylefoley/codes/german/'
obra = chr(9001)
cbra = chr(9002)


class analyze_dudencl(analyze_wdg):
    def __init__(self):
        analyze_wdg.__init__(self)

    def main_ad(self, kind='mad'):
        self.load_data_wdg(kind)

        self.simple_verbs()
        # self.get_word2duden()
        self.elim_derived_verbs()
        self.get_nouns()
        self.get_inflected()
        self.alter_capitalization()

    # def load_data(self, kind):
    #     if kind == 'ac':
    #         if not hasattr(self, 'nouns'):
    #             self.nouns = pi.open_pickle(f'{folder}duden_nouns', 1)
    #     elif kind == 'w2d':
    #         if not hasattr(self, 'dparse'):
    #             self.dparse = pi.open_pickle(f'{folder}duden_parsed', 1)
    #
    #     elif kind == 'mad':
    #         self.dwords = pi.open_pickle(f'{folder}duden_filt', 1)
    #         self.dparse = pi.open_pickle(f'{folder}duden_parsed', 1)
    #         self.word2freq = pi.open_pickle(f'{folder}word2freq', 1)
    #         self.pos_dct = to.from_txt2dct_1d(f'{folder}duden_pos')
    #         self.word2duden = to.from_txt2lst_tab_delim(f'{folder}word2duden')
    #         self.word2duden = {x: eval(y) for x, y in self.word2duden}

    def save_data(self, kind):
        if kind == 'w2d':
            to.from_dct2txt_1d(self.word2duden, f'{folder}word2duden')

    def num_vparadigm(self):
        b = 0
        c = 0
        for x, y in self.dparsed.items():
            b += 1

            if hasattr(y, 'vparadigms'):
                for k, v in y.vparadigms.items():
                    for z in v:
                        if ',' in z:
                            c += 1
        p(b)
        p(c)

    def get_inflected(self):
        self.all_words = set()
        self.plurals = set()
        self.genitivs = set()
        for x, y in self.dparsed.items():
            if hasattr(y, 'nparadigm'):
                for k, v in y.nparadigm.items():
                    self.all_words |= set(v)
                    if k == 'np':
                        self.plurals |= set(v)
                    if k in ['gs', 'gp']:
                        self.genitivs |= set(v)

            if hasattr(y, 'vparadigm'):
                for dct in y.vparadigm:
                    for k, v in dct.items():
                        self.all_words |= set(v)
                        if k in ['Partizip I', 'Partizip II']:
                            self.subset |= set(v)
            if hasattr(y, 'aparadigm'):
                self.all_words |= set(y.aparadigm.values())
            if hasattr(y, 'steigerung'):
                self.all_words |= set(y.steigerung)
            for z in y.defs:
                if z.plurals:
                    self.all_words |= set(z.plurals)
                    self.plurals |= set(z.plurals)
                if z.genitivs:
                    self.all_words |= set(z.genitivs)
                    self.genitivs |= set(z.genitivs)

            self.plurals |= set(y.plurals)

        st = set()
        for x in self.plurals:
            if not x:
                pass
            elif x in self.word2duden:
                pass
            elif len(x) == 1 or x[0].islower() or '-' in x or \
                    (len(x) > 1 and bool(re.search(r'[A-Z]', x[1:]))):
                pass
            else:
                st.add(x)
        assert "" not in st
        assert "H" not in st
        self.plurals = st
        st = set()
        for x in self.genitivs:
            if not x:
                pass
            elif x in self.word2duden:
                pass
            elif len(x) == 1 or x[0].islower() or '-' in x or \
                    (len(x) > 1 and bool(re.search(r'[A-Z]', x[1:]))):
                pass
            else:
                st.add(x)
        assert "" not in st
        self.genitivs = st
        pi.save_pickle(self.all_words, f'{folder}duden_all_words', 1)
        pi.save_pickle(self.plurals, f'{folder}duden_plurals', 1)
        pi.save_pickle(self.genitivs, f'{folder}duden_genitivs', 1)
        p(len(self.plurals))

    def simple_verbs(self):
        self.all_verbs = {}
        for x, y in self.dparsed.items():
            if y.pos and y.pos[0] == 'v':
                if " " not in y.aword:
                    if y.aword == 'rennen':
                        bb = 8
                    self.all_verbs[y.aword] = 1
        dct = vgf.sort_dct_keys_by_len(self.all_verbs, 1)
        self.high = len(list(dct.keys())[0]) + 1
        self.low = len(list(dct.keys())[-1])
        self.by_len = {b: set() for b in range(self.high)}
        for k in dct.keys():
            l = len(k)
            self.by_len[l].add(k)
        dct2 = {}
        for num, st in self.by_len.items():
            if st:
                dct2[num] = st
        self.by_len = dct2

        self.simples = {i: set() for i in range(self.low, self.high)}
        self.compounds = {i: set() for i in range(self.low, self.high)}
        self.simples[3] = self.by_len[3]
        self.simples[4] = self.by_len[4]
        self.by_len = self.len_by_end(self.by_len, 1)
        self.by_len_wi = copy.deepcopy(self.by_len)
        dct5 = {}
        dct5['ver'] = self.simples
        self.simples = dct5
        self.compounds['ver'] = self.compounds
        self.step6('ver', 1)

    def get_word2duden(self):
        self.load_data_wdg('w2d')
        self.word2duden = {}
        for x, y in self.dparsed.items():
            self.word2duden.setdefault(y.aword, []).append(x)
        b = 0
        for x, y in self.word2duden.items():
            if len(y) > 1:
                b += 1
        p(f'{b} words with multiple entries')
        self.save_data('w2d')

    def elim_prefix(self, st):
        st = set(v for v in st if not v.endswith('ieren'))
        verbs = copy.deepcopy(st)
        complex = set()
        mcomplex = set()
        other = set()
        for x in st:
            for y in self.prefixes:
                if x.startswith(y):
                    z = x[len(y):]
                    p(z)
                    if z in st:
                        if len(y) > 2:
                            complex.add(x)
                        else:
                            mcomplex.add(x)
                    else:
                        if len(y) > 2:
                            other.add(x)

        dsimple = verbs - complex
        msimple = verbs - (complex | mcomplex)
        dsimple = vgf.sort_lst_by_len(dsimple, 1)
        msimple = vgf.sort_lst_by_len(msimple, 1)
        other = vgf.sort_lst_by_len(other, 1)
        dct1 = {}
        npara = set()
        npara2 = set()
        hpara = set()
        irr = set()
        for x in verbs:
            obj = self.word2duden.get(x)
            if obj:
                for y in obj:
                    ins = self.dparsed.get(y)
                    ins2 = self.dwords.get(y)
                    dct1.setdefault(ins.pos, set()).add(x)
                    if ins.pos in ['vs', 'vss', 'vu']:
                        if not hasattr(ins, 'vparadigms'):
                            npara.add(x)
                            if all(x != 'Präsens' for x in ins2):
                                npara2.add(x)
                            else:
                                hpara.add(x)
                                if all(x != 'Präsens' for x in ins2):
                                    npara2.add(x)
                                else:
                                    hpara.add(x)
                        elif not ins.vparadigms:
                            npara.add(x)
                        irr.add(x)

    def elim_derived_verbs(self):
        st = set()
        for y, x in self.simples['ver'].items():
            st |= x

        self.everbs = st
        actors = set()
        stems = set()
        for e, x in en(self.everbs):
            if x in ['spicken']:
                bb = 8

            lst = self.word2duden[x]
            str2 = f'Indikativ 3 Präsens Singular of {x}'
            str3 = f'Indikativ 1 Präsens Singular of {x}'
            str4 = f'Indikativ 1 Präteritum Singular of {x}'
            lst5 = []
            found = 0
            for y in lst:
                ins = self.dparsed[y]
                if hasattr(ins, 'vparadigms'):
                    lst5 = ins.vparadigms[0][str2]
                    lst6 = ins.vparadigms[0].get(str3, [])
                    lst7 = []
                    if ins.pos in ['vss', 'vs', 'vu']:
                        lst7 = ins.vparadigms[0].get(str4, [])

                    found = 1
                else:
                    if ins.pos in ['vss', 'vs', 'vu']:
                        pass
                        # p(f'{x} has no paradigm')
                    else:
                        if ins.aword[-3:] in ['ern', 'eln']:
                            str6 = ins.aword[:-3]
                            str7 = ins.aword[:-1]
                            stems.add(str7)
                            if ins.aword[-3:] == 'ern':
                                new = f"{str6}ner".capitalize()
                            else:
                                new = f"{str6}ler".capitalize()
                        else:
                            str6 = ins.aword[:-2]
                            stems.add(str6)
                            new = f"{str6}er".capitalize()

                        if new not in self.word2duden:
                            actors.add(new)

                if found:
                    for stem in lst5 + lst6 + lst7:
                        if " " in stem:
                            stem = stem[:stem.index(" ")]

                        if not stem[-1] == 't' and stem in lst5:
                            pass
                            # p(f'in {x} its stem {stem} does not end with t')


                        else:
                            if stem in lst7:
                                pass
                            elif stem[-2:] == 'et':
                                stem = stem[:-2]

                            else:
                                stem = stem[:-1]
                            stems.add(stem)

                            new = ""
                            new2 = ""
                            if x.endswith('eln'):
                                new = stem + 'ler'
                                new2 = stem
                            elif x.endswith('ern'):
                                new = f'{stem}ner'
                                new2 = stem

                            elif x.endswith('en'):
                                new = f'{stem}er'
                            if new2 == 'elnler':
                                bb = 8

                            if new:
                                new = new.capitalize()
                                if new not in self.word2duden:
                                    actors.add(new)
                                else:
                                    pass
                                    if ins.aword[-3:] in ['ern', 'eln']:
                                        pass
                                        # p (f'{new} is in duden')
                                if new2 and x[-3:] in ['ern', 'eln'] and \
                                        new2.capitalize() not in self.word2duden:
                                    actors.add(new2.capitalize())

        lst8 = ['schmetter', 'förder', 'seh', 'trüb', 'exerzier', 'fuhr','schmiss',
                'spick']

        stems |= {'spring', 'sprang'}
        for x in lst8:
            assert x in stems, f"{x} should be in stems"
        # assert 'Elnler' in self.dactors

        self.stems = set(x.capitalize() for x in stems if x.capitalize() not in self.word2duden)
        self.dactors = actors
        to.from_lst2txt(self.dactors, f'{folder}actors')
        self.everbs = set(x.capitalize() for x in self.everbs if x.capitalize() not in self.word2duden)
        to.from_lst2txt(self.everbs, f'{folder}everbs')
        to.from_lst2txt(stems, f'{folder}stems')
        return

    def get_nouns(self):
        # self.load_data_wdg('gn')
        self.nouns = {}
        deviants = {}
        f = 0
        for x, y in self.dparsed.items():
            if y.pos and y.pos[0] == 's' or y.pos == 'js':
                x = y.aword
                if len(x) == 1 or x[0].islower() or '-' in x or " " in x or \
                        (len(x) > 1 and bool(re.search(r'[A-Z]', x[1:]))):
                    deviants[y.word] = y.genders
                    p(f'deviant {y.aword}')
                else:
                    obj = self.nouns.get(y.aword)
                    if obj:
                        obj |= y.genders
                    else:
                        if not y.genders:
                            y.genders = set('z')
                            f += 1
                        self.nouns[y.aword] = y.genders

        assert "" not in self.nouns
        assert "" not in deviants
        assert "H" not in self.nouns
        pi.save_pickle(self.nouns, f'{folder}duden_nouns', 1)
        pi.save_pickle(deviants, f'{folder}deviant_nouns', 1)

    def alter_capitalization(self):
        self.load_data_wdg('ac')
        nspell2ospell = {}
        for x in self.nouns.keys():
            y = x.capitalize()
            if y != x:
                nspell2ospell[y] = x

        p(f'{len(nspell2ospell)} alt spellings')
        to.from_dct2txt_1d(nspell2ospell, f'{folder}nspell2ospell')
