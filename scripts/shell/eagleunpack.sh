#!/bin/bash
if [ ! -e pack.json ]; then
	echo "Wrong directory"
	exit 1
fi
set -e
#jq '.folder | walk(if type == "object" then (.name as $n | (.children[] | .name) |= $n + "/" + .) else . end) | recurse(.children[]) | .name' pack.json # not works
CMD="$(
jq -r '.folder as $f | $f | path(.. | .name?) as $a |
	[$a | ["name"], foreach .[] as $i ([]; . + [$i]; if $i | type == "number" then . + ["name"] else empty end) ] as $b |
	[$b | .[] as $c | $f | getpath($c) ] as $d |
	($d | join("/") | "mkdir -p \"" + . + "\"") ' pack.json
jq -r '([.folder as $f | $f | path(.. | .name?) as $a |
	[$a | ["name"], foreach .[] as $i ([]; . + [$i]; if $i | type == "number" then . + ["name"] else empty end) ] as $b |
	[$b | .[] as $c | $f | getpath($c) ] as $d |
	{"value": $d | join("/"), "key": $f | getpath(($a | .[:-1]) + ["id"])}] | from_entries) as $d |
		.images | .[] as $i | $i | .folders | .[] as $f | $d | getpath([$f]) as $p |
		$i | select($p) | "ln -f \"\(.id).info/\(.name).\(.ext)\" \"\($p)\""' pack.json
jq -r '.folder as $f | $f | path(.. | .name?) as $a |
	[$a | ["name"], foreach .[] as $i ([]; . + [$i]; if $i | type == "number" then . + ["name"] else empty end) ] as $b |
	[$b | .[] as $c | $f | getpath($c) ] as $d |
	"touch \"\($d | join("/"))\" -d @\($f | getpath(($a | .[:-1]) + ["modificationTime"]) | . / 1000)" ' pack.json
)"
time sh -s <<< "$CMD"
#echo "$CMD"
echo Done
