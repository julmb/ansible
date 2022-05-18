# tuples
def fst(t): x, _ = t; return x
def snd(t): _, y = t; return y

# sequences
def single(sequence): [item] = sequence; return item
# TODO: replace this with itertools.pairwise in python 3.10
def pairwise(sequence): return zip(sequence, sequence[1:])
def iterate(get):
	while item := get(): yield item
