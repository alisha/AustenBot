#!/usr/bin/python

from random import randrange
import sys, os, tweepy
from secret import *

# Get words
corpusPath = os.path.dirname(os.path.realpath(__file__)) + "/corpus.txt"
corpus = open(corpusPath, "r")
wordLines = corpus.readlines()

for line in range(0, len(wordLines)-2):
	wordLines[line] = wordLines[line][:-1]

corpus.close()

# Store the start of sentences
sentenceStarters = []

# Create graph of words
def createWordMap(wordLines):
	wordMap = dict()

	for line in wordLines:
		
		words = line.split()

		endOfSentence = True
		
		for index in range(0,len(words)-2):
			
			# Add to list of sentence starters
			if endOfSentence:
				sentenceStarters.append((words[index], words[index + 1]))
				endOfSentence = False

			# Check if at the end of sentence
			if words[index + 1] == "?" or words[index + 1] == "." or words[index + 1] == "!":
				endOfSentence = True

			# Add to word map
			wordMap[(words[index], words[index + 1])] = words[index + 2]

	return wordMap

# Returns true if the contents of the array is under Twitter's character limit
def underLimit(array):
	return len(' '.join(array)) < 140

# Generate tweet
def genTweet(wordMap):
	index = randrange(len(sentenceStarters) - 1)

	firstWord = sentenceStarters[index][0]
	secondWord = sentenceStarters[index][1]
	thirdWord = wordMap[(firstWord, secondWord)]
	
	# holds an array of all words in the tweet
	tweetArray = [firstWord, secondWord, thirdWord]

	while underLimit(tweetArray) is True:
		end = len(tweetArray)
		lastElements = [tweetArray[end-2], tweetArray[end-1]]

		clonedTweetArray = list(tweetArray)
		
		if (lastElements[0], lastElements[1]) in wordMap:
			clonedTweetArray.append(wordMap[(lastElements[0], lastElements[1])])
		else:
			return tweetArray

		if underLimit(clonedTweetArray) is True:
			tweetArray = clonedTweetArray
		else:
			return tweetArray

# Get and trim message
def createGoodTweet(wordLines):
	hasMessage = False
	
	while hasMessage is False:

		# generate tweet array and turn into string
		tweet = genTweet(createWordMap(wordLines))
		message = ' '.join(tweet)
		
		# don't end on something like "mr."
		currentChar = len(message) - 1
		lastPeriod = 0

		while currentChar >= 0:
			newMessage = message
			char = newMessage[currentChar]
			
			if char is ".":
				lastPeriod = currentChar
				currentChar = -1
			else:
				currentChar = currentChar - 1

		message = message[0:lastPeriod+1]

		if len(message) is not 1 and message[0].isalpha():
			hasMessage = True

	# capitalize first letter
	message.capitalize()

	return message

# Publish to Twitter
def tweet():
	auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
	auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
	api = tweepy.API(auth)

	message = createGoodTweet(wordLines)
	try:
		api.update_status(message)
		tweeted = True
	except TweepyError:
		print "Found duplicate tweet"

tweet()
