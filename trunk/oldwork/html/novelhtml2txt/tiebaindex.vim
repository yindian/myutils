%s/"\(\%(http:..\%(tieba\|post\).baidu.com[^\/]*\)\=\/f?kz=\d\+\)"/>\1/g
%s/^[^>].*/
%s/^\n/
%s/\n$/
%s/^>/
%s+^/+http://tieba.baidu.com/+
