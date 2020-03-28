#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import string
import traceback

sjeng2onset = {
        u'幫': lambda s: (s[1:3] == u'合三' and s[0] != u'梗' or s[1:3] == u'開三' and (s[0] == u'通' or s[4] == u'尤')) and 'f' or 'b',
        u'滂': lambda s: (s[1:3] == u'合三' or s[1:3] == u'開三' and (s[0] == u'通' or s[4] == u'尤')) and 'f' or 'p',
        u'並': lambda s: (s[1:3] == u'合三' or s[1:3] == u'開三' and (s[0] == u'通' or s[4] == u'尤')) and 'f' or (s[3] == u'平' or s[3:5] == u'上支') and 'p' or 'b',
        u'明': lambda s: not (s[1:3] == u'合三' and s[3:5] != u'上凡') and 'm' or '',
        u'端': lambda s: s[3:5] != u'上覃' and 'd' or 't',
        u'透': lambda s: 't',
        u'定': lambda s: s[3] == u'平' and 't' or 'd',
        u'泥': lambda s: 'n',
        u'來': lambda s: 'l',
        u'知': lambda s: 'zh',
        u'徹': lambda s: 'ch',
        u'澄': lambda s: s[3] == u'平' and 'ch' or 'zh',
        u'娘': lambda s: 'n',
        u'精': lambda s: (s[2] in u'三四' and s[0] not in u'通止' and s[:2] != u'蟹合') and 'j' or 'z',
        u'清': lambda s: (s[2] in u'三四' and s[0] not in u'通止' and s[:2] != u'蟹合') and 'q' or 'c',
        u'從': lambda s: s[3] == u'平' and (s[2] in u'三四' and s[0] not in u'通止' and 'q' or 'c') or (s[2] in u'三四' and s[0] not in u'通止' and 'j' or (s[:4] == u'止合三去' and 'c' or (s[3:5] == u'去寒' and 's' or 'z'))),
        u'心': lambda s: (s[2] in u'三四' and s[0] not in u'通止' and s[:2] != u'蟹合') and 'x' or 's',
        u'邪': lambda s: (s[2] in u'三四' and s[0] not in u'通止' and s[:2] != u'蟹合') and 'x' or 's',
        u'莊': lambda s: 'zh',
        u'初': lambda s: 'ch',
        u'崇': lambda s: s[3] == u'平' and 'ch' or ((s[3] == u'上' or (s[3] == u'去' and (s[0] in u'通江止' or s[:2] == u'山合'))) and 'sh' or 'zh'),
        u'生': lambda s: 'sh',
        u'俟': lambda s: s[3] == u'平' and 'ch' or 'sh',
        u'章': lambda s: 'zh',
        u'昌': lambda s: 'ch',
        u'常': lambda s: s[3] == u'平' and 'ch' or ((s[2] == u'三') and 'sh' or 'zh'),
        u'書': lambda s: 'sh',
        u'船': lambda s: s[3] == u'平' and 'ch' or 'sh',
        u'日': lambda s: s[:2] != u'止開' and 'r' or '',
        u'見': lambda s: (s[2] in u'三四' and not (s[1] == u'合' and s[0] in u'止蟹宕' and s[:4] != u'宕合三入') or s[1:3] == u'開二' and s[0] != u'梗') and 'j' or (s[:5] in (u'通開一入冬', u'宕開一去唐', u'蟹合一去泰', u'蟹合二去皆') and 'k' or 'g'),
        u'溪': lambda s: (s[2] in u'三四' and not (s[1] == u'合' and s[0] in u'止蟹宕' and s[:4] != u'宕合三入') or s[1:3] == u'開二' and s[0] != u'梗') and 'q' or 'k',
        u'群': lambda s: s[3] == u'平' and (s[2] == u'三' and not (s[1] == u'合' and s[0] in u'止宕') and 'q' or 'k') or (s[2] == u'三' and not (s[1] == u'合' and s[0] in u'止宕蟹' and s[:4] != u'宕合三入') and 'j' or 'g'),
        u'疑': lambda s: '',
        u'曉': lambda s: (s[2] in u'三四' and not (s[1] == u'合' and s[0] in u'止宕蟹' and s[:4] != u'宕合三入') or s[1:3] == u'開二' and s[0] != u'梗') and 'x' or 'h',
        u'匣': lambda s: (s[2] in u'三四' and s[:2] != u'蟹合' or s[1:3] == u'開二' and s[0] != u'梗') and 'x' or 'h',
        u'影': lambda s: '',
        u'云': lambda s: '',
        u'以': lambda s: '',
        }

