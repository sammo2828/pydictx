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

>>> print movies.find({'year': {'$nin': [1978, 2012]}})
set(['Avatar'])

>>> print movies.find({'stars': {'$nin': ['John Hurt', 'Zoe Saldana']}})
set(['Prometheus'])

>>> print movies.find({'$and': [{'stars': 'Sigourney Weaver'}, {'stars': 'Tom Skerritt'}, {'stars': 'John Hurt'}]})
set(['Alien'])

>>> movies.find({'$or': [{'stars': 'Tom Skerritt'}, {'stars': 'Logan Marshall-Green'}]})
set(['Alien', 'Prometheus'])

>>> movies.find({'$nor': [{'stars': 'Tom Skerritt'}, {'stars': 'Logan Marshall-Green'}]})
set(['Avatar'])



"""

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
        self["$nin"] = self._nin
        self["$and"] = self._and
        self["$or"] = self._or
        self["$nor"] = self._nor
        
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
    def _nin(self, left, right):
        return set(self.d.iterkeys()) - self._in(left, right)
    def _and(self, expressions):
        return set.intersection(*[self.d.find(query) for query in expressions])
    def _or(self, expressions):
        return set.union(*[self.d.find(query) for query in expressions])
    def _nor(self, expressions):
        return set(self.d.iterkeys()) - self._or(expressions)

class IndexedList(list):
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        self.parent = None
    def __setitem__(self, i, item):
        if i < len(self):
            self.unindexitem(i)
        if isinstance(item, dict):
            indexed_document = IndexedDict(item)
            indexed_document.set_parent(self.parent, self._id)
            list.__setitem__(self, i, indexed_document)
        elif isinstance(item, list):
            indexed_list = IndexedList(item)
            indexed_list.set_parent(self.parent, self._id)
            list.__setitem__(self, i, indexed_list)
        else:
            list.__setitem__(self, i, item)
            self.parent.update_index([self._id], item)
    def unindexitem(self, i):
        value = self[i]
        if isinstance(value, IndexedDict):
            value.unindex()
        elif isinstance(value, IndexedList):
            value.unindex()
        else:
            self.parent.remove_index([self._id], value)
    def unindex(self):
        for i in xrange(len(self)):
            self.unindexitem(i)
    def set_parent(self, parent, _id):
        self.parent = parent
        self._id = _id
        for i, item in enumerate(self):
            self[i] = item

class IndexedDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.parent = None
    def __setitem__(self, key, value):
        if key in self:
            self.unindexitem(key)
        if isinstance(value, dict):
            indexed_document = IndexedDict(value)
            indexed_document.set_parent(self, key)
            dict.__setitem__(self, key, indexed_document)
        elif isinstance(value, list):
            indexed_list = IndexedList(value)
            indexed_list.set_parent(self, key)
            dict.__setitem__(self, key, indexed_list)
        else:
            dict.__setitem__(self, key, value)
            self.update_index([key], value)
    def unindexitem(self, key):
        value = self[key]
        if isinstance(value, IndexedDict):
            value.unindex()
        elif isinstance(value, IndexedList):
            value.unindex()
        else:
            self.remove_index([key], value)
    def unindex(self):
        for key, value in self.iteritems():
            self.unindexitem(key)
    def set_parent(self, parent, _id):
        self.parent = parent
        self._id = _id
        for key, value in self.iteritems():
            self[key] = value
    def update_index(self, key, value):
        key.append(self._id)
        self.parent.update_index(key, value)
    def remove_index(self, key, value):
        key.append(self._id)
        self.parent.remove_index(key, value)

class dictx(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.operations = Operations(self)
        self.indices = {}
    def insert(self, *args):
        for document in args:
            indexed_document = IndexedDict(document)
            indexed_document.set_parent(self, indexed_document['name']) # in future use gid
            self[indexed_document['name']] = indexed_document
    def update_index(self, key, value):
        _id = ".".join(key[-2::-1])
        try:
            self.indices[_id][value].add(key[-1])
        except KeyError:
            try:
                self.indices[_id][value] = set([key[-1]])
            except KeyError:
                self.indices[_id] = {}
                self.indices[_id][value] = set([key[-1]])
    def remove_index(self, key, value):
        _id = ".".join(key[-2::-1])
        try:
            self.indices[_id][value].remove(key[-1])
            if not self.indices[_id][value]:
                del self.indices[_id][value]
        except:
            pass
        
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
            results = results.intersection(self.operations[lhs](rhs))
        # return results
        return results
        

if __name__ == "__main__":
    
    from pprint import pprint
    # Create a dictionary-like database of movies
    
    movies = dictx()
    movies.insert(
        {
            'name'        : 'Prometheus',
            'blah'        : [{'hello': 1234, 'world': 5678}, "jkajskldf", [1, 2, 3]],
            'year'        : 2012,
            'rating'      : 5,
            'directors'   : ['Ridley Scott'],
            'stars'       : ['Noomi Rapace', 'Logan Marshall-Green',
                             'Michael Fassbender'],
            'description' : 'A team of explorers discover a clue to the ' \
                            'origins of mankind on Earth, leading them on a ' \
                            'journey to the darkest corners of the universe. ' \
                            'There, they must fight a terrifying battle to ' \
                            'save the future of the human race.'
        },
        {
            'name'        : 'Alien',
            'stunts'      : [['Jackie', 'Chan'], ['Arnold', 'Schwarzenegger']],
            'blah'        : [{'hello': 1234}, "jkajskldf", [1, 2, 3], ['a', 'a', 'a', 'a', [38209132, 895032235]]],
            'year'        : 1978,
            'rating'      : 4,
            'directors'   : ['Ridley Scott'],
            'stars'       : ['Sigourney Weaver', 'Tom Skerritt', 'John Hurt'],
            'description' : 'A mining ship, investigating a suspected SOS, ' \
                            'lands on a distant planet. The crew discovers '\
                            'some strange creatures and investigates.'
        },
        {
            'name'        : 'Avatar',
            'year'        : 2009,
            'rating'      : 3,
            'directors'   : 'James Cameron',
            'stars'       : ['Sam Worthington', 'Zoe Saldana',
                             'Sigourney Weaver'],
            'description' : 'A paraplegic Marine dispatched to the moon ' \
                            'Pandora on a unique mission becomes torn between ' \
                            'following his orders and protecting the world he ' \
                            'feels is his home.'
        }
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
        

    import doctest
    doctest.testmod(verbose=2, report=False)

    
    # change dictionary attributes
    pprint(movies['Avatar']['rating'])
    movies['Avatar']['rating'] = 5
    pprint(movies['Avatar']['rating'])
    
    # change list items
    pprint(movies['Avatar']['stars'])
    movies['Avatar']['stars'][2] = "Tom Skerritt"
    pprint(movies['Avatar']['stars'])
    
    
    # change attribute from dict to int
    pprint(movies['Prometheus']['blah'])
    #movies['Prometheus']['blah'] = 1234567890
    pprint(movies['Prometheus']['blah'])
    
    movies.insert({'name': 'fofoofooo', 'blah': 'the quick brown fox jumped over the lazy dog', 'foo': True})
    
    pprint(movies.indices)
    

