#!/bin/bash
set -e
OUTDIR=merged
PATCHDIR=patch
mkdir -p $OUTDIR
mkdir -p $OUTDIR/bad
for c in `seq 21`; do
	if ls $PATCHDIR/$c-*.pdf >/dev/null 2>&1; then
		if [ $c -le 9 ]; then
			FNAME="$(ls *（0$c）*.pdf)"
		else
			FNAME="$(ls *（$c）*.pdf)"
		fi
		pdftk "$FNAME" dump_data_utf8 | sed '/^InfoKey: ModDate/,/^InfoBegin/d;/^PageMediaBegin/,$d' > "${FNAME%.pdf}.info"
		HEAD="$(sed -n '1,/目录页/d;/^BookmarkPageNumber:/p' "${FNAME%.pdf}.info" | head -2)"
		case $c in
			16)
				TOC=3
				BASE=11
				;;
			17)
				TOC=7
				BASE=14
				;;
			18)
				TOC=2
				BASE=8
				;;
			19)
				TOC=6
				BASE=12
				;;
			20)
				TOC=6
				BASE=11
				;;
			21)
				TOC=2
				BASE=7
				;;
			*)
				TOC=`cat <<< "$HEAD" | head -1 | awk '{print $2 - 1}'`
				BASE=`cat <<< "$HEAD" | tail -1 | awk '{print $2 - 1}'`
		esac
		LIST="$(ls $PATCHDIR/$c-*.pdf | sed 's/^[^-]*-//;s/\.pdf$//;s/,/\n/g' | sort -n)"
		#echo $FNAME, $TOC, $BASE, $LIST
		PAGES=
		for d in $LIST; do
			if [ "${d:0:1}" = "m" ]; then
				PAGES="$PAGES $((TOC + ${d:1}))"
			else
				PAGES="$PAGES $((BASE + d))"
			fi
		done
		pdftk "$FNAME" cat $PAGES output "$OUTDIR/bad/$FNAME"
		FILES="A=$FNAME"
		case $c in
			17)
				FILES="$FILES B=$PATCHDIR/17-3,4.pdf"
				RANGE="A1-16 B A19-end"
				;;
			*)
				RANGE=
				HND=A
				N=1
				for d in $PAGES; do
					HND=`echo $HND | xxd -p -l 1 | awk '{printf "%02x\n", strtonum("0x" $1) + 1}' | xxd -p -r`
					if [ $d -le $BASE ]; then
						FILES="$FILES $HND=$PATCHDIR/$c-m$((d - TOC)).pdf"
					else
						FILES="$FILES $HND=$PATCHDIR/$c-$((d - BASE)).pdf"
					fi
					if [ $d -gt $N ]; then
						RANGE="$RANGE A$N-$((d - 1)) $HND"
					else
						RANGE="$RANGE $HND"
					fi
					N=$((d + 1))
				done
				RANGE="$RANGE A$N-end"
		esac
		pdftk $FILES cat $RANGE output - | pdftk - update_info_utf8 "${FNAME%.pdf}.info" output "$OUTDIR/$FNAME"
		rm "${FNAME%.pdf}.info"
	else
	       	ln -v *（$c）*.pdf $OUTDIR || :
	fi
done