sjep2rime = {
        u'通': lambda s: s[3] == u'入' and (s[2] == u'三' and s[-1] in u'來娘見溪群疑影曉匣云以' and 'v' or 'u') or 'eng',
        u'江': lambda s: s[3] == u'入' and (s[-1] in u'見溪群疑影曉匣云以' and 'e^' or 'o') or 'ang',
        u'止': lambda s: s[1] == u'合' and (s[-1] in u'莊初崇生俟' and 'ai' or 'ei') or (s[-1] in u'幫滂並明端透定泥來娘見溪群疑影曉匣云以' and 'i' or (s[-1] == u'日' and 'er' or 'i^')),
        u'遇': lambda s: s[4] != u'模' and s[-1] in u'來娘精清從心邪見溪群疑影曉匣云以' and 'v' or 'u',
        u'蟹': lambda s: box2rime[s[4]](s),
        u'臻': lambda s: s[3] == u'入' and box2rime[s[4]](s) or 'en',
        u'山': lambda s: s[3] == u'入' and box2rime[s[4]](s) or 'an',
        u'效': lambda s: 'ao',
        u'果': lambda s: box2rime[s[4]](s),
        u'假': lambda s: s[2] == u'三' and (s[-1] in u'知徹澄莊初崇生俟章昌常書船日' and 'e' or 'e^') or 'a',
        u'宕': lambda s: s[3] == u'入' and box2rime[s[4]](s) or 'ang',
        u'梗': lambda s: s[3] == u'入' and box2rime[s[4]](s) or 'eng',
        u'曾': lambda s: s[3] == u'入' and box2rime[s[4]](s) or 'eng',
        u'流': lambda s: s[4] == u'幽' and s[-1] in u'幫滂並明' and 'ao' or 'ou',
        u'深': lambda s: s[3] == u'入' and (s[-1] in u'知徹澄章昌常書船日' and 'i^' or (s[-1] in u'莊初崇生俟' and 'e' or 'i')) or 'en',
        u'咸': lambda s: s[3] == u'入' and box2rime[s[4]](s) or 'an',
        }

