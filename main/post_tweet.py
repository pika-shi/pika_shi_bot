#!/usr/bin/env python
#-*- coding: utf-8 -*-

import twitter
import random
from google.appengine.ext import db
import datetime

d = datetime.datetime.today()

# pika_shi_botの認証
bot_CONSUMER_KEY="lBqP8HaZkCbawFJLNWS1kQ"
bot_CONSUMER_SECRET="YMj1GwIskLJTyRc4vn03yyJmau8oYSB0wknPfKR3Vec"
bot_ACCESS_TOKEN="356707929-uMDe1JQx2BOsLakWIg7MdNW0WKcSchpM0qh4CV02"
bot_ACCESS_TOKEN_SECRET="hlWR74q54JUgOhFVr3Qibrrzs8XrMdjqdgHw2w7vZc"

api = twitter.Api(consumer_key=bot_CONSUMER_KEY,
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

# 0~8時(日本時間)はtweetしない
if d.hour <= 14 or d.hour == 23:
    # countの最大値を取得
    max = WordModel.all().order('-count').get().count

    # 最頻出単語の検索
    wordmodels = WordModel.all().filter('count =', max)

    # 最頻出単語を含むtweetのidのリストを生成
    id_list = []
    for wordmodel in wordmodels:
        id_list.extend(wordmodel.id_list)
    
    # その中からランダムで1つを選択し、post
    id = random.choice(id_list)
    tweet = TweetModel.all().filter('id =', id).get().tweet
    api.PostUpdate(tweet)

# TweetModel,WordModelのエンティティを削除
db.delete(TweetModel.all())
db.delete(WordModel.all())