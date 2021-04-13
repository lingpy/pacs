from collections import defaultdict
import html
import networkx as nx
from lingpy import *
from clldutils.path import Path
from pyconcepticon.api import Concepticon
import attr

def librarypath(*comps):
    return Path(__file__).parent.parent.joinpath(*comps).as_posix()


def write_gml(graph, fn):
    with open(fn, 'w') as f:
        f.write('\n'.join(html.unescape(line) for line in nx.generate_gml(graph)))

doculects = ['BiaoMin', 'CentralGuizhouChuanqiandian', 'Changsha', 'Chengdu',
        'Chuanqiandian', 'DahuaYantan', 'Dongnu', 'DuAnBaiwang',
        'EasternBahen', 'EasternLuobuohe', 'EasternQiandong', 'EasternXiangxi',
        'GangbeiZhongli', 'Guangzhou', 'Guilin', 'Guiyang', 'Haikou',
        'Jiongnai', 'KimMun', 'Kunming', 'LuzhaiLuzhai', 'MashanBaishan',
        'Meixian', 'Mien', 'Nanning', 'NortheastYunnanChuanqiandian',
        'NorthernQiandong', 'Numao', 'Nunu', 'Pandong', 
        'RenliEasternSandong', 'She', 'ShuigenCentralSandong',
        'SouthernGuizhouChuanqiandian', 'SouthernQiandong', 'Tuoluo',
        'WesternBaheng', 'WesternLuobuohe', 'WesternXiangxi', 'Wuhan',
        'WuxuanHuangmao', 'Xianggang', 'XiangzhouYunjiang', 'XinfengSonaga',
        'XingbinQianjiang', 'Yangjiang', 'Younuo', 'ZaoMin']

# colors for transitions
pcols = {
        'missing': 'white',
        'Hmong-Mien--Sino-Tibetan--Tai-Kadai': 'black',
        'Hmong-Mien': 'Crimson',
        'Sino-Tibetan': 'DodgerBlue',
        'Tai-Kadai': 'Gold',
        'Hmong-Mien--Sino-Tibetan': 'Orchid',
        'Hmong-Mien--Tai-Kadai':    'Orange',
        'Sino-Tibetan--Tai-Kadai':  'Green',
        'singleton': '0.5',
        'Austroasiatic': 'cyan',
        'Austroasiatic--Hmong-Mien': 'darkorchid',
        'Austroasiatic--Sino-Tibetan': 'lawngreen',
        'Austroasiatic--Tai-Kadai': '0.8',
        'Austroasiatic--Hmong-Mien--Sino-Tibetan': 'brown',
        'Austroasiatic--Hmong-Mien--Tai-Kadai': 'darkorange',
        'Austroasiatic--Sino-Tibetan--Tai-Kadai': 'yellow',
        }

