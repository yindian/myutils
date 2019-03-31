#!/usr/bin/env python
import sys
assert __name__ == '__main__'
with open(sys.argv[1]) as f:
    fn = None
    cap = last_cap = None
    for line in f:
        if line.startswith('Processing '):
            if fn and last_cap and cap:
                if last_cap > cap:
                    print fn
            fn = line[11:-3] + 'png'
            cap = last_cap = None
        #elif line.endswith('Giving up.\n') and fn:
        #    print fn
        #    fn = None
        elif line.startswith('Generating capture') and fn:
            p = line.index('(')
            s = line[p+1:line.index(')', p)]
            if cap:
                if last_cap and last_cap > cap:
                    print fn
                    fn = None
                last_cap = cap
            cap = s
        elif line.startswith('  Capture point changed to ') and fn:
            s = line[27:-1]
            assert cap
            try:
                assert len(s) == len(cap)
            except:
                print >> sys.stderr, '"%s" vs "%s"' % (s, cap)
                raise
            cap = s
            if last_cap and last_cap > cap:
                print fn
                fn = None