box2rime = {
        u'東': sjep2rime[u'通'],
        u'冬': sjep2rime[u'通'],
        u'鍾': sjep2rime[u'通'],
        u'江': sjep2rime[u'江'],
        u'支': sjep2rime[u'止'],
        u'脂': sjep2rime[u'止'],
        u'之': sjep2rime[u'止'],
        u'微': sjep2rime[u'止'],
        u'魚': sjep2rime[u'遇'],
        u'虞': sjep2rime[u'遇'],
        u'模': sjep2rime[u'遇'],
        u'齊': lambda s: s[1] == u'合' and 'ei' or 'i',
        u'佳': lambda s: s[-1] in u'見溪群疑影曉匣云以' and 'a' or 'ai',
        u'皆': lambda s: s[1] == u'開' and s[-1] in u'見溪群疑影曉匣云以' and 'e^' or 'ai',
        u'灰': lambda s: 'ei',
        u'咍': lambda s: s[-1] in u'幫滂並明' and 'ei' or 'ai',
        u'祭': lambda s: s[1] == u'合' and (s[-1] in u'莊初崇生俟' and 'ai' or 'ei') or (s[-1] in u'知徹澄莊初崇生俟章昌常書船日' and 'i^' or 'i'),
        u'泰': lambda s: (s[1] == u'合' and s[-1] != u'透' or s[-1] in u'幫滂並明') and 'ei' or 'ai',
        u'夬': lambda s: s[1] == u'開' and s[-1] in u'見溪群疑影曉匣云以' and 'e^' or 'ai',
        u'廢': lambda s: s[1] == u'合' and 'ei' or 'i',
        u'眞': lambda s: s[3] == u'入' and (s[1] == u'合' and 'v' or (s[-1] in u'知徹澄莊初崇生俟章昌常書船日' and 'i^' or 'i')) or 'en',
        u'諄': lambda s: s[3] == u'入' and (s[-1] in u'來娘精清從心邪見溪群疑影曉匣云以' and 'v' or (s[-1] in u'莊初崇生俟' and 'ai' or 'u')) or 'en',
        u'臻': lambda s: s[3] == u'入' and 'e' or 'en',
        u'文': lambda s: s[3] == u'入' and (s[-1] in u'幫滂並明' and 'u' or 'v') or 'en',
        u'欣': lambda s: s[3] == u'入' and 'i' or 'en',
        u'魂': lambda s: s[3] == u'入' and (s[-1] in u'幫並明' and 'o' or 'u') or 'en',
        u'痕': lambda s: s[3] == u'入' and 'e' or 'en',
        u'元': lambda s: s[3] == u'入' and (s[-1] in u'幫滂並明' and 'a' or 'e^') or 'an',
        u'寒': lambda s: s[3] == u'入' and (s[-1] in u'見溪群疑影曉匣云以' and 'e' or 'a') or 'an',
        u'桓': lambda s: s[3] == u'入' and 'o' or 'an',
        u'刪': lambda s: s[3] == u'入' and 'a' or 'an',
        u'山': lambda s: s[3] == u'入' and 'a' or 'an',
        u'先': lambda s: s[3] == u'入' and 'e^' or 'an',
        u'仙': lambda s: s[3] == u'入' and (s[-1] in u'知徹澄莊初崇生俟章昌常書船日' and (s[1] == u'合' and 'o' or 'e') or 'e^') or 'an',
        u'蕭': sjep2rime[u'效'],
        u'宵': sjep2rime[u'效'],
        u'肴': sjep2rime[u'效'],
        u'豪': sjep2rime[u'效'],
        u'歌': lambda s: s[-1] in u'見溪群疑影曉匣云以' and 'e' or 'o',
        u'戈': lambda s: s[2] == u'三' and 'e^' or 'o',
        u'麻': sjep2rime[u'假'],
        u'陽': lambda s: s[3] == u'入' and (s[-1] in u'來娘精清從心邪見溪群疑影曉匣云以' and 'e^' or 'o') or 'ang',
        u'唐': lambda s: s[3] == u'入' and (s[1] == u'開' and s[-1] in u'見溪群疑影曉匣云以' and 'e' or 'o') or 'ang',
        u'庚': lambda s: s[3] == u'入' and (s[1] == u'開' and (s[2] == u'三' and (s[-1] in u'莊初崇生俟' and 'i^' or 'i') or (s[-1] == u'莊' and 'a' or (s[-1] in u'幫滂並明' and 'o' or 'e'))) or (s[2] == u'三' and 'v' or 'o')) or 'eng',
        u'耕': lambda s: s[3] == u'入' and (s[1] == u'開' and s[-1] not in u'幫滂並明' and 'e' or 'o') or 'eng',
        u'清': lambda s: s[3] == u'入' and (s[-1] in u'知徹澄莊初崇生俟章昌常書船日' and (s[1] == u'合' and 'u' or 'i^') or (s[1] == u'合' and s[-1] not in u'幫滂並明' and 'v' or 'i')) or 'eng',
        u'青': lambda s: s[3] == u'入' and (s[1] == u'合' and 'v' or 'i') or 'eng',
        u'蒸': lambda s: s[3] == u'入' and (s[1] == u'合' and 'v' or (s[-1] in u'知徹澄章昌常書船日' and 'i^' or (s[-1] in u'莊初崇生俟' and 'e' or 'i'))) or 'eng',
        u'登': lambda s: s[3] == u'入' and (s[1] == u'開' and s[-1] not in u'幫滂並明' and 'e' or 'o') or 'eng',
        u'尤': sjep2rime[u'流'],
        u'侯': sjep2rime[u'流'],
        u'幽': sjep2rime[u'流'],
        u'侵': sjep2rime[u'深'],
        u'覃': lambda s: s[3] == u'入' and (s[-1] in u'見溪群疑影曉匣云以' and 'e' or 'a') or 'an',
        u'談': lambda s: s[3] == u'入' and (s[-1] in u'見溪群疑影曉匣云以' and 'e' or 'a') or 'an',
        u'鹽': lambda s: s[3] == u'入' and (s[-1] in u'知徹澄莊初崇生俟章昌常書船日' and 'e' or 'e^') or 'an',
        u'添': lambda s: s[3] == u'入' and 'e^' or 'an',
        u'咸': lambda s: s[3] == u'入' and 'a' or 'an',
        u'銜': lambda s: s[3] == u'入' and 'a' or 'an',
        u'嚴': lambda s: s[3] == u'入' and 'e^' or 'an',
        u'凡': lambda s: s[3] == u'入' and 'a' or 'an',
}

