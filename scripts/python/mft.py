#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import getopt
import struct
import math
import bisect
try:
    import cStringIO as StringIO
except:
    import StringIO
try:
    import readline
except:
    pass

def read_header(f):
    assert f.read(4) == 'MThd'
    assert struct.unpack('!L', f.read(4))[0] == 6
    fmt = struct.unpack('!H', f.read(2))[0]
    assert fmt < 2
    trk = struct.unpack('!H', f.read(2))[0]
    div = struct.unpack('!H', f.read(2))[0]
    assert div < 0x8000 # not SMPTE
    return fmt, trk, div

def write_header(f, fmt, trk, div):
    f.write('MThd')
    f.write(struct.pack('!LHHH', 6, fmt, trk, div))

def read_track_header(f):
    assert f.read(4) == 'MTrk'
    return struct.unpack('!L', f.read(4))[0]

def read_var_len_int(f):
    c = ord(f.read(1))
    r = c & 0x7F
    l = 1
    while (c & 0x80):
        c = ord(f.read(1))
        r = (r << 7) | (c & 0x7F)
        l += 1
    return r, l

def encode_var_len_int(x):
    assert x >= 0
    ar = [x & 0x7F]
    x >>= 7
    while x:
        ar.append((x & 0x7F) | 0x80)
        x >>= 7
    return ''.join(map(chr, reversed(ar)))

def read_track(f, running=None):
    n = read_track_header(f)
    delta_times = []
    delta_lengths = []
    events = []
    status = 0
    sysex_cont = False
    while n:
        r, l = read_var_len_int(f)
        n -= l
        delta_times.append(r)
        delta_lengths.append(l)
        pos = f.tell()
        code = ord(f.read(1))
        if code < 0x80: # running status
            assert status
            code = status
            f.seek(-1, 1)
            if running is not None:
                running.append(True)
        else:
            status = code
            if running is not None:
                running.append(False)
        hi = code & 0xF0
        if hi in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
            events.append(chr(code) + f.read(2))
            assert len(events[-1]) == 3
        elif hi in (0xC0, 0xD0):
            events.append(chr(code) + f.read(1))
            assert len(events[-1]) == 2
        elif code == 0xFF:
            subcode = f.read(1)
            r, l = read_var_len_int(f)
            events.append(chr(code) + subcode + encode_var_len_int(r) + f.read(r))
            assert len(events[-1]) == 2 + l + r
        elif code == 0xF0:
            assert not sysex_cont
            r, l = read_var_len_int(f)
            events.append(chr(code) + encode_var_len_int(r) + f.read(r))
            assert len(events[-1]) == 1 + l + r
            if events[-1].endswith('\xF7'):
                sysex_cont = False
            else:
                sysex_cont = True
        elif code == 0xF7:
            r, l = read_var_len_int(f)
            events.append(chr(code) + encode_var_len_int(r) + f.read(r))
            assert len(events[-1]) == 1 + l + r
            if sysex_cont and events[-1].endswith('\xF7'):
                sysex_cont = False
        else:
            assert False
        n -= f.tell() - pos
    return delta_times, delta_lengths, events

def write_track(f, delta_times, delta_lengths, events, running=None):
    f.write('MTrk')
    f.write(struct.pack('!L', sum(delta_lengths) + len(''.join(events)) - sum(running or [])))
    assert len(set(map(len, (delta_times, delta_lengths, events)))) == 1
    for i in xrange(len(events)):
        f.write(encode_var_len_int(delta_times[i]))
        if running and running[i]:
            f.write(events[i][1:])
            continue
        f.write(events[i])

def tohex(s):
    s = s.encode('hex')
    return ' '.join(map(''.join, zip(s[::2], s[1::2])))

def escapestr(s):
    return s.encode('string_escape').replace('"', '\\"')

