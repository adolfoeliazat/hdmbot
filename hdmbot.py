#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import tweepy
import urllib
import os
from PIL import Image 
import logging

auth = tweepy.OAuthHandler('vBRGejyUwo4SODXHBKuA8Q7oE', 'NIncJA2K07omhlVl14CHJtsvMiaGoGwo2nDzdfMCpuQCfAifQD')
auth.set_access_token('860453090696343552-VXXxo95CWAoE4zfbpo0Q4zdQbbxJ0r4', 'qZ6LtE7TcB6yLxniSTm9kHrW5PghRu6Yxx26zT5SQzA9V')
api = tweepy.API(auth)
self = 'hfeistos'

class StreamListener(tweepy.StreamListener):
    def on_status(self, tweet):
        txt = ''
	imgurl = []

	if not tweet.retweeted:	# ignore retweets 
	    if not tweet.truncated:	# tweet Is not truncated due to 140 char limit
		txt = tweet.text
		if ('media' in tweet.entities):
			txt = txt[:len(txt)-23]
			for image in tweet.entities['media']:
	        	    imgurl.append(image['media_url'])
	    else: # tweet is truncated: now get full_text
		txt = tweet.extended_tweet['full_text'] 	
		if 'media' in tweet.extended_tweet['entities']:
	            txt = txt[:len(txt)-23]
		    for image in tweet.extended_tweet['entities']['media']:
		        imgurl.append(image['media_url'])
	
	    # write tweet on console
	    # print ('(' + str(tweet.id) + ') ' + tweet.user.screen_name + ': ' + txt)
            logging.info('(' + str(tweet.id) + ') ' + tweet.user.screen_name + ': ' + txt)		
	
            if '#workshop' in txt:
		api.update_status(('Herzlich Wilkommen im #Workshop über #socialbots!'))
	    if '#followme' in txt:
		api.create_friendship(tweet.user.screen_name)

	    # check if there are images
	    if len(imgurl) > 0:
                logging.info('(' + str(tweet.id) + ') ''processing image(s)...')
		if txt[:10] == '@hfeistos ':
		    if len(txt) == 10:	# no more text, except @hfeistos on beginning
		        txt = 'Happy Medianight!'
		    elif len(txt) > 10:
			txt = txt[10:] # delete @hfeistos on beginning

	        # image processing
		for i in range(len(imgurl)):
		    picname = "%s_%i" % (str(tweet.id), i+1)
		    filename = os.path.join("./images/", picname + '.jpg')
		    urllib.urlretrieve(imgurl[i], filename)
                    
                    with Image.open(filename) as img:
		        width, height = img.size
		    
                    fontsize = 72
		    if len(txt) > 40:
		        fontsize = 50

		    # edit/create image
		    os.system('convert -background \'#00000080\' -fill white -font \'/usr/share/fonts/truetype/roboto/hinted/Roboto-Regular.ttf\' -size %ix -pointsize 40 caption:\'%s\' miff:- | composite -gravity south -geometry +0+0 - %s ./images/%s_reply.jpg' % (width, txt.encode("utf8","ignore"), filename, picname))
		    #add logo
                    os.system('composite -gravity NorthEast ./images/logo.png ./images/%s_reply.jpg ./images/%s_reply.jpg' % (picname, picname))
                    os.system('cp ./images/%s_reply.jpg /var/www/html/hdmbot/images/%s.jpg' % (picname, picname)) 
                    # answer with tweet
                    logging.info('(' + str(tweet.id) + ') posting processed image')
		    api.update_with_media('./images/%s_reply.jpg' % picname, '@' + tweet.user.screen_name + ' #medianight #socialbots')	# post image @user
		    # api.create_friendship(status.user.screen_name)	# create friendship with user

    def on_error(self, status_code):
        if status_code == 420:	# rate limited
	    # print ('420: rate limited')
	    logging.warn('Rate Limited!')
            return False	


logging.basicConfig(filename='hdmbot.log', format='%(asctime)s : %(message)s', datefmt='%d.%m.%Y %H:%M:%S', level=logging.INFO)
logging.info('##### hdmbot started #####')

myStreamListener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=myStreamListener)	
stream.filter(track=['@hfeistos'])
