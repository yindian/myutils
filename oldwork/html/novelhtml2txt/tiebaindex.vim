%s/"\(\%(http:..\%(tieba\|post\).baidu.com[^\/]*\)\=\/f?kz=\d\+\)"/
%s/^[^>].*/
%s/^\n/
%s/\n$/
%s/^>/
%s+^/+http://tieba.baidu.com/+