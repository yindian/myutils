#!/usr/bin/env python
from __future__ import print_function, unicode_literals
from cccode import *
import itertools
import pprint
import traceback

dfl_param = dict(dot='.', dash='-', gap=' ', sep='\\')

class MorseCode:
    _A = '.-'   # short 1
    _B = '-...'
    _C = '-.-.'
    _D = '-..'
    _E = '.'
    _F = '..-.'
    _G = '--.'
    _H = '....'
    _I = '..'
    _J = '.---'
    _K = '-.-'
    _L = '.-..'
    _M = '--'
    _N = '-.'
    _O = '---'
    _P = '.--.'
    _Q = '--.-'
    _R = '.-.'
    _S = '...'
    _T = '-'
    _U = '..-'  # short 2
    _V = '...-' # short 3
    _W = '.--'
    _X = '-..-'
    _Y = '-.--'
    _Z = '--..'
    _0 = '-----'
    _1 = '.----'
    _2 = '..---'
    _3 = '...--'
    _4 = '....-'
    _5 = '.....'
    _6 = '-....'
    _7 = '--...'
    _8 = '---..'
    _9 = '----.'
    Period = '.-.-.-'
    Comma = '--..--'
    Question = '..--..'
    Apostrophe = '.----.'
    Exclamation = '-.-.--'
    Slash = '-..-.'
    ParenOpen = '-.--.'
    ParenClose = '-.--.-'
    Ampersand = '.-...'
    Colon = '---...'
    Semicolon = '-.-.-.'
    Equals = '-...-'
    Plus = '.-.-.'
    Hyphen = '-....-'
    Underscore = '..--.-'
    Quotation = '.-..-.'
    Dollar = '...-..-'
    At = '.--.-.'

class ProSign:
    UnknownStation = 'AA'
    Out = 'AR'
    Wait = 'AS'
    Verified = 'VE'
    Interrogative = 'INT'
    Correction = 'HH'
    Break = 'BT'
    Attention = 'KA'
    EndOfWork = 'VA'
    SOS = 'SOS'
    Wabun = 'DO'

_punct_map = dict(
        Period = '.',
        Comma = ',',
        Question = '?',
        Apostrophe = "'",
        Exclamation = '!',
        Slash = '/',
        ParenOpen = '(',
        ParenClose = ')',
        Ampersand = '&',
        Colon = ':',
        Semicolon = ';',
        Equals = '=',
        Plus = '+',
        Hyphen = '-',
        Underscore = '_',
        Quotation = '"',
        Dollar = '$',
        At = '@')
_map_to_morse = {}
_map_from_morse = {}
_verbose = False# __name__ == '__main__'

def _init():
    for k in MorseCode.__dict__:
        if k.startswith('__'):
            continue
        elif k.startswith('_'):
            assert len(k) == 2
            c = k[1]
            _map_to_morse[c] = _map_to_morse[c.lower()] = v = getattr(MorseCode, k)
            assert v not in _map_from_morse
            _map_from_morse[v] = c
        else:
            c = _punct_map[k]
            _map_to_morse[c] = v = getattr(MorseCode, k)
            if v not in _map_from_morse:
                _map_from_morse[v] = c
            elif _verbose:
                prn('Ignoring %s with same code as %s: %s' % (c, _map_from_morse[v], v))
        assert set(v).issubset(set('.-'))

    for k in ProSign.__dict__:
        if k.startswith('__'):
            continue
        c = getattr(ProSign, k)
        v = ''.join(map(_map_to_morse.__getitem__, c))
        c = '<%s>' % (c,)
        _map_to_morse[c] = v
        if v not in _map_from_morse:
            _map_from_morse[v] = c
        elif _verbose:
            prn('Ignoring %s with same code as %s: %s' % (c, _map_from_morse[v], v))
        assert set(v).issubset(set('.-'))

_init()

class FormatError(Exception):
    pass

class ParamError(Exception):
    pass

def _decode(buf, dot, dash, gap, sep):
    res = []
    xlat = {}
    if dot:
        xlat[ord(dot)] = ord('.')
    if dash:
        xlat[ord(dash)] = ord('-')
    for s in buf.split(sep or '<sep>'):
        x = []
        for t in s.split(gap or '<gap>'):
            if not t:
                continue
            x.append(_map_from_morse[t.translate(xlat)])
        res.append(''.join(x))
    return ' '.join(res)

try:
    unichr
    def _unichr(o):
        if o < 0x10000:
            s = unichr(o)
        else:
            o -= 0x10000
            s = unichr(0xD800 | (o >> 10)) + unichr(0xDC00 | (o & 0x3FF))
        return s
except NameError:
    _unichr = chr