class MidiFile:
    _meta_types = {
            "Text":         1,
            "Copyright":    2,
            "TrkName":      3,
            "SeqName":      3,
            "InstrName":    4,
            "Lyric":        5,
            "Marker":       6,
            "Cue":          7,
            "PrName":       8,
            "DevName":      9,
            "TrkEnd":       0x2F,
            "_SeqNr":       0,
            "_Tempo":       0x51,
            "_SMPTE":       0x54,
            "_TimeSig":     0x58,
            "_KeySig":      0x59,
            "_SeqSpec":     0x7F,
            }
    _meta_type_str = {}
    major = 0
    minor = 1

    def __init__(self, f=None):
        self._fmt = self._trk = self._div = None
        self._tracks = []
        self._now = None
        self._sysex_cont = False
        if f:
            self._fmt, self._trk, self._div = read_header(f)
            for i in xrange(self._trk):
                running = []
                delta_times, delta_lengths, events = read_track(f, running)
                times = []
                try:
                    times.append(delta_times[0])
                except IndexError:
                    pass
                else:
                    for j in xrange(1, len(delta_times)):
                        times.append(delta_times[j] + times[j - 1])
                self._tracks.append((times, events, running))

    def write(self, f):
        assert self._trk == len(self._tracks)
        write_header(f, self._fmt, self._trk, self._div)
        for i in xrange(self._trk):
            delta_times, delta_lengths = [], []
            times = self._tracks[i][0]
            try:
                delta_times.append(times[0])
            except IndexError:
                pass
            else:
                delta_lengths.append(len(encode_var_len_int(delta_times[0])))
                for j in xrange(1, len(times)):
                    delta_times.append(times[j] - times[j - 1])
                    delta_lengths.append(len(encode_var_len_int(delta_times[-1])))
            write_track(f, delta_times, delta_lengths, self._tracks[i][1], self._tracks[i][2])

    def dump(self, f):
        assert self._trk == len(self._tracks)
        print >> f, 'Header(%d, %d, %d)' % (self._fmt, self._trk, self._div)
        sigtimes = []
        siglens = []
        sigbars = []
        for i in xrange(self._trk):
            print >> f, 'Track() # %d' % (i + 1,)
            delta_times = []
            times = self._tracks[i][0]
            try:
                delta_times.append(times[0])
            except IndexError:
                pass
            else:
                for j in xrange(1, len(times)):
                    delta_times.append(times[j] - times[j - 1])
            events = self._tracks[i][1]
            running = self._tracks[i][2]
            sysex_cont = False
            last_bar = 0
            last_bar_end = 0
            p = 0
            for j in xrange(len(events)):
                if sigtimes and times[j] >= last_bar_end and not events[j].startswith('\xFF'):
                    p = bisect.bisect(sigtimes, times[j], p)
                    if p:
                        bar = sigbars[p - 1] + (times[j] - sigtimes[p - 1]) / siglens[p - 1]
                        if bar != last_bar:
                            print >> f, '# Measure %d: %d ~ %d' % (bar,
                                    sigtimes[p - 1] + siglens[p - 1] * (bar - 1), 
                                    sigtimes[p - 1] + siglens[p - 1] * bar)
                            last_bar = bar
                            last_bar_end = sigtimes[p - 1] + siglens[p - 1] * bar
                if delta_times[j]:
                    print >> f, 'after(%d) # at(%d)' % (delta_times[j], times[j])
                code = ord(events[j][0])
                hi = code & 0xF0
                if hi < 0xF0:
                    ar = map(ord, events[j])
                    if hi == 0x80:
                        line = 'Off(%d, %d, %d)' % (1 + (ar[0] & 0x0F), ar[1], ar[2])
                    elif hi == 0x90:
                        line = 'On(%d, %d, %d)' % (1 + (ar[0] & 0x0F), ar[1], ar[2])
                    elif hi == 0xA0:
                        line = 'PoPr(%d, %d, %d)' % (1 + (ar[0] & 0x0F), ar[1], ar[2])
                    elif hi == 0xB0:
                        line = 'Par(%d, %d, %d)' % (1 + (ar[0] & 0x0F), ar[1], ar[2])
                    elif hi == 0xC0:
                        line = 'PrCh(%d, %d)' % (1 + (ar[0] & 0x0F), ar[1])
                    elif hi == 0xD0:
                        line = 'ChPr(%d, %d)' % (1 + (ar[0] & 0x0F), ar[1])
                    elif hi == 0xE0:
                        line = 'Pb(%d, %d)' % (1 + (ar[0] & 0x0F), ar[1] | (ar[2] << 7))
                    else:
                        assert False
                elif code == 0xFF:
                    subtype = ord(events[j][1])
                    r, l = read_var_len_int(StringIO.StringIO(events[j][2:]))
                    buf = events[j][2 + l:]
                    assert len(buf) == r
                    if subtype == MidiFile._SeqSpec:
                        line = 'SeqSpec("%s")' % (tohex(buf),)
                    elif subtype == MidiFile._SeqNr:
                        line = 'SeqNr(%d)' % struct.unpack('!H', buf)
                    elif subtype == MidiFile._Tempo:
                        line = 'Tempo(%d)' % struct.unpack('!L', '\0' + buf)
                    elif subtype == MidiFile._SMPTE:
                        line = 'SMPTE(%d, %d, %d, %d, %d)' % struct.unpack('B' * 5, buf)
                    elif subtype == MidiFile._TimeSig:
                        nn, dd, cc, bb = struct.unpack('B' * 4, buf)
                        line = 'TimeSig(%d, %d, %d, %d)' % (nn, 1 << dd, cc, bb)
                        p = bisect.bisect(sigtimes, times[j])
                        sigtimes.insert(p, times[j])
                        siglens.insert(p, (self._div * nn * 4) >> dd)
                        sigbars.insert(p, math.ceil(1. * (times[j] - (p > 0 and sigtimes[p - 1] or 0)) / siglens[p])
                                + (p > 0 and sigbars[p - 1] or 1))
                        p = 0
                    elif subtype == MidiFile._KeySig:
                        sf, mi = struct.unpack('bB', buf)
                        line = 'KeySig(%d, %s)' % (sf, mi and 'minor' or 'major')
                    else:
                        s = MidiFile._meta_type_str.get(subtype, hex(subtype))
                        if i == 0 and s == 'TrkName':
                            s = 'SeqName'
                        if buf:
                            line = 'Meta(%s, "%s")' % (s, escapestr(buf))
                        else:
                            line = 'Meta(%s)' % (s,)
                elif code == 0xF0:
                    assert not sysex_cont
                    r, l = read_var_len_int(StringIO.StringIO(events[j][1:]))
                    buf = events[j][1 + l:]
                    assert len(buf) == r
                    line = 'SysEx("%s")' % (tohex(buf),)
                    if buf.endswith('\xF7'):
                        sysex_cont = False
                    else:
                        sysex_cont = True
                elif code == 0xF7:
                    r, l = read_var_len_int(StringIO.StringIO(events[j][1:]))
                    buf = events[j][1 + l:]
                    assert len(buf) == r
                    if sysex_cont:
                        line = 'SysEx("%s")' % (tohex(buf),)
                        if buf.endswith('\xF7'):
                            sysex_cont = False
                    else:
                        line = 'Arb("%s")' % (tohex(buf),)
                else:
                    assert False
                # ((
                assert line[-1] == ')'
                if running[j]:
                    print >> f, line[:-1] + ', running=True)'
                else:
                    print >> f, line

    def Header(self, fmt, trk, div):
        assert self._fmt == self._trk == self._div == None
        self._fmt, self._trk, self._div = fmt, trk, div

    def Track(self):
        assert self._fmt is not None
        assert self._trk is not None
        assert self._div is not None
        assert not self._sysex_cont
        times, events = [], []
        running = []
        self._tracks.append((times, events, running))
        self._now = 0

    def Event(self, buf, **kwargs):
        if self._sysex_cont:
            assert buf.startswith('\xF7')
        times = self._tracks[-1][0]
        if times and self._now < times[-1]:
            p = bisect.bisect(times, self._now)
            times.insert(p, self._now)
            self._tracks[-1][1].insert(p, buf)
            self._tracks[-1][2].insert(p, kwargs.get('running', False))
            return
        self._tracks[-1][0].append(self._now)
        self._tracks[-1][1].append(buf)
        if kwargs:
            for k in kwargs:
                assert k in ('running',)
        self._tracks[-1][2].append(kwargs.get('running', False))

    def at(self, tick):
        self._now = tick

    def after(self, delta):
        self._now += delta

    def Meta(self, subtype, buf='', **kwargs):
        ar = [chr(0xFF), chr(subtype)]
        ar.append(encode_var_len_int(len(buf)))
        ar.append(buf)
        return self.Event(''.join(ar), **kwargs)

    def SeqNr(self, num, **kwargs):
        return self.Meta(MidiFile._SeqNr, struct.pack('!H', num), **kwargs)

    def Tempo(self, tempo, **kwargs):
        buf = struct.pack('!L', tempo)
        assert buf[0] == '\0'
        return self.Meta(MidiFile._Tempo, buf[1:], **kwargs)

    def SMPTE(self, hr, mn, se, fr, ff, **kwargs):
        return self.Meta(MidiFile._SMPTE, struct.pack('B' * 5, hr, mn, se, fr, ff), **kwargs)

    def TimeSig(self, nn, denom, cc, bb, **kwargs):
        dd = int(math.log(denom) / math.log(2))
        assert denom == 1 << dd
        return self.Meta(MidiFile._TimeSig, struct.pack('B' * 4, nn, dd, cc, bb), **kwargs)

    def KeySig(self, sf, mi, **kwargs):
        assert mi in (MidiFile.major, MidiFile.minor)
        return self.Meta(MidiFile._KeySig, struct.pack('bB', sf, mi), **kwargs)

    def SeqSpec(self, text, **kwargs):
        buf = text.replace(' ', '').decode('hex')
        return self.Meta(MidiFile._SeqSpec, buf, **kwargs)

    def SysEx(self, text, **kwargs):
        buf = text.replace(' ', '').decode('hex')
        ar = []
        if self._sysex_cont:
            ar.append('\xF7')
        else:
            ar.append('\xF0')
        if buf.endswith('\xF7'):
            self._sysex_cont = False
        else:
            self._sysex_cont = True
        ar.append(encode_var_len_int(len(buf)))
        ar.append(buf)
        return self.Event(''.join(ar), **kwargs)

    def Arb(self, text, **kwargs):
        buf = text.replace(' ', '').decode('hex')
        ar = ['\xF7']
        ar.append(encode_var_len_int(len(buf)))
        ar.append(buf)
        return self.Event(''.join(ar), **kwargs)

    def ChanEvent(self, evhi, chan, c1, c2=None, **kwargs):
        assert 1 <= chan <= 16
        if c2 is None:
            return self.Event(struct.pack('BB', evhi + chan - 1, c1), **kwargs)
        return self.Event(struct.pack('BBB', evhi + chan - 1, c1, c2), **kwargs)

    def Off(self, chan, pitch, vol=0, **kwargs):
        return self.ChanEvent(0x80, chan, pitch, vol, **kwargs)

    def On(self, chan, pitch, vol, **kwargs):
        return self.ChanEvent(0x90, chan, pitch, vol, **kwargs)

    def PoPr(self, chan, pitch, press, **kwargs):
        return self.ChanEvent(0xA0, chan, pitch, press, **kwargs)

    def Par(self, chan, control, value, **kwargs):
        return self.ChanEvent(0xB0, chan, control, value, **kwargs)

    def PrCh(self, chan, program, **kwargs):
        return self.ChanEvent(0xC0, chan, program, **kwargs)

    def ChPr(self, chan, press, **kwargs):
        return self.ChanEvent(0xD0, chan, press, **kwargs)

    def Pb(self, chan, bend, **kwargs):
        return self.ChanEvent(0xE0, chan, bend & 0x7F, (bend >> 7), **kwargs)

