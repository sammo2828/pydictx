#!/usr/bin/env python
#Copyright (C) Samson Lee. All rights reserved.

"""Python dictionary with built-in indexing and advanced querying

>>> movies.find({})
set(['Alien', 'Prometheus', 'Avatar'])

>>> movies.find({'year': 1978})
set(['Alien'])

>>> movies.find({'stars': 'Sigourney Weaver'})
set(['Alien', 'Avatar'])

>>> movies.find({'stars': 'Sigourney Weaver', 'year': 2009})
set(['Avatar'])

>>> movies.find({'year': {'$lt': 2010}})
set(['Alien', 'Avatar'])

>>> movies.find({'year': {'$gt': 1980, '$lt': 2010}})
set(['Avatar'])

#>>> movies.find({'year': {'$gt': 1970, '$lt': 2010}, 'rating': {'$gt': 2, '$lt': 5}})
#set(['Alien', 'Avatar'])

>>> movies.find({'$or': [{'stars': 'Tom Skerritt'}, {'stars': 'Logan Marshall-Green'}]})
set(['Alien', 'Prometheus'])

>>> movies.find({'stars': {'$all': ['Sigourney Weaver', 'Tom Skerritt']}})
set(['Alien'])

>>> movies.find({'stars': {'$in': ['Sigourney Weaver', 'Tom Skerritt', 'Sam Worthington']}})
set(['Alien', 'Avatar'])

>>> movies.find({'directors': {'$exists': True}})
set(['Alien', 'Prometheus', 'Avatar'])

>>> movies.find({'directors': {'$ne': 'Ridley Scott'}})
set(['Avatar'])

>>> print movies.find({'stars': {'$ne': 'Sigourney Weaver'}})
set(['Prometheus'])

"""

from pprint import pprint

class Operations(dict):
    def __init__(self, d):
        self.d = d
        self["$gt"] = self._gt
        self["$lt"] = self._lt
        self["$gte"] = self._gte
        self["$lte"] = self._lte
        self["$all"] = self._all
        self["$in"] = self._in
        self["$exists"] = self._exists
        self["$ne"] = self._ne
    def _gt(self, left, right):
        return set.union(*[value for key, value in self.d.indices[left].iteritems() if key > right])
    def _lt(self, left, right):
        return set.union(*[value for key, value in self.d.indices[left].iteritems() if key < right])
    def _gte(self, left, right):
        return set.union(*[value for key, value in self.d.indices[left].iteritems() if key >= right])
    def _lte(self, left, right):
        return set.union(*[value for key, value in self.d.indices[left].iteritems() if key <= right])
    def _all(self, left, right):
        return set.intersection(*[self.d.indices[left][key] for key in right])
    def _in(self, left, right):
        return set.union(*[self.d.indices[left][key] for key in right])
    def _exists(self, left, right):
        return set.union(*[value for value in self.d.indices[left].itervalues()])
    def _ne(self, left, right):
        return set(self.d.iterkeys()) - self.d.indices[left][right]

class dictx(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.operations = Operations(self)
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
                else:
                    try:
                        index[value[childkey]].add(key)
                    except KeyError:
                        index[value[childkey]] = set([key])
    def find(self, query):
        """Find using query dict
        #>>> print movies.find({'year': {'$gt': 1970, '$lt': 2010}, 'stars': 'Sigourney Weaver'}):
        """
        # query object format: blah.find({lhs1: rhs1, lhs2: rhs2, etc.})
        # lhs can be attribute name, e.g. 'year'
        #     followed by rhs dict or simple type
        # lhs can also be boolean operators, e.g. '$or' '$and'
        #     followed by rhs list of query objects [{lhs1: rhs1}, {lhs1:
        #     rhs2}]
        if not query:
            return set(self.keys())
        sub_queries = []
        advanced_queries = []
        direct_queries = []
        # separate simple and complex queries for performance reasons
        for lhs, rhs in query.iteritems():
            if isinstance(rhs, list):
                sub_queries.append((lhs, rhs))
            elif isinstance(rhs, dict):
                advanced_queries.append((lhs, rhs))
            else:
                direct_queries.append((lhs, rhs))
        # filter simple queries
        if direct_queries:
            results = set.intersection(*[self.indices[lhs][rhs] for lhs, rhs in direct_queries])
        else:
            results = set(self.keys())
        # filter advanced queries
        for lhs, rhs in advanced_queries:
            results = results.intersection(*[self.operations[operator](lhs, operand) for operator, operand in rhs.iteritems()])
        # filter sub queries
        for lhs, rhs in sub_queries:
            if lhs == "$and":
                sub_results = set.intersection(*[self.find(query) for query in rhs])
            elif lhs == "$or":
                sub_results = set.union(*[self.find(query) for query in rhs])
            else:
                raise Exception("bad condition. must be $and or $or")
            results = results.intersection(sub_results)
        # return results
        return results

if __name__ == "__main__":
    
    # Create a dictionary-like database of movies
    
    movies = dictx(
        Prometheus=
            dictx(
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
            dictx(
                    year        = 1978,
                    rating      = 4,
                    directors   = ['Ridley Scott'],
                    stars       = ['Sigourney Weaver', 'Tom Skerritt', 'John Hurt'],
                    description = 'A mining ship, investigating a suspected SOS, ' \
                                  'lands on a distant planet. The crew discovers '\
                                  'some strange creatures and investigates.'
            ),
         Avatar=
            dictx(
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
    movies.create_index("year")
    movies.create_index("rating")
    movies.create_index("stars")
    movies.create_index("directors")
    #pprint(movies.indices)

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
        

    import doctest
    doctest.testmod(verbose=2, report=False)
