#!/usr/bin/env python
#-*- coding: utf-8 -*-

import twitter
from module import remove_stopwords
import igo.Tagger
from google.appengine.ext import db
from random import choice
import re

tagger = igo.Tagger.Tagger('ipadic_gae', gae=True)

# pika_shiの認証
CONSUMER_KEY="gtCXsTWe36CVbW5XzatYSg"
CONSUMER_SECRET="igYhRFLGC3aeGnNst8VbWOVbbrK854NRtlJvravO8U"
ACCESS_TOKEN="141077154-YAcEuL6qZIifys2jN4vLqrtTsWrgQHQiM8qbXrch"
ACCESS_TOKEN_SECRET="Ry09sYcYuh9cWEldXsmQn9ooJVlkIspxbQUHyX0Ls"

api = twitter.Api(consumer_key=CONSUMER_KEY,
                      consumer_secret=CONSUMER_SECRET,
                      access_token_key=ACCESS_TOKEN,
                      access_token_secret=ACCESS_TOKEN_SECRET,
                      cache=None)

# pika_shi_botの認証
bot_CONSUMER_KEY="lBqP8HaZkCbawFJLNWS1kQ"
bot_CONSUMER_SECRET="YMj1GwIskLJTyRc4vn03yyJmau8oYSB0wknPfKR3Vec"
bot_ACCESS_TOKEN="356707929-uMDe1JQx2BOsLakWIg7MdNW0WKcSchpM0qh4CV02"
bot_ACCESS_TOKEN_SECRET="hlWR74q54JUgOhFVr3Qibrrzs8XrMdjqdgHw2w7vZc"

bot_api = twitter.Api(consumer_key=bot_CONSUMER_KEY,
                      consumer_secret=bot_CONSUMER_SECRET,
                      access_token_key=bot_ACCESS_TOKEN,
                      access_token_secret=bot_ACCESS_TOKEN_SECRET,
                      cache=None)

class TweetModel(db.Model):
  id = db.IntegerProperty() # tweetのid
  tweet = db.StringProperty(multiline=True) # tweetの内容

class WordModel(db.Model):
  word = db.StringProperty() # 単語
  id_list = db.ListProperty(item_type=long,default=[]) # その単語が含まれるtweetのidのリスト
  count = db.IntegerProperty(default=0) # その単語が含まれるtweetの数

# 正規表現パターン
p1 = 'ぴか(し|に(い|ぃ))(いけめん|イケメン|はんさむ|ハンサム)'
p2 = 'ぴか(し|に(い|ぃ))かわいい'
p3 = 'ぴか(し|に(い|ぃ))(ど|ド)(Ｍ|M|えむ|エム)'

# compile
re1 = re.compile(p1)
re2 = re.compile(p2)
re3 = re.compile(p3)

# TL取得
TL = api.GetFriendsTimeline()
for tweet in TL:
    # tweetがDBに登録されていない場合
    if TweetModel.all().filter('id =', tweet.id).get() == None:
        # reply除去
        while 1:
            if tweet.text[0] == '@':
                tweet.text = tweet.text[tweet.text.find(' ')+1:len(tweet.text)]
            else:
                break
        # @,[]を含むtweetは除去
        if tweet.text.find('@') != -1 or tweet.text.find('[') != -1:
            continue
        # 長いtweet or 空tweet は除去
        if len(tweet.text) > 40 or len(tweet.text) == 0:
            continue
        # reply
        if re1.scanner(tweet.text.encode('utf-8')).search() != None:
            postmsg = '@'.decode("utf-8") + tweet.user.screen_name.decode("utf-8") + choice([' ｷﾘｯ',' さんくす(・∀・)',' そんなことないよ！',' うれしいでござる',' 言うまでもないがなｗ']).decode("utf-8")
            bot_api.PostUpdate(postmsg)
        if re2.scanner(tweet.text.encode('utf-8')).search() != None:
            postmsg = '@'.decode("utf-8") + tweet.user.screen_name.decode("utf-8") + choice([' てへっ',' (´ω`)',' 君には負けるぜ(ｷﾘｯ',' まあね',' どこがやｗ']).decode("utf-8")
            bot_api.PostUpdate(postmsg)
        if re3.scanner(tweet.text.encode('utf-8')).search() != None:
            postmsg = '@'.decode("utf-8") + tweet.user.screen_name.decode("utf-8") + choice([' ばれてますやんｗ',' もっといじめて！',' ギクッ']).decode("utf-8")
            bot_api.PostUpdate(postmsg)
        # DBに登録
        tweetmodel = TweetModel(id=tweet.id, tweet=tweet.text)
        tweetmodel.put()

        # 形態素解析
        l = tagger.parse(tweet.text)
        for m in l:
            # 名詞かつ日本語かつ2文字以上かつストップワードでないものを抽出
            if m.feature.split(',')[0] == u"名詞" and m.feature.split(',')[len(m.feature.split(','))-1] != u"*" and len(m.surface) >= 2 and not remove_stopwords(m.surface):
                # wordがDBに登録されていない場合
                if WordModel.all().filter('word =', m.surface).get() == None:
                    # DBに登録 
                    wordmodel = WordModel(word=m.surface)
                else:
                    # wordをfetchする
                    wordmodel = WordModel.all().filter('word =', m.surface).get()
                    # 同じtweetに複数出てくるwordは除去
                    if tweet.id in wordmodel.id_list:
                        continue
                # DBを更新
                wordmodel.id_list.append(tweet.id)
                wordmodel.count = int(wordmodel.count)+1
                wordmodel.put()