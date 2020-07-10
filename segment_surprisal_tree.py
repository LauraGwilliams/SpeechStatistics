# Author: Tal Linzen & Laura Gwilliams
# License: BSD (3-clause)import csv

import csv
import paths
from prefix_tree import PrefixTree
from cmu_ipa import ELP2CMU


class SegmentSurprisalTree(object):

    frequency_field = 'SUBTLWF'

    def __init__(self):
        self.elp2cmu = ELP2CMU()

    def read_elp(self):
        self.tree = PrefixTree()
        self.pronunciations = {}

        words = list(csv.DictReader(open(paths.elp)))
        for i, x in enumerate(words):
            pron = self.elp2cmu.translate(x['Pron'])
            if x[self.frequency_field] not in ['0', 'NULL']:
                self.tree.insert(tuple(pron + ['#']),
                        float(x[self.frequency_field]), x['Word'])

            self.pronunciations[x['Word']] = pron

        self.tree.calculate_probs()

    def surprisals(self, word, with_end=True):
        pron = self.pronunciations[word]
        pron = tuple(pron + ['#'] if with_end else [])
        return self.tree.prefix_surprisals(pron)

    def entropies(self, word, with_end=True):
        pron = self.pronunciations[word]
        pron = tuple(pron + ['#'] if with_end else [])
        return self.tree.prefix_entropies(pron)

    def probabilities(self, word, with_end=True):
        pron = self.pronunciations[word]
        pron = tuple(pron + ['#'] if with_end else [])
        return self.tree.prefix_probabilities(pron)

    def frequencies(self, word, with_end=True):
        pron = self.pronunciations[word]
        pron = tuple(pron + ['#'] if with_end else [])
        return self.tree.prefix_frequencies(pron)

    def node_frequencies(self, word, with_end=True):
        pron = self.pronunciations[word]
        pron = tuple(pron + ['#'] if with_end else [])
        return self.tree.prefix_frequencies(pron)

    def get_word_continuations(self, word):

        # get pronunciation of the word
        try:
            word_pron = self.pronunciations[word]
        except:
            raise NotImplementedError("Word '%s' not found in corpus." % word)

        # convert into expected tuple format
        word_tuple = tuple(word_pron + ['#'] if True else [])

        # extract prefix frequency for target word
        continuation_dict = {}  # empty dict to populate w/ frequencies
        phoneme_count = 0
        for phoneme_iter, prefix in self.tree.get_prefixes(word_tuple):

            # get frequency of all phoneme continuations
            cont_freqs = [x[1] for x in self.tree.get_continuations(prefix)]

            # add to dictionary
            continuation_dict.update({'%s_%s' % (phoneme_count, phoneme_iter): cont_freqs })

            # update phoneme count
            phoneme_count = phoneme_count + 1

        return continuation_dict

    def get_uniqueness_point(self, word):

        # get word continuation dict
        continuation_dict = self.get_word_continuations(word)

        # sort key entries
        phoneme_list = continuation_dict.keys()
        phoneme_list.sort()

        # loop through each phoneme entry
        for n, phoneme in enumerate(phoneme_list):
            conts = continuation_dict[phoneme]

            # when there is only one continuation, we have found the UP.
            if len(conts) == 1:
                return n, phoneme

        # if no UP found, return error.
        raise ValueError("No uniqueness point found.")
