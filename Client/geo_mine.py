import os
import collections
import nltk as nk
from nltk.chunk import conlltags2tree, tree2conlltags
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.tag import StanfordNERTagger
import re
import nltk.data
# ner_tagger = StanfordNERTagger(
# 	    '/mnt/c/Users/herbe/CS493/cs_492_fall/nre/classifiers/english.all.3class.distsim.crf.ser.gz',
# 	    '/mnt/c/Users/herbe/CS493/cs_492_fall/nre/stanford-ner.jar', encoding='utf8')
ner_tagger = StanfordNERTagger(
	    '/home/rwang67/cs_492_fall/nre/classifiers/english.all.3class.distsim.crf.ser.gz',
	    '/home/rwang67/cs_492_fall/nre/stanford-ner.jar', encoding='utf8')
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


def nltk_dist(article, list_value):
	mydic = {}
	if len(list_value) == 0 or article == '':
		return {}
	geo_word_loc = []
	ret = {}
	article = article.decode('utf-8').strip()
	words = nk.word_tokenize(article)
	try:
		results = ner_tagger.tag(words)
	except GeneratorExit:
		print "Generator exiting!"
	for result in results:
		if result[1] == "LOCATION":
			location = article.find(result[0])
			geo_word_loc.append(location)
			mydic.update({location : result[0]})

	if len(geo_word_loc) == 0:
		return {}
	for name in list_value:
		ret.update({name: []})
		for name_loc in [m.start() for m in re.finditer(name, article)]:
			closet_loc = min(geo_word_loc, key=lambda x:abs(x-name_loc))
			ret[name].append((abs(name_loc-closet_loc), str(mydic[closet_loc])))
	return ret

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

# import os
# import collections
# import nltk as nk
# from nltk.chunk import conlltags2tree, tree2conlltags
# from nltk import word_tokenize, pos_tag, ne_chunk
# import re
# def main():
# 	sentence = "Mark and John are working at Google in China."
# 	fname = "myfile.txt"
# 	lines = [line.rstrip('\n') for line in open(fname)]
# 	file_input = ' '.join(lines)
# 	file_input = re.sub(r'[^\x00-\x7F]+',' ', file_input)
# 	ne_tree = nk.ne_chunk(nk.pos_tag(nk.word_tokenize(file_input)))
# 	# ne_tree = nk.ne_chunk(nk.pos_tag(nk.word_tokenize(sentence)))
	
# 	iob_tagged = tree2conlltags(ne_tree)

# 	for i in iob_tagged:
# 		if(i[2] == 'B-GPE'):
# 			print(i[0])


# 	ner_tags = collections.Counter()
# 	corpus_root = "myfile.txt"   # Make sure you set the proper path to the unzipped corpus
	 
# 	for root, dirs, files in os.walk(	):
# 		print("why")
# 		for filename in files:
# 			if filename.endswith(".tags"):
# 			    with open(os.path.join(root, filename), 'rb') as file_handle:
# 			        file_content = file_handle.read().decode('utf-8').strip()
# 			        annotated_sentences = file_content.split('\n\n')   # Split sentences
# 			        for annotated_sentence in annotated_sentences:
# 			            annotated_tokens = [seq for seq in annotated_sentence.split('\n') if seq]  # Split words

# 			            standard_form_tokens = []

# 			            for idx, annotated_token in enumerate(annotated_tokens):
# 			                annotations = annotated_token.split('\t')   # Split annotations
# 			                word, tag, ner = annotations[0], annotations[1], annotations[3]

# 			                ner_tags[ner] += 1
	 
# 	print (ner_tags)


# if __name__ == "__main__":
# 	main()







