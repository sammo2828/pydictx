#!/usr/bin/env python
#Copyright (C) Samson Lee. All rights reserved.

"""Python dictionary with built-in indexing and advanced querying"""

from pprint import pprint

class Operations(dict):
    def __init__(self):
    	self["$gt"] = self.gt
		self["$lt"] = self.lt
		
	def gt(self, field, operand):
		if field > operand:
			return True
		else:
			return False
	def lt(self, field, operand):
		if field < operand:
			return True
		else:
			return False

class dixt(dict):
	operations = Operations()
	def __init__(self, *args, **kwargs):
		dict.__init__(self, *args, **kwargs)
		self.indices = {}
		
	def create_index(self, childkey):
		self.indices[childkey] = index = {}
		for key, value in self.iteritems():
			if childkey in value:
				# index each element of items that are list-like
				if not isinstance(value[childkey], str):
					try:
						for item in value[childkey]:
							try:
								index[item].add(key)
							except KeyError:
								index[item] = set([key])
					except TypeError:
						# not iterable
						try:
							index[value[childkey]].add(key)
						except KeyError:
							index[value[childkey]] = set([key])
	
	def find(self, query):
		"""Find using query dict
		>>> for movie in movies.find({'year': {'$gt': 1970, '$lt': 2010}, 'stars': 'Sigourney Weaver'}):
		        print movie
		"""
		complex_queries = []
		simple_queries = []
		
		# separate simple and complex queries for performance reasons
		for childkey, conditions in query.iteritems():
			if isinstance(conditions, dict):
				complex_queries.append((childkey, conditions))
			else:
				simple_queries.append((childkey, conditions))
		
		# filter simple queries
		if simple_queries:
			results = set.intersection(*[self.indices[childkey][conditions] for childkey, conditions in simple_queries])
		else:
			results = self.iterkeys()
		
		# filter complex queries
		for result in results:
			outcome = True
			for childkey, conditions in complex_queries:
				print result, childkey, conditions
				for operator, operand in conditions.iteritems():
					if not self.operations[operator](self[result][childkey], operand):
						outcome = False
						break
				if not outcome:
					break
		# yield results
			if outcome:
				yield result
			

# Create a dictionary-like database of movies

movies = dixt(
    Prometheus=
        dixt(
        	year        = 2012,
        	rating      = 5,
            directors   = ['Ridley Scott'],
            stars       = ['Noomi Rapace', 'Logan Marshall-Green',
                           'Michael Fassbender'],
            description = 'A team of explorers discover a clue to the ' \
                          'origins of mankind on Earth, leading them on a ' \
                          'journey to the darkest corners of the universe. ' \
                          'There, they must fight a terrifying battle to ' \
                          'save the future of the human race.'
        ),
     Alien=
     	dixt(
     		year        = 1978,
        	rating      = 4,
     		directors   = ['Ridley Scott'],
     		stars       = ['Sigourney Weaver', 'Tom Skerritt', 'John Hurt'],
     		description = 'A mining ship, investigating a suspected SOS, ' \
     		              'lands on a distant planet. The crew discovers '\
     		              'some strange creatures and investigates.'
     	),
     Avatar=
     	dixt(
     		year        = 2009,
        	rating      = 3,
     		directors   = 'James Cameron',
     		stars       = ['Sam Worthington', 'Zoe Saldana',
     		               'Sigourney Weaver'],
     		description = 'A paraplegic Marine dispatched to the moon ' \
     		              'Pandora on a unique mission becomes torn between ' \
     		              'following his orders and protecting the world he ' \
     		              'feels is his home.'
     	)
)

# What are some queries/filters that might be useful?

## Find by exact name:
#print ("Prometheus", movies["Prometheus"])
#print ("Alien", movies["Alien"])

## Find by partial name:
#print [movies[movie] for movie in movies if movie.find("Prom")]
#print [movies[movie] for movie in movies if movie.find("Al")]

## Find by year:
#print [(movie, data) for movie, data in movies.items() if data["year"] == 2012]
#print [(movie, data) for movie, data in movies.items() if data["year"] > 1980]

## Find by actor:
#print [(movie, data) for movie, data in movies.items() if "Sigourney Weaver" in data["stars"]]
#print [(movie, data) for movie, data in movies.items() if [star for star in data["stars"] if star.find(" W")]]

movies.create_index("year")
movies.create_index("rating")
movies.create_index("stars")
movies.create_index("directors")
#pprint(movies.indices)

#for movie in movies.find({'year': {'$gt': 1970, '$lt': 2010}}):
#	print movie

#for movie in movies.find({'year': 1978}):
#	print movie


#for movie in movies.find({'stars': 'Sigourney Weaver'}):
#	pprint(movie)

for movie in movies.find({'stars': 'Sigourney Weaver', 'year': 2009}):
	pprint(movie)

#for movie in movies.find({'year': {'$gt': 1970, '$lt': 2010}}):
#	print movie

#for movie in movies.find({'year': {'$gt': 1970, '$lt': 2010}, 'rating': {'$gt': 2, '$lt': 5}}):
#	print movie
