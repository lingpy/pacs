from importlib import import_module
from lingpy import *
from pylexibank.__main__ import configure
from pylexibank.util import pb
from tabulate import tabulate
from collections import defaultdict

families = {
        'Hmong-Mien': 'red', 
        'Indo-European': 'blue', 
        'Sino-Tibetan': 'green', 
        'SinoTibetan': 'green',
        'Tai-Kadai': 'yellow',
        'Austroasiatic': 'cyan',
        }

base = [
	#"allenbai",
	"beidasinitic",
	"beidazihui",
	"castrosui",
	"castroyi",
	"castrozhuang",
	"chenhmongmien",
        "peirossea",
	"housinitic",
	"houzihui",
	"liusinitic",
	"wangbai",
	"yanglalo",
        ]

full = [
	"abrahammonpa",
	"allenbai",
        "bodtnepal",
        "ivanisuansu",
	"backstromnorthernpakistan",
	"beidasinitic",
	"beidazihui",
	"bodtkhobwa",
	"castrosui",
	"castroyi",
	"castrozhuang",
	"chenhmongmien",
	#"gawnetibetan",
	"halenepal",
	"housinitic",
	"houzihui",
	#"lieberherrkhobwa",
	"liusinitic",
	"marrisonnaga",
	"mortensentangkhulic",
	"naganorgyalrongic",
	"peirossea",
	"sagartst",
	#"satterthwaitetb",
	"sohartmannchin",
	"suntb",
	"vanbikkukichin",
	"wangbai",
	"yanglalo",
        ]

selected = [
        "BaotingHlai",
        "BiaoMin", 
        "CentralGuizhouChuanqiandian", 
        "Changsha", 
        "Chengdu", 
        "Chuanqiandian", 
        "DahuaYantan", 
        "Dongnu",
        "DuAnBaiwang", 
        "EasternBahen", #10 
        "EasternLuobuohe", 
        "EasternQiandong",
        "EasternXiangxi", 
        "GangbeiZhongli", 
        "Guangzhou",
        "Guilin", 
        "Guiyang", 
        "Haikou", 
        "Jiongnai",
        "KimMun", 
        "Kunming", 
        "LangjaBuyang",
        "LazhaiNung", 
        "LuzhaiLuzhai", 
        "Maonan", 
        "MashanBaishan",
        "Meixian", 
        "Mien", 
        "Mulam", 
        "Nanning",
        "NortheastYunnanChuanqiandian", 
        "NorthernQiandong", 
        "Numao", 
        "Nunu",
        "Paliu",
        "Pandong", 
        "Qingyun", 
        "RenliEasternSandong", 
        "She", 
        "Shuangfeng",
        "ShuigenCentralSandong", 
        "SouthernGuizhouChuanqiandian",
        "SouthernQiandong", 
        "Tuoluo", 
        "WesternBaheng", 
        "WesternLuobuohe",
        "WesternXiangxi", 
        "Wuhan", 
        "WuxuanHuangmao", 
        "Xianggang",
        "XiangzhouYunjiang", 
        "XinfengSonaga", 
        "XingbinQianjiang", 
        "Yangjiang",
        "Younuo", 
        "ZaoMin"
        ]

header = ["lexibank_id", "concept", "concept_in_source", "chinese_gloss",
        "doculect", "doculect_name", "value", "form", "tokens", "family",
        "subgroup", "structure"
        ]

conf = configure()

def get_languages():
    families = {
        'Hmong-Mien': 'red', 
        'Indo-European': 'blue', 
        'Sino-Tibetan': 'green', 
        'Tai-Kadai': 'yellow',
        'Austroasiatic': 'cyan',
        }
    languages = csv2list('stats/languages-large.tsv', strip_lines=False)
    ld = {language[0]: dict(zip([h.lower() for h in languages[0]], language)) for language in
            languages[1:]}
    for k in ld:
        try:
            ld[k]['longitude'] = float(ld[k]['longitude'])
            ld[k]['latitude'] = float(ld[k]['latitude'])
        except:
            pass
        ld[k]['fcolor'] = families.get(ld[k]['family'], 'black')
    return ld


def modules(which):
    
    return {m: import_module('lexibank_'+m).Dataset() for m in which}


def get_wordlist(dataset):
    """
    Convert a lexibank dataset into a wordlist.
    """
    wl = Wordlist.from_cldf(
            dataset.cldf_dir.joinpath('cldf-metadata.json'),
            columns = [
                'id',
                'concept_concepticon_gloss',
                'concept_name',
                'concept_chinese_gloss',
                'language_id',
                'language_name',
                'value',
                'form',
                'segments',
                'language_family',
                'language_subgroup'
                ],
            namespace = {
                'id': 'lexibank_id',
                'concept_chinese_gloss': 'chinese_gloss',
                'concept_concepticon_gloss': 'concept',
                'language_id': 'doculect',
                'segments': 'tokens',
                'concept_name': 'concept_in_source',
                'language_name': 'doculect_name',
                'language_family': 'family',
                'language_subgroup': 'subgroup'
                }
            )
    return wl