tongxho2medial = {
        u'開一': lambda s: ((s[0] == u'通' and s[3] != u'入' and s[-1] not in u'幫滂並明') or (s[0] == u'臻' and s[-1] == u'透') or ((s[0] == u'果' or s[0] == u'宕' and s[3] == u'入') and s[-1] not in u'幫滂並明見溪群疑影曉匣云以')) and 'u' or '',
        u'開二': lambda s: (s[0] != u'梗' and s[-1] in u'見溪群疑影曉匣云以' or s[-3:] == u'上咸娘') and (s[3:5] == u'入江' and 'v' or 'i') or ((s[0] == u'江' and (s[-1] in u'知徹澄莊初崇生俟章昌常書船日' or s[3] == u'入' and s[-1] not in u'幫滂並明') or s[-3:] == u'入山初') and 'u' or ''),
        u'開三': lambda s: (s[-1] in u'幫滂並明' and (s[3] == u'入' and (s[0] == u'山' and 'i' or '_') or ((s[0] in u'通止蟹' or s[0] == u'流' and s[-1] != u'明' and s[4] != u'幽') and '_' or 'i')) or (
            s[-1] in u'見溪群疑影曉匣云以' and (s[3] == u'入' and ((s[0] == u'咸' or s[0] == u'山' and s[4:] not in (u'仙B見', u'仙B曉')) and 'i' or (s[0] in u'山宕' and 'v' or '_')) or (s[0] == u'通' and 'v' or (s[0] in u'止遇蟹' and '_' or 'i'))) or (
                s[-1] in u'來娘精清從心邪' and (s[3] == u'入' and (s[0] == u'宕' and 'v' or (s[0] in u'咸山' and 'i' or '_')) or (s[0] == u'通' and 'u' or (s[0] in u'止遇蟹' and '_' or (s[3:] == u'上仙A從' and 'v' or 'i')))) or (
                    s[0] == u'宕' and ((s[3] == u'入' or s[-1] in u'莊初崇生俟') and 'u' or '_') or (s[3] == u'入' and '_' or (s[0] == u'通' and 'u' or '_'))
                    )
                )
            )).replace('_', ''),
        u'開四': lambda s: (s[3] == u'入' and (s[0] == u'梗' and '_' or 'i') or (s[0] == u'蟹' and '_' or (s[3:] == u'去青影' and 'v' or 'i'))).replace('_', ''),
        u'合一': lambda s: (s[-1] not in u'幫滂並明' and s[3:5] != u'入魂'
            and (s[0] != u'蟹' or s[-1] not in u'泥來' and s[-2:] != u'泰透')
            ) and 'u' or '',
        u'合二': lambda s: (s[-1] not in u'來娘' or s[0] == u'山' and s[3] != u'入' or s[3:5] == u'入庚') and 'u' or '',
        u'合三': lambda s: (s[-1] in u'幫滂並明' and (s[-1] == u'明' and s[0] in u'止臻咸山宕' and s[3:5] not in (u'入文', u'上凡') and 'u' or '_') or (
            s[-1] in u'見溪群疑影曉匣云以' and (s[3] == u'入' and (s[0] in u'山宕' and 'v' or '_') or (s[0] == u'遇' and '_' or (s[0] in u'止蟹宕' and 'u' or 'v'))) or (
                s[-1] in u'來娘精清從心邪' and (s[3] == u'入' and (s[0] == u'山' and 'v' or '_') or ((s[0] == u'果' or s[0] in u'臻山' and s[-1] != u'來') and 'v' or ((s[0] == u'止' and s[-1] not in u'來娘' or s[0] in u'蟹臻山') and 'u' or (s[0] == u'梗' and 'i' or '_')))) or (
                    (s[0] == u'遇' or s[0] == u'臻' and s[3] == u'入' and s[-1] not in u'莊初崇生俟' or s[0] == u'梗') and '_' or 'u'
                    )
                )
            )).replace('_', ''),
        u'合四': lambda s: s[0] == u'蟹' and 'u' or (s[3:5] != u'入青' and 'v' or ''),
        }

