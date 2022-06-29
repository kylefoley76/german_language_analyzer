import add_path
from general import *
import german3 as ge
import german4 as ge4
from german3 import excel_entry
import gtools as gt
import wdg
import parse_duden as pd
import analyze_duden as ad

args = vgf.get_arguments()
args = [0, 'ad']


if args[1] == 'cp':
    ins = ge.review_text()
    ins.calc_progress()
elif args[1] == 'rt':
    ins = ge.read_text()
    ins.main_rt()
elif args[1] == 'cr':
    ge.check_review()
elif args[1] == 't11':
    ge4.temp11()
elif args[1] == 'pt':
    ge4.prepare_test()
elif args[1] == 'bc':
    ins = gt.build_corpus()
    ins.bc_step1(1)
elif args[1] == 't11':
    ge4.temp11()
elif args[1] == 'ld':
    ge4.loop_duden()
elif args[1] == 'pc':
    ge4.parse_cambridge()
elif args[1] == 'uc':
    ge4.use_conjugator()
elif args[1] == 'pl':
    ge4.parse_leo()
elif args[1] == 'lcl':
    ge4.loop_cam_leo()
elif args[1] == 'pd':
    pd.parse_duden()
elif args[1] == 'ad':
    ins = ad.analyze_dudencl()
    ins.main_ad()
    ins.step3('ad')
    ins.step4()
    ins.step5_loop()
    ins.step7()
    ins.s8_ext_ge2()
    ins.test_awdg()
    ins.count_simples()
    # ins.output_file()

elif args[1] == 'ado':
    ## this was just designed to build the genitiv pickle
    ins = ad.analyze_dudencl()
    ins.main_ad('ado')

elif args[1] == 'co':
    # ins = ad.analyze_dudencl()
    # ins.main_ad()
    ins = wdg.analyze_wdg()
    ins.main_wdg()
    # ins.all_nouns()
    ins.ana_comp()
elif args[1] == 'ad2':
    ins = ad.analyze_dudencl()
    ins.alter_capitalization()
    ins.get_word2duden()
elif args[1] == 'dwds':
    ge4.use_dwds('x')
elif args[1] == 'wdg':
    ins = wdg.analyze_wdg()
    # ins.main_wdg()
    # ins.all_nouns()
    ins.step3()
    ins.step4()
    ins.step5_loop()
    ins.step7()
    ins.s8_ext_ge2()
    ins.test_awdg()
    ins.count_simples()

elif args[1] == 'cwdg':
    ins = wdg.analyze_wdg()
    ins.check_compounds()

elif args[1] == 'gw':
    gt.build_corpus()
