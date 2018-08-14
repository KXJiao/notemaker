import gensim
import time
import string
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
from  nltk.tokenize import sent_tokenize
from nltk.stem import PorterStemmer
from . import bioSearchTree as bst
import re
import math
import os
import gzip
from urllib.request import urlopen
import io

def add(dic,k,v):
	if k in dic.keys():
		temp=dic[k]
		temp.add(v)
		dic[k]=temp
	else:
		dic[k]=set([v])

def addOne(dic,k):
	if k in dic.keys():
		temp=dic[k]
		temp+=1
		dic[k]=temp
	else:
		dic[k]=1

def summary(text, num):
	start = time.time()
	
	# baseURL = "https://raw.githubusercontent.com/eyaler/word2vec-slim/master/"
	# filename = "GoogleNews-vectors-negative300-SLIM.bin.gz"
	# outFilePath = "GoogleNews-vectors-negative300-SLIM.bin"
	# response = urlopen(baseURL + filename)
	# compressedFile = io.BytesIO(response.read())
	# decompressedFile = gzip.GzipFile(fileobj=compressedFile)
	print("summary started")
	basedir = os.path.abspath(os.path.dirname(__file__))
	googlepath = os.path.join(basedir, "static", "GoogleNews-vectors-negative300.bin")
	#"https://s3.amazonaws.com/dl4j-distribution/GoogleNews-vectors-negative300.bin.gz"
	model=gensim.models.KeyedVectors.load_word2vec_format(googlepath, binary=True, limit=100000)
	#words=open("subInfo.txt").read()
	print("loaded GoogleNews-vectors-negative300")
	words = text
	txt = words

	bioTerms=bst.retList()
	bioPhrases=[term for term in bioTerms if " " in term]
	phsWords=[]
	for ph in bioPhrases:
		a = re.search(r"\b(?=\w)" + re.escape(ph) + r"\b(?!\w)",words,re.IGNORECASE)
		while a is not None:
			words=words[:a.start()]+words[a.end():]
			phsWords.append(ph)		
			a = re.search(r"\b(?=\w)" + re.escape(ph) + r"\b(?!\w)",words,re.IGNORECASE)

	tknzr = TweetTokenizer()
	words=tknzr.tokenize(words)
	words=words+phsWords
	words=[w for w in words if not w in string.punctuation]
	#words = [w[0].lower()+w[1:] if w[0].lower()+w[1:] in model.vocab else w for w in words]
	stop_words = set(stopwords.words('english'))
	words = [w for w in words if not w in stop_words]
	words = [w for w in words if len(w)>1 or w in string.ascii_letters or w in string.digits]
	setWords=set(words)
	setWords=list(setWords)
	#print(words)
	#print(setWords)

	graph={}
	pairGraph={}
	notCons=set()
	for i in range(len(setWords)):
		for x in range(len(setWords)):
			if x != i:
				if setWords[i] not in model.vocab:
					notCons.add(setWords[i])			
				elif setWords[x] not in model.vocab:
					notCons.add(setWords[x])
				else:
					similVal=model.similarity(setWords[i],setWords[x])
					dup=(similVal,setWords[x])
					add(graph,setWords[i],dup)
					pairGraph[(setWords[i],setWords[x])]=similVal
					pairGraph[(setWords[x],setWords[i])]=similVal
	#print(notCons)
	### Algorithm ###
	keyTerms=[t for t in setWords if t in bioTerms or t[0].lower()+t[1:] in bioTerms]
	# finding frequencies
	freqDic={}
	wToStem={}
	ps = PorterStemmer()
	for t in words:
		stem=ps.stem(t)
		addOne(freqDic,stem)
		wToStem[t]=stem
	# calculation for avg. freq.
	freqArr=[freqDic[k] for k in freqDic.keys()]
	tot=sum(freqArr)
	avgFreq=tot/(len(freqArr))
	###
	# context calculation
	pardCount=0
	for kt in keyTerms:
		if kt in notCons:
			pardCount+=1
	divNum=len(keyTerms)-pardCount
	contDic={}
	for t in setWords:
		if t not in notCons and t not in keyTerms:
			contScore=0
			for kt in keyTerms:
				if kt not in notCons:
					contScore+=pairGraph[(kt,t)]
			contDic[t]=contScore/divNum
	###
	# finding avg context score
	contArr=[contDic[k] for k in contDic.keys()]
	tot=sum(contArr)
	avgCont=tot/(len(contArr))
	###
	# giving context score to notCons and keyTerms
	for t in notCons:
		if t not in keyTerms:
			contDic[t]=avgCont
	for t in keyTerms:
		contDic[t]=1
	# finding the importance of each term
	termVal={}
	print(avgFreq)
	for t in setWords:
		termVal[t]=contDic[t]*12 + (freqDic[wToStem[t]]-avgFreq)*1  #Vary results by changing factors
		print(t+": "+ str(contDic[t]*12)+ " + "+ str(freqDic[wToStem[t]]-avgFreq) + " ("+wToStem[t]+": "+str(freqDic[wToStem[t]])+")")
	###
	#finding important sentences
	sentScoreDic={}
	sents=sent_tokenize(txt)
	for sen in sents:
		sentScore=0
		for t in setWords:
			hits=[m.start() for m in re.finditer(r"\b" +re.escape(t)+r"\b", sen)]
			#sentScore+=len(hits)*termVal[t]
			if len(hits)>0:
				sentScore+=termVal[t]
		sentScoreDic[sen]=sentScore

	dicCopy = dict(sentScoreDic)
	sentScoreArr=[]
	while dicCopy.keys():
		maxNum=-math.inf
		for i in dicCopy.keys():
			if dicCopy[i]>maxNum:
				maxNum=dicCopy[i]
				corSent=i
		sentScoreArr.append((corSent,maxNum))
		del dicCopy[corSent]

	print(sentScoreArr[:5])

	
	end=time.time()-start
	print("time: "+ str(end))
	return sentScoreArr[:num]
