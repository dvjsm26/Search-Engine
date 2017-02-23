import nltk
from nltk.corpus import reuters
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize
import re
import string
from string import *
from nltk.stem import *
from nltk.stem.porter import *
import math
import re
import enchant
import fnmatch
from heapq import nlargest

N = 400
index = {}
terms = []
Length = [0] * N
stop_words = set(stopwords.words('english'))

#for spell correction
class SpellingReplacer(object):
    def __init__(self, dict_name='en_US'):
        self.spell_dict = enchant.Dict(dict_name)

    def replace(self, word):
        if self.spell_dict.check(word):
            return word
        suggestions = self.spell_dict.suggest(word)
        return suggestions[0]

def sort(scores, N, k):
	return nlargest(k, scores, key=lambda e:e[1])

def get_posting_list(term,index):
    if term in index:
        return index[term]
    return []

def tokenize_normalize(lis):
    stemmer = PorterStemmer();
    tokens = [q.lower() for q in lis if (q.lower() not in stop_words)]
    # normalization - porter stemming
    edited_terms = []
    edited_terms = [stemmer.stem(plural) for plural in tokens]
    j = 0
    while j < len(edited_terms):
        if ((edited_terms[j] != '' and re.findall('[^0-9a-zA-Z*]+', edited_terms[j])) or len(edited_terms[j]) == 1):
            edited_terms.pop(j)
            j -= 1
        j += 1
    return edited_terms

def inverted_index(terms,idx):
        pageid = idx
        # build the index for the current page
        page_dict = {}
        for pos, term in enumerate(terms):
            # print pos,term
            try:
                page_dict[term][1].append(pos)
            except:
                page_dict[term] = [pageid, [pos]]

        # merge the current page index with the main index-dict(hash table internally implemented)
        #print "This loop starts"

        for term_page, posting_list_page in page_dict.iteritems():
            #print term_page
            #print posting_list_page
            # index[term_page].append(posting_list_page)
            try:
                index[term_page][0] += 1  # this is doc freq
                index[term_page][1].append(posting_list_page)
            except:
                index[term_page] = [1, [posting_list_page]]
        return index

#converts the input string into list
def get_list(qString):
    return re.findall('[a-z0-9*]+', qString.lower())

# total keys
def get_vocabLength(index):
    return len(index)

def cosineScore(query, scores,index):
    for t in query:
        pl = get_posting_list(t,index)  # returns an empty list if the term is not in vocab
        if not pl:
            continue
        idf = math.log(float(N / pl[0]), 10)
        wtq = weight(t, query, idf)  # calculate weight of term in query
        for docList in pl[1]:
            tf = 1 + math.log(len(docList[1]), 10)
            wtd = tf * idf
            scores[docList[0]][1] += wtq * wtd

    for d in range(N):
        scores[d][1] /= Length[d]
    return scores

def weight(term, query, invDf):
    freq = 0
    for w in query:
        if w == term:
            freq = freq + 1
    tfq = 1 + math.log(freq, 10)
    return tfq * invDf

def main():

    #step1
    queryString = raw_input("Enter Test query\n")
    stop_words.update(['.',',','"','"',"'",'?','!',':',';','(',')','[',']','{','}','<','>','-'])
    query = get_list(queryString)  # returns query as a LIST (not a string)
    query1 = query	#storing a copy of the query list as given by user

	
	#this is a list of lists where each inner list will have 3 components - docId,score,docName
    scores=[]
    #this is a way of storing doc file names
    for ix, doc1 in enumerate(reuters.fileids()):
        if (ix == N):
            break;
        present_doc = reuters.fileids()[ix][5:]	
        scores.append([ix,0,present_doc])	#initializing score such that docIds and docNames are stored - default score for each doc=0

	#tokenization, normalization and formation of inverted index
    #step 4
    lis=[]; l=[]
    for idx in range(0,N):
        #name of the doc
        present_doc = scores[idx][2]

        #storing contents of the doc in a variable
        with open(present_doc, 'r') as myfile:
            data = myfile.read().replace('\n', ' ')
        lis = get_list(data)
        l = l+lis
        terms = tokenize_normalize(lis)
        index = inverted_index(terms,idx)

    l = list(set(l))

    #print terms
    #print index
	
	#step 5
    #will have all possibility of wildcard query terms
    filtered = [];
    #final query term list
    #print "the list is ", lis
    q = [];
    for i in range(len(query)):
        if '*' in query[i]:
            filtered = fnmatch.filter(l, query[i])
            for j in filtered:
                q.append(j)
        else:
            q.append(query[i])
    
    query = q 	 # storing the final query token list into query
    print "Wildcard query resolved: "
    print query
    #print lis


    #step2
    print "Input 1 for Tokenization and Normalization of the query"
    token_norm_input = raw_input("Enter: ")
    if(token_norm_input == "1"):
        #print "Tokenizing and Normalizing query"
        query = tokenize_normalize(query)
    print query

    #step 3 - Spell correction using enchant
    flag=0; q1=[]
    print "Input 2 for spell correction of query terms"
    spell_correct = raw_input("Enter: ")
    if(spell_correct=="2"):
        for idx,query_term in enumerate(query1):
            if '*' not in query_term:
                replacer = SpellingReplacer()
                suggested_term = (replacer.replace(query_term))
                if suggested_term!=query_term:			#displaying the suggested word if it is different from the user's word
            		print "Actual query term: " + query_term + " Suggested term: " +suggested_term
                	spelling_replace = raw_input("Enter Y for accepting suggestion, N for rejecting: ")
                	if(spelling_replace == "Y"):
						q1.append(suggested_term)
						flag=1		#indicating that at least one token has been changed													
    else:
		print "Spell correct not desired"
	
	#at least one token has become changed by spell correct so normalize the correct query list
    if flag==1:
		query = tokenize_normalize(query+q1)

    M = get_vocabLength(index)

    #step 6
    #Matrix for storing tf-idf weights
    Matrix = [[0 for x in range(N)] for y in range(M)]  # initialise Matrix with 0
    i=0
    for term in index.keys():
        pl = get_posting_list(term,index)
        tf, idf = 0, 0;
        idf = math.log(float(N / pl[0]), 10)
        for docList in pl[1]:
            tFreq = len(docList[1])
            tf = 1 + math.log(tFreq, 10)
            Matrix[i][docList[0]] = tf * idf
        i = i + 1
    
    #step 7
    #L2 Norm for each doc
    for j in range(N):
        s = 0
        for i in range(M):
            s = s + Matrix[i][j] ** 2
        Length[j] = math.sqrt(s)
    #print Length

    #step 8: finding the scores of query-doc
    scores = cosineScore(query,scores,index)

    #k is the value of top k docs to be retrieved
    k = 10

    #step 9: sorting top-k documents
    scores = sort(scores, N, k)

    #step10 - fetching
    print "Input 3 for printing fetched documents"
    fetch_doc = raw_input("Enter: ")
    if (fetch_doc == "3"):
        for i in range(0,k):
            print "Scores: " + str(scores[i][1]), " docid: " + str(scores[i][0]) + " docName: " + scores[i][2]
    else:
        print "fetched documents not desired"

if __name__ == '__main__':
    main()