deuh2tone = {
        u'平': lambda s: s[-1] in u'並明定泥來澄娘從邪崇俟常船日群疑匣云以' and 2 or (s[-1] == u'昌' and s[:3] == u'山開三' and 2 or 1),
        u'上': lambda s: s[-1] in u'並定澄從邪崇俟常船群匣' and s[4:] not in (u'佳並', u'脂B群', u'清澄') and 4 or 3,
        u'去': lambda s: 4,
        u'入': lambda s: s[-1] in u'並定澄從邪崇俟常船群匣' and s[4:] != u'銜澄' and 2 or (s[-1] in u'明泥來娘日疑云以' and s[4:] != u'山明' and 4 or 0),
        }

shengmu = tuple(u'''\
b  p  m  f  d t n l
g  k  h     j q x
zh ch sh r  z c s
'''.split())
assert len(shengmu) == 21

yunmu = tuple(u'''\
i u v
a o e e^ i^
ai ei ao ou
an en ang eng er
'''.split())
assert len(yunmu) == 17

def parsepy(py):
    if type(py) != str:
        py = str(py)
    if py[-1].isdigit():
        tone = int(py[-1])
        assert 1 <= tone <= 4
        py = py[:-1]
    else:
        tone = 0
    c = py[0]
    if c in shengmu:
        if py[1] == 'h' and c in 'zcs':
            onset = c + 'h'
        else:
            onset = c
    else:
        onset = ''
        if py.startswith('yu'):
            py = 'v' + py[2:]
    p = len(onset)
    c = py[p]
    if c in 'iy':
        p += 1
        rime = py[p:]
        if rime == 'i':
            assert c == 'y'
            medial = ''
        elif not rime:
            medial = ''
            if onset and onset[0] in 'zcsr':
                rime = 'i^'
            else:
                rime = 'i'
        elif rime == 'ong':
            rime = 'eng'
            medial = 'v'
        else:
            medial = 'i'
            if rime == 'e':
                rime = 'e^'
            elif rime == 'n' or rime == 'in':
                rime = 'en'
            elif rime == 'ng' or rime == 'ing':
                rime = 'eng'
            elif rime == 'u':
                if c == 'i':
                    rime = 'ou'
                else:
                    assert c == 'y' or onset in 'jqx'
                    rime = 'v'
    elif c in 'uw':
        p += 1
        rime = py[p:]
        if rime == 'u':
            assert c == 'w'
            medial = ''
        elif not rime:
            medial = ''
            if onset and onset in 'jqx':
                rime = 'v'
            else:
                rime = 'u'
        else:
            if onset and onset in 'jqx':
                medial = 'v'
            else:
                medial = 'u'
            if rime == 'i':
                rime = 'ei'
            elif rime == 'e':
                rime = 'e^'
            elif rime == 'n':
                rime = 'en'
            elif rime == 'ng':
                rime = 'eng'
    elif c == 'v':
        p += 1
        rime = py[p:]
        if not rime:
            medial = ''
            rime = 'v'
        else:
            medial = 'v'
            if rime == 'e':
                rime = 'e^'
            elif rime == 'n':
                rime = 'en'
    else:
        medial = ''
        rime = py[p:]
        if rime == 'ong':
            medial = 'u'
            rime = 'eng'
    assert not onset or onset in shengmu
    assert not medial or medial in yunmu[:3]
    assert rime in yunmu
    return onset, medial, rime, tone

