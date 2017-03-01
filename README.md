# Search-Engine

Using Vector-Space model to build a simple search engine that will return 10-20 documents pertaining to a query.

The assignment has been implemented on Python making use of the NLTK module. A very basic documnet-retrieval engine has been made which uses vector space model to get the 10 most relevant documents pertaining to a query. Spell corrections have been handled by making use of the Enchant module of Python. Wildcard queries are also handled (use of * in the query term indicates that wildcard expansion is required for that term).

For testing purpose, the Reuters corpus from NLTK Data is used and a very small collection of documents is chosen (~20) for evaluation of the performance metrics (F-measure, MAP and MRR) for 20 queries. 

To-do: make the inverted index persistent with the help of the Pickle module.