def get_wordlists(which):
    """
    Return wordlists in a dictionary.
    """
    D = {}
    for name, dataset in pb(which.items()):
        D[name] = get_wordlist(dataset)
    return D


def language_table(which, filename='languages.tsv', conf=False):
    """
    Make a table of languages in a combined sample of datasets.
    """
    conf = conf or configure()
    langD = {}
    for dataset, lds in which.items():
        print('Analyzing dataset...{0}'.format(dataset))
        langs = lds.cldf.wl.tablegroup.tabledict['languages.csv']
        for doculect in langs.iterdicts():
            gc = False
            key = dataset+'-'+doculect['ID']
            if doculect['Glottocode']:
                try:
                    key = dataset+'-'+doculect['ID']
                    langD[key] = {'ID': doculect['ID'], 'Dataset': dataset}

                    if doculect['Latitude'] and doculect['Longitude']:
                        langD[key]['Latitude'] = str(doculect['Latitude'])
                        langD[key]['Longitude'] = str(doculect['Longitude'])
                    
                    langD[key]['Glottocode'] = doculect['Glottocode']
                    langD[key]['Name'] = doculect['Name']

                    if not doculect['Family']:
                        gc = conf.glottolog.languoid(doculect['Glottocode'])
                        langD[key]['Family'] = gc.family.name if gc.family else \
                                doculect['ID']
                    else:
                        langD[key]['Family'] = doculect['Family'] or ''
                    
                    if not doculect['Latitude']:
                        gc = gc or conf.glottolog.languoid(doculect['Glottocode'])
                        langD[key]['Latitude'] = str(gc.latitude)
                    
                    if not doculect['Longitude']:
                        gc = gc or conf.glottolog.languoid(doculect['Glottocode'])
                        langD[key]['Longitude'] = str(gc.longitude)
                    
                    langD[key]['SubGroup'] = doculect.get('SubGroup', '') or ''
                    langD[key]['DialectGroup'] = doculect.get('DialectGroup',
                            '') or ''
                    langD[key]['ChineseName'] = doculect.get('ChineseName', '') \
                            or ''
                    print('[i] added {0}'.format(key))
                except:
                    print('[!] problem with {0} {1} {2}'.format(
                        dataset, doculect['Name'], doculect['Glottocode']))
            else:
                if doculect['Latitude'] and doculect['Longitude']:
                    langD[key] = {'ID': doculect['ID'], 'Dataset': dataset}
                    langD[key]['Latitude'] = str(doculect['Latitude'])
                    langD[key]['Longitude'] = str(doculect['Longitude'])
                    langD[key]['Glottocode'] = ''
                    langD[key]['Name'] = doculect['Name']
                    langD[key]['Family'] = doculect.get('Family', '')
                    langD[key]['SubGroup'] = doculect.get('SubGroup', '') or ''
                    langD[key]['ChineseName'] = doculect.get('ChineseName', '') \
                            or ''
                else:
                    print('[!] Skipping {1} missing coordinates...'.format(
                        dataset, key))
    
    header = ['ID', 'Dataset', 'Name', 'ChineseName', 'Glottocode', 'Family', 'SubGroup',
            'Latitude', 'Longitude']
    
    with open(filename, 'w') as f:
        f.write('\t'.join(header)+'\n')
        for val in langD.values():
            try:
                f.write('\t'.join([val.get(h, '') for h in header])+'\n')
            except:
                print('!', val)


def data_table(which, filename='data-summary.tex'):
    """
    Create a table of the data assembled so far.
    """
    print(which)
    table = []
    concepts, languages, words = [], defaultdict(list), 0
    clists = 0
    mods = modules(which)
    wols = get_wordlists(mods)
    print(which)

    for k, v in pb(sorted(mods.items())):
        wl = wols[k]
        table += [[
            v.metadata.title,
            wl.height,
            wl.width,
            len(wl),
            1 if v.metadata.conceptlist else 0
            ]]
        words += len(wl)
        concepts += wl.rows
        for language in wl.cols:
            languages[language] += [k]
        clists += table[-1][-1]
        wl.output('tsv', filename='wordlists/'+k, ignore='all', prettify=False)
    
    table += [['total', len(set(concepts)), len(languages), words ]]
    text = tabulate(table, headers=['Dataset', 'Concepts', 'Languages', 'Words',
        'Conceptlist'], tablefmt='latex')
    print(text)
    with open(filename, 'w') as f:
        f.write(text)