def formatpy(onset, medial, rime, tone):
    ar = [onset]
    if not medial:
        if not onset:
            if rime == 'i':
                ar.append('yi')
            elif rime == 'u':
                ar.append('wu')
            elif rime == 'v':
                ar.append('yu')
            else:
                ar.append(rime)
        elif rime == 'i^':
            assert onset[0] in 'zcsr'
            ar.append('i')
        elif rime == 'v':
            if onset in 'jqx':
                ar.append('u')
            else:
                ar.append('v')
        else:
            ar.append(rime)
    elif medial == 'i':
        if not onset:
            ar.append('y')
            if rime == 'en':
                ar.append('in')
            elif rime == 'eng':
                ar.append('ing')
            elif rime == 'e^':
                ar.append('e')
            else:
                ar.append(rime)
        else:
            ar.append('i')
            if rime == 'en':
                ar.append('n')
            elif rime == 'eng':
                ar.append('ng')
            elif rime == 'e^':
                ar.append('e')
            elif rime == 'ou':
                ar.append('u')
            else:
                ar.append(rime)
    elif medial == 'u':
        if not onset:
            ar.append('w')
            ar.append(rime)
        else:
            ar.append('u')
            if rime == 'en':
                ar.append('n')
            elif rime == 'eng':
                ar[-1] = 'ong'
            elif rime == 'e^':
                ar.append('e')
            elif rime == 'ei':
                ar.append('i')
            else:
                ar.append(rime)
    elif medial == 'v':
        if not onset:
            ar.append('yu')
            if rime == 'e^':
                ar.append('e')
            elif rime == 'en':
                ar.append('n')
            elif rime == 'eng':
                ar[-1] = 'yong'
            elif rime == 'e^':
                ar.append('e')
            else:
                ar.append(rime)
        else:
            if onset in 'jqx':
                ar.append('u')
            else:
                ar.append('v')
            if rime == 'e^':
                ar.append('e')
            elif rime == 'en':
                ar.append('n')
            elif rime == 'eng':
                ar[-1] = 'iong'
            else:
                ar.append(rime)
    else:
        assert False
    if tone:
        ar.append(str(tone))
    return ''.join(ar)

def gy2py(s):
    zi = sjeng2onset[s[-1]](s)
    jie = tongxho2medial[s[1:3]](s)
    mu = box2rime[s[4]](s)
    diao = deuh2tone[s[3]](s)
    return formatpy(zi, jie, mu, diao)

def checkpy(py, s):
    onset, medial, rime, tone = parsepy(py)
    assert len(s) >= 6
    mu = box2rime[s[4]](s)
    if mu is not None:
        assert rime == mu
        assert sjep2rime[s[0]](s) == mu
    zi = sjeng2onset[s[-1]](s)
    if zi is not None:
        assert onset == zi
    jie = tongxho2medial[s[1:3]](s)
    if jie is not None:
        assert medial == jie
    diao = deuh2tone[s[3]](s)
    if diao is not None:
        assert tone == diao
    assert gy2py(s) == py or py in ('hung4', 'shung4')

assert __name__ == '__main__'
with open(sys.argv[1]) as f:
    for line in f:
        try:
            ar = line.decode('utf-8').split()
        except AttributeError:
            ar = line.split()
        try:
            br = parsepy(ar[0])
            assert ar[0] == formatpy(*br) or ar[0] in ('hung4', 'shung4')
        except:
            if type('') == type(u''):
                print(ar[0], br, file=sys.stderr)
            else:
                print(ar[0].encode('utf-8'), br, file=sys.stderr)
            raise
        for i in range(1, len(ar)):
            try:
                checkpy(ar[0], ar[i])
            except:
                if type('') == type(u''):
                    print(ar[0], ar[i], br, file=sys.stderr)
                else:
                    print(ar[0].encode('utf-8'), ar[i].encode('utf-8'), br, file=sys.stderr)
                #raise