for k, v in MidiFile._meta_types.iteritems():
    setattr(MidiFile, k, v)
    if k != 'SeqName':
        MidiFile._meta_type_str[v] = k.lstrip('_')

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'df')
        assert len(args) <= 2
    except:
        print 'Usage: %s [-d|-f] [input_file [output_file]]' % (os.path.basename(sys.argv[0]),)
        print 'Add option -f to force overwrite'
        print 'Convert text to midi file by default, add option -d to convert back'
        sys.exit(0)
    opts = dict(opts)
    force = opts.has_key('-f')
    if not opts.has_key('-d'):
        mf = MidiFile()
        g = dict([(x, getattr(mf, x)) for x in MidiFile.__dict__ if not x.startswith('_')])
        if not args:
            buf = sys.stdin.read()
            exec(buf, g)
        else:
            execfile(args[0], g)
        if len(args) <= 1:
            mf.write(sys.stdout)
        else:
            if not force and os.path.exists(args[1]):
                print >> sys.stderr, 'Not overridden'
                sys.exit(0)
            with open(args[1], 'wb') as f:
                mf.write(f)
    else:
        if not args:
            mf = MidiFile(sys.stdin)
        else:
            with open(args[0], 'rb') as f:
                mf = MidiFile(f)
        if len(args) <= 1:
            mf.dump(sys.stdout)
        else:
            if not force and os.path.exists(args[1]):
                print >> sys.stderr, 'Not overridden'
                sys.exit(0)
            with open(args[1], 'w') as f:
                mf.dump(f)
