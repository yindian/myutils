#!/bin/bash
if [ -z "$TEMP" ]; then
	TEMP=$HOME/temp
	mkdir -p "$TEMP"
fi
TEMPDIR="$TEMP/test"
mkdir -p "$TEMPDIR"
while [ -n "$1" ]; do
	stat -c 'Checking file sized %s on %y : %N' "$1"
	file "$1"
	extract "$1"
	BASE="$(basename "$1")"
	EXT="${BASE##*.}"
	case "$EXT" in
		jpg|png|Jpeg|jpeg|tif|PNG|gif|bmp|JPG|svg|Png|ICO|GIF|ico)
			identify "$1" 
			rm -f "$TEMPDIR/out.png"
			convert "$1" "$TEMPDIR/out.png"
			;;
		pdf|PDF)
			qpdf --check "$1"
			;;
		mdx|mdd|mdxbak|mddbak|MDX|origin|MDXbak|MDD)
			mdict -q "$1"
			;;
		zip|rar|exe|epub|xlsx|7z|apk|chm|apkg|uvz|docx|bin|RAR|iso|EXE|DLL|dz|gz|xmind|msi|dll|bz2)
			7z -p t "$1" || 7z -p l "$1"
			;;
		css|txt|js|rmp|xml|lrc|ini|cfg|TXT|html|htm|py|map|CSS|cssbak|vpn|md|HTM|ann|url|dsl|PKG|INF|css2|cedict_doc|Txt|srt|mht|LICENSE|json|itf|INI|ifo|gitignore|FPW|defconfig|csv|COPYING_OASIS|COPYING|config|bat)
			cat "$1" | chardet
			;;
		mp3|avi|mkv|Mkv|mp4|mpg|xkw|cc|www|Mp3)
			ffmpeg -loglevel 24 -i "$1" -c copy -f mpegts -y /dev/null
			;;
		ebz|CATALOGS|HONMON|GAI16F00|GAI16H00|GA16HALF|GA16FULL|GA24HALF|GA24FULL|GA48HALF|GA48FULL|GA30HALF|GA30FULL|Honmon2|Catalogs|GAI16H|GAI16F|GAI48H00|GAI30H00|GAI24H00|GAI48F00|GAI30F00|GAI24F00|CATALOG|VTOC|GAI24H|GAI24F|WELCOME|HONMONG|START|Honmons|Honmon|GAI48H|GAI48F|GAI30H|GAI30F|Gai24f|Gai16f|FTXTIDX1|FTXTIDX|catalogs|HONMONS|Honmong)
			if echo "$BASE" | grep -Fqi catalog; then
				ebinfo "$(dirname "$1")"
			elif echo "$BASE" | grep -Fqi honmon; then
				c="$(dirname "$1")"
				c="$(dirname "$c")"
				d="$(dirname "$c")"
				ebstopcode "$d" "$(basename "$c")"
			fi
			;;
		mobi|azw3)
			find "$TEMPDIR" -mindepth 1 -maxdepth 1 -print0 | xargs -0 -r rm -rf
			ebook unpack "$1" "$TEMPDIR" && ls "$TEMPDIR"
			;;
		otf|ttf|TTF|woff|eot|woff2|TTE)
			;;
		doc)
			catdoc -w "$1"
			;;
		xls)
			xls2csv "$1"
			;;
		ppt)
			;;
		rtf)
			unrtf --text "$1"
			;;
		djvu)
			djvm -l "$1"
			;;
		bgl|BGL)
			dictconv -o "$TEMPDIR/out.ifo" "$1"
			;;
		torrent)
			aria2 -S "$1"
			;;
		mdb|MDB)
			mdb-schema "$1"
			;;
		*)
			;;
	esac
	shift
done