_cn_cols = 'china3 china2 china1'.split()
_hk_cols = cols[:5]
def _cnjoin(ar, typ):
    br = []
    lastcn = True
    for x in ar:
        if type(x) == dict:
            if not lastcn:
                br.append(' ')
            lastcn = True
            if typ in x:
                br.append(x[typ])
            else:
                t = []
                if typ.startswith('china'):
                    l = _cn_cols
                else:
                    l = _hk_cols
                for k in l:
                    if k in x:
                        t.append(x[k])
                if not t:
                    br.append('[%s]' % (x['raw'],))
                elif len(t) == 1:
                    br.append(t[0])
                else:
                    br.append('{%s}' % ('|'.join(t),))
        elif x:
            br.append(' ')
            lastcn = False
    return ''.join(br)

_xlat_ccc = dict(A=1, a=1, U=2, u=2, V=3, v=3)
_digit_ccc = set('1234567890AUV')
_digit_uni = set('1234567890ABCDEF')
def _chinese(raw, out={}):
    n = 0
    ar = raw.split(' ')
    if len(ar) == 1 and len(ar[0]) % 4 == 0:
        t = set(ar[0].upper())
        if t.issubset(_digit_ccc):
            ar = [''.join(x) for x in zip(raw[::4], raw[1::4], raw[2::4], raw[3::4])]
    ccc = china = uni = True
    for i in range(len(ar)):
        s = ar[i]
        if len(s) == 4:
            t = set(s.upper())
            br = {}
            if t.issubset(_digit_ccc):
                try:
                    x = int(s.translate(_xlat_ccc))
                    for k, v in zip(cols, code2hanzi[x]):
                        if v:
                            br[k] = v
                    if not any(map(br.__contains__, _cn_cols)):
                        #prn(s, br)
                        china = False
                    assert br
                    n += 1
                except:
                    #traceback.print_exc()
                    ccc = False
            if t.issubset(_digit_uni):
                try:
                    x = int(s, 16)
                    br['uni'] = _unichr(x)
                    n += 1
                except:
                    uni = False
            if br:
                br['raw'] = s
                ar[i] = br
        elif len(s) == 5 and set(s.upper()).issubset(_digit_uni):
            br = {}
            try:
                x = int(s, 16)
                br['uni'] = _unichr(x)
                n += 1
            except:
                uni = False
            if br:
                br['raw'] = s
                ar[i] = br
    if uni:
        out['uni'] = _cnjoin(ar, 'uni')
    if ccc:
        if china:
            out['china'] = _cnjoin(ar, 'china3')
        out['hkc'] = _cnjoin(ar, 'hkc')
    return n

def _unparam(param):
    return (param['dot'], param['dash'], param['gap'], param['sep'])

def decode(buf, out={}, **opt):
    if not buf:
        return ''
    if type(buf) != type(bytes):
        buf = buf.decode('ascii')
    a = set(buf)
    if len(a) > 4:
        raise FormatError('Too many different characters: %s' % (','.join(map(repr, a)),))
    if not set(opt.keys()).issubset(set(dfl_param.keys())):
        raise ParamError('Invalid param: %s' % (','.join([k for k in opt if k not in dfl_param]),))
    if False:
        param = opt.copy()
        for k in dfl_param:
            if k not in param:
                param[k] = dfl_param[k]
        b = set(filter(None, param.values()))
        if not a.issubset(b):
            raise FormatError('Invalid characters: %s' % (','.join(map(repr, a.difference(b))),))
    else:
        if len(opt) < len(dfl_param):
            a = [(buf.count(c), c) for c in a if c not in opt.values()]
            a.sort(reverse=True)
            ar = []
            for k in 'dot dash gap sep'.split():
                if k not in opt:
                    ar.append(k)
            if len(a) > len(ar):
                raise FormatError('Too many (> %d) different characters: %s' % (len(ar), ','.join(map(repr, [x[1] for x in a if x[1] not in opt.values()])),))
            br = [x[1] for x in a]
            while len(br) < len(ar):
                br.append('')
            for t in set(itertools.permutations(br)):
                p = opt.copy()
                for k, v in zip(ar, t):
                    p[k] = v
                try:
                    v = _unparam(p)
                    s = _decode(buf, *v)
                    out['raw_' + '_'.join(v)] = s
                except:
                    pass
            param = None
            best = None
            for t in itertools.permutations(br):
                p = opt.copy()
                for k, v in zip(ar, t):
                    p[k] = v
                v = _unparam(p)
                k = 'raw_' + '_'.join(v)
                if k in out:
                    s = out[k]
                    x = -s.count(' ') + _chinese(s) * 1000
                    if best is None or x > best:
                        param = p
                        best = x
        else:
            param = opt.copy()
    v = _unparam(param)
    out['param'] = '_'.join(v)
    s = _decode(buf, *v)
    if _chinese(s, out):
        for k in 'china hkc uni'.split():
            if k in out:
                out['choice'] = k
                return out[k]
    return s

if __name__ == '__main__':
    with open('test.txt', 'rb') as f:
        buf = f.read()
        buf = buf.replace(b'\n', b' ').replace(b'\r', b'')
        out = {}
        prn(decode(buf, out))
        #pprint.pprint(out)
