#!/usr/bin/env python
import sys
assert __name__ == '__main__'
for line in sys.stdin:
    try:
        ar = line.split('\t')
        n = int(ar[0], 16)
        if (0x2E80 <= n < 0x2FE0 or 0x3005 <= n < 0x3008 or 0x3021 <= n < 0x302A
                or 0x3038 <= n < 0x303C or 0x3400 <= n < 0x4DC0 or 0x4E00 <= n <
                0xA000 or 0xF900 <= n < 0xFB00 or 0x20000 <= n < 0x30000):
            sys.stdout.write(line)
    except:
        pass
