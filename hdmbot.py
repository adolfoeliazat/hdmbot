#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import tweepy 			# library for accessing the Twitter API
import urllib 			# open arbitrary resources by URL
import os 				# miscellaneous operating system interface
from PIL import Image 	# Python Imaging Library
import logging			# logging facility for Python

import threading
import schedule
import datetime
import time

import keys

auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.access_token, keys.access_token_secret)
api = tweepy.API(auth)

# the bot's name on Twitter (without the '@')
self = 'hdm_bot'

class StreamListener(tweepy.StreamListener):
	
	def on_status(self, tweet):
		
		# full text as string without imagelink(s) & '@hdm_bot' at the beginning
		tweettext = ''
		# list of all image-urls
		imgurls = []

		# ignore retweets
		if not tweet.retweeted:	 
			# now get text and image-url(s) from tweet
			
			# is it truncated due to 140 char limit?
			# NO it is not truncated
			if not tweet.truncated:
				if hasattr(tweet, 'extended_entities'):
					if ('media' in tweet.extended_entities):
						tweettext = tweet.text[:len(tweettext)-23] # cut link at end of tweet
						for image in tweet.extended_entities['media']:
							imgurls.append(image['media_url'])
				else:
					tweettext = tweet.text		
			# YES, it is truncated
			else:
				tweettext = tweet.extended_tweet['full_text'] 	
				if hasattr(tweet, 'extended_tweet'):
					if 'media' in tweet.extended_tweet['entities']:
						tweettext = tweettext[:len(tweettext)-23]
						for image in tweet.extended_tweet['entities']['media']:
							imgurls.append(image['media_url'])
		
			# write tweet in logfile
			# print ('(' + str(tweet.id) + ') ' + tweet.user.screen_name + ': ' + tweettext)
			logging.critical('(' + str(tweet.id) + ') ' + tweet.user.screen_name + ': ' + tweettext)		
		
			# react to specific hashtags
			if '#workshop' in tweettext:
				api.update_status(('Herzlich Wilkommen im #Workshop über #socialbots!'))
			if '#followme' in tweettext:
				api.create_friendship(tweet.user.screen_name)

			# check if there are images
			if len(imgurls) > 0:
				logging.critical('(' + str(tweet.id) + ') processing ' + str(len(imgurls)) + ' image(s)...')
			# check if tweet begins with '@hdm_bot'
			if tweettext[:9] == '@hdm_bot ':
				if len(tweettext) == 9: # '@hdm_bot' on the beginning is only text
					tweettext = 'Happy Medianight!' # write some default stuff on picture
				elif len(tweettext) > 9: # '@hdm_bot' is not the only text
					tweettext = tweettext[9:] # delete @hdm_bot on beginning, keep text

			# image processing
			for i in range(len(imgurls)):
				picname = "%s_%i" % (str(tweet.id), i+1)
				filename = os.path.join("./images/", picname + '.jpg')
				urllib.urlretrieve(imgurls[i], filename)

				with Image.open(filename) as img:
					width, height = img.size

				fontsize = 72
				if len(tweettext) > 40:
					fontsize = 50

				# edit/create image
				os.system('convert -background \'#00000080\' -fill white -font \'/usr/share/fonts/truetype/roboto/hinted/Roboto-Regular.ttf\' -size %ix -pointsize 40 caption:\'%s\' miff:- | composite -gravity south -geometry +0+0 - %s ./images/%s_reply.jpg' % (width, tweettext.encode("utf8","ignore"), filename, picname))
				#add logo
				os.system('composite -gravity NorthEast ./images/logo.png ./images/%s_reply.jpg ./images/%s_reply.jpg' % (picname, picname))
				os.system('cp ./images/%s_reply.jpg /var/www/hdmbot/images/%s.jpg' % (picname, picname)) 
				# answer with tweet
                                logging.critical('(' + str(tweet.id) + ') posting processed image ( http://45.77.67.24/hdmbot/images/' + picname + '.jpg )')
				api.update_with_media('./images/%s_reply.jpg' % picname, '@' + tweet.user.screen_name + ' #medianight #socialbots')	# post image @user
			    # api.create_friendship(status.user.screen_name)	# create friendship with user

	def on_error(self, status_code):
		if status_code == 420:	# rate limited
			# print ('420: rate limited')
			logging.warn('Rate Limited!')
			return False	


logging.basicConfig(filename='hdmbot.log', format='%(asctime)s : %(message)s', datefmt='%d.%m.%Y %k:%M:%S', level=logging.CRITICAL)
logging.critical('##### hdmbot started #####')

myStreamListener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=myStreamListener)	
def thread_stream():
	stream.filter(track=['@hdm_bot'], async=True)

def post_xdaysleft():
	api.update_status('Die #Medianight rückt näher! Noch ' + str((datetime.datetime(2017,06,29)-datetime.datetime.now()).days) + ' Tage. #hochschuledermedien #socialbots')
        logging.critical('Posted daily countdown to Medianight')

schedule.every().day.at("18:00").do(post_xdaysleft)
#schedule.every(1).second.do(post_xdaysleft)

def thread_countdown():
	while True:
		schedule.run_pending()
		time.sleep(1)


threading.Thread(target=thread_stream).start()
threading.Thread(target=thread_countdown).start()

