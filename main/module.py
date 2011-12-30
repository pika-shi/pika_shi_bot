#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ストップワードの除去
def remove_stopwords(word):
    seq = []

    f = open('Japanese.txt','r')
    while 1:
        s = f.readline().rstrip()
        if not s:
            break
        seq.append(unicode(s,'utf-8'))
    f.close()

    stopwords = frozenset(seq)
    #print type(stopwords)
    return word in stopwords

if __name__ == '__main__':
    print remove_stopwords(u'今日')
