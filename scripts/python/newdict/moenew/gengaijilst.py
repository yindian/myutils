import sys
count = {}
for line in sys.stdin:
	code = int(line, 16)
	count[code] = count.get(code, 0) + 1

for code in count.keys():
	print '%04X\t%d\t%s' % (code, count[code], chr(code>>8)+ chr(code&0xff))
