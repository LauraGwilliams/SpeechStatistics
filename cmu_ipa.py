# Author: Tal Linzen <linzen@nyu.edu>
# License: BSD (3-clause)

import csv
import os

from nltk.corpus import cmudict
import paths

def get_elp_dict():
    elp_dict = {x['Word']: x['Pron'] for x in 
            csv.DictReader(open(paths.elp))}
    return elp_dict

class ELP2CMU(object):
    single = {'S': 'SH', 'O': 'AO', 'I': 'AH', 'U': 'UH', 'h': 'HH',
            'V': 'AH', 'j': 'Y', 'o': 'OW', '4': 'D', 'T': 'TH',
            'Z': 'ZH',
            'u': 'UW', 'E': 'EH', 'i': 'IY', 'D': 'DH', 'A': 'AA',
            'I': 'IH', 'N': 'NG', 'a': 'AE', 'e': 'EY', '@': 'AH'}
    double = {'hw': 'W', 'OI': 'OY', 'aI': 'AY', 'dZ': 'JH',
            'aU': 'AW', '3`': 'ER', 'tS': 'CH', '@`': 'ER'}

    def translate(self, s):
        nostress = s.replace('"', '')
        
        res = []
        i = 0
        while i < len(s):
            if s[i] in '."%':
                i = i + 1
            elif len(s) > i + 1 and s[i:i+2] in self.double:
                res.append(self.double[s[i:i+2]])
                i = i + 2
            elif len(s) > i + 1 and s[i+1] == '=':
                res.append('AH')
                res.append(s[i].upper())
                i = i + 2
            elif s[i] in self.single:
                res.append(self.single[s[i]])
                i = i + 1
            elif s[i] == 'r' and len(res) > 0 and res[-1] == 'ER':
                i = i + 1
            else:
                res.append(s[i].upper())
                i = i + 1

        return res

    def test(self):
        self.cmu = cmudict.dict()
        self.elp = get_elp_dict()
        res = []
        for word, pron in self.elp.items():
            translated = self.translate(pron)
            cmu = self.cmu.get(word)
            if cmu is not None:
                cmu = [x[:2] for x in cmu[0]]
                if (len(translated) != len(cmu) or
                        any(x != y for x, y in zip(translated, cmu))):
                    res.append((word, pron, translated, cmu))
        return res

    def write_test_to_file(self):
        test = self.test()
        f = open('/tmp/test.txt', 'w')
        for r in sorted(test):
            f.write('%s: %s\n%s\n%s\n\n' % r)
