#!/bin/sh
awk -F '|' '{s=gensub(/^[| ]*-/,"",1);n=NF-1;a[n]=s;for(i=1;i<n;++i)printf("%s/",a[i]);printf("%s\n",s)}' "$@"
