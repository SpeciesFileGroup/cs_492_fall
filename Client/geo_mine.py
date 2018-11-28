#title           :geo_mine.py
#author          :Herbert Wang
#date            :20181120
#usage           :Called from client.py, for debuggin: python geo_mine.py
#python_version  :Python 2.7.15rc1
#==============================================================================

import os
import collections
import nltk as nk
from nltk.chunk import conlltags2tree, tree2conlltags
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.tag import StanfordNERTagger
import re
import spacy
import nltk.data
# for local testing, put the ner.jar and .gz file path here
ner_tagger = StanfordNERTagger(
	    '/mnt/c/Users/herbe/CS493/cs_492_fall/nre/classifiers/english.all.3class.distsim.crf.ser.gz',
	    '/mnt/c/Users/herbe/CS493/cs_492_fall/nre/stanford-ner.jar', encoding='utf8')

## for running on remote server
# ner_tagger = StanfordNERTagger(
# 	    '/home/rwang67/cs_492_fall/nre/classifiers/english.all.3class.distsim.crf.ser.gz',
# 	    '/home/rwang67/cs_492_fall/nre/stanford-ner.jar', encoding='utf8')


tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')


def geo(textInput):
	file_input = re.sub(r'[^\x00-\x7F]+',' ', textInput)
	ne_tree = nk.ne_chunk(nk.pos_tag(nk.word_tokenize(file_input)))
	# ne_tree = nk.ne_chunk(nk.pos_tag(nk.word_tokenize(sentence)))
	
	iob_tagged = tree2conlltags(ne_tree)
	myset = set()
	for i in iob_tagged:
		if(i[2] == 'B-GPE'):
			myset.add(i[0])

	return list(myset)

# Tokelize the page into sentences and find geo entity that is radius of "sentence" away instead of number of character away
# This is slower than distance by character
# Using Stanford NLTK library
def nltk_mine(article, list_value, radius):
	mydic = {}
	article = str(article)
	sentence_split = tokenizer.tokenize(str(article))
	for cur_value in list_value:
		cur_value = str(cur_value)
		cur_sentence = ''
		for idx in range(len(sentence_split)):
			if cur_value in sentence_split[idx]:
				cur_sentence = sentence_split[idx]
				if idx >= (0 + radius):
					cur_sentence += "".join(sentence_split[idx-radius: idx])
				if idx <= (len(sentence_split) - radius):
					cur_sentence += "".join(sentence_split[idx+1: idx+radius+1])
		words = nk.word_tokenize(cur_sentence)

		try:
			results = ner_tagger.tag(words)
		except GeneratorExit:
			print "Generator exiting!"
		
		myset = set()
		for result in results:
			if result[1] == "LOCATION":
				myset.add(result[0])
		mydic[cur_value] = list(myset)
	return mydic

# given a page.name, i.e, a page that contains names, extract all the name string from it
def path_split(name_string):
	myset = set()
	for i in name_string:
		myset.add((i.value).encode('utf-8'))
	return list(myset)

# Tokelize the page into sentences and find geo entity that is radius of "characters" away instead of number of senetence away
# This is faster than distance by character
# Using either Stanford NLTK library or Spacy library
def nltk_dist(page_list, name_list, title_id_list, nlp, output):
	ret = {}
	for i in range(len(page_list)):
		mydic = {}
		article = page_list[i]
		list_value = path_split(name_list[i])
		title_id = title_id_list[i]

		# article, list_value, title_id
		if len(list_value) == 0 or article == '':
			continue

#=========================Stanford NLTK Library =========================
		# geo_word_loc = []
		# article = article.decode('utf-8').strip()
		# print(article)
		# words = nk.word_tokenize(article)
		# results = ner_tagger.tag(words)
		# for result in results:
		# 	if result[1] == "LOCATION":
		# 		location = article.find(result[0])
		# 		geo_word_loc.append(location)
		# 		mydic.update({location : result[0]})  # location -> geo entity
#=========================Spacy https://spacy.io/ =========================
		geo_word_loc = []
		article = article.decode('utf-8').strip()
		doc = nlp(article)
		for entity in doc.ents:
			if entity.label_ == "GPE":
				location = article.find(entity.text)
				geo_word_loc.append(location)
				mydic.update({location : entity.text})  # location -> geo entity
#========================================================================
		if len(geo_word_loc) == 0:
			continue		
		for name in list_value:
			ret.update({name: []})
			for name_loc in [m.start() for m in re.finditer(name, article)]: #Find all the location that a name string appear in the page
				closet_loc = min(geo_word_loc, key=lambda x:abs(x-name_loc))
				ret[name].append((abs(name_loc-closet_loc), mydic[closet_loc].encode('utf-8'), title_id))
	
	output.put(ret)
	# return ret


# Main function here for debugging purpose only
def main():
	# fname = "myfile.txt"
	# lines = [line.rstrip('\n') for line in open(fname)]
	# file_input = ' '.join(lines).replace('\n', ' ').replace('\r', '')
	# ret = geo(file_input)
	# print(ret)

	# ner_tagger = StanfordNERTagger(
	#     '/mnt/c/Users/herbe/CS493/cs_492_fall/nre/classifiers/english.all.3class.distsim.crf.ser.gz',
	#     '/mnt/c/Users/herbe/CS493/cs_492_fall/nre/stanford-ner.jar', encoding='utf8')

	fname = "myfile.txt"
	lines = [line.rstrip('\n') for line in open(fname)]
	file_input = ' '.join(lines).replace('\n', ' ').replace('\r', '')
	list_value = ['Hydrocena', 'Bourciera', 'Tudora', 'Cyclotus', 'Schasicheila', 'Bulimus', 'Megalomastoma']
	print(nltk_mine(file_input, list_value, 1))
	# article = u"The university was founded in 1885 by Leland and Jane Stanford in memory of their only child, Leland Stanford Jr., who had died of typhoid fever at age 15 the previous year. Stanford was a former Governor of California and U.S. Senator; he made his fortune as a railroad tycoon. The school admitted its first students on October 1, 1891,[2][3] as a coeducational and non-denominational institution."
	# words = nk.word_tokenize(article)
	# results = ner_tagger.tag(words)
	# ret = []
	# for result in results:
	# 	if result[1] == "LOCATION":
	# 		ret.append(result[0])
	# print(ret)

	# tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	# fp = open("myfile.txt")
	# data = fp.read()

	# sentence_split = tokenizer.tokenize(data)

if __name__ == "__main__":
	main()