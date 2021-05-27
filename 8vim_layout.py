#!/usr/bin/env python

import enum
import itertools
import time

# Read in bigram frequencies.
BigramFrequencies = {}
BigramTupleFrequencies = {}
TotalBigramFrequency = 0
with open('bigram_dictionaries/english_bigrams_1.txt', 'r') as bbl:
    for line in bbl:
        bigram, freq = line.lower().split()
        freq = int(freq)
        BigramFrequencies[bigram] = freq
        TotalBigramFrequency += freq
# Normalize frequencies.
for bigram in BigramFrequencies.keys():
    BigramFrequencies[bigram] /= TotalBigramFrequency
    # use tuple encoding of bigram as alternate key
    BigramTupleFrequencies[tuple(bigram)] = BigramFrequencies[bigram]

class Sector(enum.Enum):
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3
    CENTER = 4

    def clockwise(self, amount=1):
        return self.turn(amount)
    def counterClockwise(self, amount=1):
        return self.turn(-amount)
    def turn(self, direction):
        if self == Sector.CENTER:
            return self
        else:
            return Sector((self.value + direction) % 4)

    def turnSeq(start, travel):
        if travel < 0:
            steps = range(-1, travel-1, -1)
        else:
            steps = range(+1, travel+1, +1)
        return [Sector.CENTER, start] + [start.turn(step) for step in steps] + [Sector.CENTER]


def unigramCost(sectorSequence):
    return len(sectorSequence) - 1
# This is a very simplistic cost function for bigrams.
def bigramCost(seq1, seq2):
    cost = unigramCost(seq1) + unigramCost(seq2)
    # Add penalty if seq2 makes us reverse course on the last step of seq1
    if seq1[-2] == seq2[1]:
        cost += 2
    return cost

# A layout is a mapping of { letter -> [list of Sector] }
#
# Convert from a string listing the letters in order of
# SW(clockwise,anticlock),NW,NE,SE.
LayoutStringListingOrder = list(
    map(Sector.turnSeq,
        [Sector.BOTTOM,
         Sector.LEFT, Sector.LEFT,
         Sector.TOP, Sector.TOP,
         Sector.RIGHT, Sector.RIGHT,
         Sector.BOTTOM] * 4,
        itertools.chain(*[[layer,-layer]*4 for layer in [1,2,3,4]])))

# This could be useful for optimizing cost calculation for many layouts at a time.
MovementBigrams = (itertools.product(LayoutStringListingOrder, repeat=2))
MovementBigramCosts = list(itertools.starmap(bigramCost, MovementBigrams))

def layoutFromString(layoutString):
    layout = {}
    for letter,sectors in zip(layoutString, LayoutStringListingOrder):
        layout[letter] = sectors
    return layout

def calcLayoutCost(layout):
    cost = 0
    for bigram,freq in BigramFrequencies.items():
        cost += freq * bigramCost(layout[bigram[0]], layout[bigram[1]])
    return cost

def calcLayoutCost2(layoutString):
    cost = 0
    for layoutBigram,bigramCost in zip(itertools.product(layoutString, repeat=2), MovementBigramCosts):
        if '-' not in layoutBigram:
            cost += BigramTupleFrequencies[layoutBigram] * bigramCost
    return cost

customLayouts = {
    'Old / original 8VIM layout'               : 'eitsyanolhcdbrmukjzgpxfv----q--w',
    'English layout by sslater11'              : 'hitanerolfydmcsujwkgpxbv----q--z',
    'English layout by kjoetom'                : 'oilseatncpdhrmfubjgvxwky----q-z-',
    'English layout 2 by kjoetom'              : 'enotiraspugdlhcmfjkbywxvz-q-----',
    'English layout 3 by kjoetom'              : 'aoierntlgfcmhsudzyvpjbwkq------x',
    'English layout 4 by kjoetom'              : 'ieaorntsubdhmcflvqypwgkj-x---z--',
    'Best English layout found by this script' : 'eotrnsaidfcugmlhxvjykpwbq-z-----'
}

for layoutName,layoutString in customLayouts.items():
    cost = calcLayoutCost(layoutFromString(layoutString))
    cost2 = calcLayoutCost2(layoutString)
    print("%s cost = %-4.3f [[%-4.3f]] {%s}" % (layoutString, cost, cost2, layoutName))

minCost = 9999
minCostLayoutPerm = None
start_time = time.time()
permutations = 10000
for layoutString in itertools.islice(itertools.permutations('eitsyanolhcdbrmukjzgpxfv----q--w'),permutations):
    # layout = layoutFromString(layoutString)
    # cost = calcLayoutCost(layout)
    ## optimized version
    cost = calcLayoutCost2(layoutString)
    if cost < minCost:
        print("%s cost = %-4.3f {newmin}" % (''.join(layoutString), cost))
        minCost = cost
        minCostLayoutPerm = layoutString
end_time = time.time()
print("checked %d layouts in %.5f seconds" % (permutations, (end_time - start_time)))
print("%s cost = %-4.3f" % (''.join(minCostLayoutPerm), minCost))

# Some debug stuff
if False:
    origLayoutString = customLayouts['Old / original 8VIM layout']
    origLayout = layoutFromString(origLayoutString)

    print( "z: %s" % origLayout['z'] )
    print( "a: %s" % origLayout['a'] )
    print( "o: %s" % origLayout['o'] )
    print( "n: %s" % origLayout['n'] )

    print( "cost(o) = %d" % unigramCost(origLayout['o']))
    print( "cost(n) = %d" % unigramCost(origLayout['n']))
    print( "cost(a) = %d" % unigramCost(origLayout['a']))
    print( "cost(k) = %d" % unigramCost(origLayout['k']))
    print( "cost(w) = %d" % unigramCost(origLayout['w']))
    print( "cost(on) = %d" % bigramCost(origLayout['o'], origLayout['n']))
    print( "cost(an) = %d" % bigramCost(origLayout['a'], origLayout['n']))
    print( "cost(oh) = %d" % bigramCost(origLayout['o'], origLayout['h']))
    print( "cost(ok) = %d" % bigramCost(origLayout['o'], origLayout['k']))
    print( "cost(ow) = %d" % bigramCost(origLayout['o'], origLayout['w']))
    print( "cost(ww) = %d" % bigramCost(origLayout['w'], origLayout['w']))
    print( "cost(kk) = %d" % bigramCost(origLayout['k'], origLayout['k']))

    print("th freq: %g" % BigramFrequencies['th'])
