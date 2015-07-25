__doc__ = """

This modules implements a bloom filter which can store arbitrary strings.

Requires:

    mmh3 (https://pypi.python.org/pypi/mmh3/)
    bitarray (https://pypi.python.org/pypi/bitarray/)

"""

from bitarray import bitarray
import math
import mmh3


LOG2 = math.log(2)

def murmur(key, seed=0):
    """Return murmur3 hash of the key as 32 bit signed int."""
    return mmh3.hash(key, seed)


class BloomFilter(object):
    def __init__(self, capacity, error=0.001):
        self.capacity = capacity
        self.error = error
        self._count = 0
        self._setup()

    def _setup(self):
        self._num_bits = int(-self.capacity * math.log(self.error) / (LOG2 * LOG2))
        self._num_hashes = int(LOG2 * (self._num_bits / self.capacity) + 0.5)
        self._bitarray = bitarray(self._num_bits)
        self._bitarray.setall(False)

    def add(self, key):
        if key not in self:
            for b in self._get_hashes(key):
                self._bitarray[b] = True

            self._count += 1

    def __contains__(self, key):
        for b in self._get_hashes(key):
            if self._bitarray[b] is False:
                return False

        return True

    def __len__(self):
        return self._count

    def _get_hashes(self, key):
        h1 = murmur(key, seed=0)
        h2 = murmur(key, h1)

        # doing a modulo now instead of earlier so that h2 could be seeded on a
        # larger space
        h1 = h1 % self._num_bits;
        h2 = h2 % self._num_bits;

        sum_h2 = 0
        for i in range(self._num_hashes):
            h = h1 + sum_h2
            if h >= self._num_bits:
                h -= self._num_bits

            yield h
            sum_h2 += h2
            if sum_h2 >= self._num_bits:
                sum_h2 -= self._num_bits
