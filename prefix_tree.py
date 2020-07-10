# Author: Tal Linzen <linzen@nyu.edu>
# License: BSD (3-clause)

import sys
import numpy as np
import xml.etree.ElementTree as ET

class PrefixTree(object):
    '''
    Stores the frequency of a set of sequences in a tree in which the 
    nodes represent prefixes. All sequences that are stored under a given 
    node start with the prefix that is associated with that node. Similar
    idea to a trie, but the keys aren't necessarily strings. The sequences
    must be hashable (e.g. strings or tuples of immutable data). Example:

    >>> p = PrefixTree()
    >>> p.insert('124', 3)   # '124' has a frequency of 3
    >>> p.insert('125', 3)
    >>> p.pprint()
        Representation        Labels       Frequency   Probability
            1                                    6         1.0
              12                                 6         1.0
                 124                             3         0.5
                 125                             3         0.5

    "Probability" represents the conditional probability of the last
    element of the prefix given the previous ones, and "Frequency" is
    the frequency of the prefix (total frequency of sequences that
    start with it).
    
    Each (terminal) sequence may also have a more compact label; for 
    example:

    >>> p = PrefixTree()
    >>> p.insert(('K', 'IH', 'L'), 3, 'kill')
    >>> p.insert(('K', 'AE', 'T'), 6, 'cat')
    >>> p.pprint()
        Representation        Labels       Frequency   Probability
        ('K',)                                   9         1.0
          ('K', 'AE')                            6      0.6667
            ('K', 'AE', 'T')  cat                6         1.0
          ('K', 'IH')                            3      0.3333
            ('K', 'IH', 'L')  kill               3         1.0
    '''

    # Field widths for pretty printing
    labelwidth = 25
    keywidth = 40

    def __init__(self):
        self.tree = {'id': (), 'labels': ['root'], 'freq': 0,
                'children': {}}
        self._cache = {}
    
    def key_repr(self, key):
        'Stub to be overridden when subclassed'
        return str(key)

    def insert(self, vector, freq, label=''):
        self.tree['freq'] += freq
        pointer = self.tree['children']
        for i in range(len(vector)):
            node = pointer.setdefault(vector[:i+1], 
                    {'id': vector[:i+1], 'labels': [], 'freq': 0,
                        'children': {}})
            node['freq'] = node['freq'] + freq
            pointer = node['children']
        node['labels'].append(label)

    def pprint(self, nodes=None, file_handle=sys.stdout):
        self.calculate_probs()
        if nodes is None:
            nodes = [self.tree]

        if file_handle is None:
            filename = '/tmp/prefix_probs.txt'
            file_handle = open(filename, 'w')

        s = '{0:{keywidth}} {1:{labelwidth}} {2} {3}\n'
        file_handle.write(s.format(
            'Representation', 'Labels', 'Frequency', 'Probability', 
            keywidth=self.keywidth, labelwidth=self.labelwidth))

        for node in nodes:
            self._pprint_node(node['children'], file_handle)
            file_handle.write('\n')

    def _pprint_node(self, node, file_handle):
        if node != {}:
            for key, value in sorted(node.items()):
                key_trans = '%s%s' % (
                        ' ' * (len(key) - 1) * 2, self.key_repr(key))
                labels = ', '.join(value['labels'])
                s = '{0:{keywidth}} {1:{labelwidth}} {2:9} {3:11.4}\n'
                file_handle.write(s.format(
                    key_trans, labels, value['freq'], value['prob'],
                    keywidth=self.keywidth, labelwidth=self.labelwidth))
                self._pprint_node(value['children'], file_handle)

    def get_node(self, vector):
        pointer = self.tree
        for i in range(len(vector)):
            pointer = pointer['children'][vector[:i+1]]
        return pointer

    def get_prefixes(self, vector):
        prefixes = []
        pointer = self.tree
        for i in range(len(vector)):
            pointer = pointer['children'][vector[:i+1]]
            prefixes.append((vector[i], pointer))
        return prefixes

    def calculate_probs(self, node=None):
        '''
        Needs to be manually called to calculate conditional probabilities;
        means that the field can get out of sync. Probably worth making
        this automatic (triggered by every insert).
        '''
        if node is None:
            node = self.tree
        for child in node['children'].values():
            child['prob'] = float(child['freq']) / node['freq']
            self.calculate_probs(child)
            
    def phoneme_string_freq(self, node=None):
        """gets the frequency of a phoneme string"""
        
        if node is None:
            node = self.tree
        for child in node['children'].values():
            child['freq'] = float(child['freq'])
            self.phoneme_string_freq(child)   

    def string_freq(self, node=None):
        """gets the frequency of a phoneme string"""
        
        if node is None:
            node = self.tree
        for child in node['freq']:
            self.phoneme_string_freq(child) 

    def get_continuations(self, node):
        if node['children'] == {}:
            return [(node['labels'], node['freq'])]
        else:
            return sum((self.get_continuations(x) 
                for x in node['children'].values()), [])
            
    def _entropy(self, v):
        'Expects frequencies rather than probabilities'
        v = np.array(v, float)
        v = v + 1    # smoothing
        v = v / np.sum(v)
        return -np.sum(v * np.log2(v))

    def get_node_stats(self, node):
        if node['id'] not in self._cache:
            cont_freqs = [x[1] for x in self.get_continuations(node)]
            self._cache[node['id']] = {
                    'n': len(cont_freqs), 
                    'entropy': self._entropy(cont_freqs)}
        return self._cache[node['id']]

    def iterate_by_depth(self, node, depth, only_terminal=False):
        if depth == 0 and (not only_terminal or node['children'] == {}):
            yield node
        else:
            for child in node['children'].values():
                for y in self.iterate_by_depth(
                        child, depth - 1, only_terminal):
                    yield y

    def prefix_surprisals(self, vector):
        return [(x, -np.log2(y['prob'])) for x, y in 
                self.get_prefixes(vector)]

    def prefix_entropies(self, vector):
        return [(x, self.get_node_stats(y)['entropy']) 
                for x, y in self.get_prefixes(vector)]
                
    def prefix_probabilities(self, vector):
        return [(x, y['prob']) for x, y in 
                self.get_prefixes(vector)]

    def prefix_frequencies(self, vector):
        return [(x, y['freq']) for x, y in 
                self.get_prefixes(vector)]
