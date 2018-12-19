#title           :Topic_Model.py
#author          :Herbert Wang
#date            :20181101
#usage           :Called from server.py, used when client stream pages to server, server run topic modeling and streams back the result
#python_version  :Python 2.7.15rc1
#==============================================================================
# Source: https://towardsdatascience.com/topic-modeling-and-latent-dirichlet-allocation-in-python-9bf156893c24
# Source: https://medium.com/mlreview/topic-modeling-with-scikit-learn-e80d33668730
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.datasets import fetch_20newsgroups
from sklearn.decomposition import NMF, LatentDirichletAllocation

class Topic_Model():
	global display_topics
	def __init__(self):
		self.documents = []
		self.no_topics = 3
		self.no_top_words = 5
		self.no_features = 1000

	def display_topics(model, feature_names, no_top_words):
	    for topic_idx, topic in enumerate(model.components_):
	        print ("Topic %d:" % (topic_idx))
	        print (" ".join([feature_names[i]
	                        for i in topic.argsort()[:-no_top_words - 1:-1]]))

	def train(self, documents, no_topics, no_top_words):
		# dataset = fetch_20newsgroups(shuffle=True, random_state=1, remove=('headers', 'footers', 'quotes'))
		# documents = dataset.data
		self.no_topics = no_topics
		self.no_top_words = no_top_words
		self.documents = documents

	# TF-IDF
	def tf_idf(self):
		# NMF is able to use tf-idf
		tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=self.no_features, stop_words='english')
		tfidf = tfidf_vectorizer.fit_transform(self.documents)
		tfidf_feature_names = tfidf_vectorizer.get_feature_names()
		# Run NMF
		nmf = NMF(n_components=self.no_topics, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)
		display_topics(nmf, tfidf_feature_names, self.no_top_words)

	# Latent Dirichlet allocations
	def lda(self):
		# LDA can only use raw term counts for LDA because it is a probabilistic graphical model
		tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=self.no_features, stop_words='english')
		tf = tf_vectorizer.fit_transform(self.documents)
		tf_feature_names = tf_vectorizer.get_feature_names()
		# Run LDA
		lda = LatentDirichletAllocation(n_topics=self.no_topics, max_iter=5, learning_method='online', learning_offset=50.,random_state=0).fit(tf)
		display_topics(lda, tf_feature_names, self.no_top_words)