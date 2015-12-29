__doc__ = """

This modules implements a bloom filter which can store arbitrary strings.

Requires:

    mmh3 (https://pypi.python.org/pypi/mmh3/)
    bitarray (https://pypi.python.org/pypi/bitarray/)

"""

from bitarray import bitarray
import math
import mmh3
import time


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
        self._mem_time = 0
        self._mem_access = 0
        self._hash_time = 0
        self._hash_access = 0
        self._hash_init_count = 0
        self._hash_init_time = 0

    def _setup(self):
        num_bits = int(-self.capacity * math.log(self.error) / (LOG2 * LOG2))
        self._num_hashes = int(LOG2 * (num_bits / self.capacity) + 0.5)
        self._bits_per_hash = int(num_bits / self._num_hashes + 0.5)
        self._num_bits = self._bits_per_hash * self._num_hashes
        self._bitarray = bitarray(self._num_bits)
        self._bitarray.setall(False)

    def add(self, key):
        if key not in self:
            for b in self._get_hashes(key):
                start = time.clock()
                self._bitarray[b] = True
                self._mem_time += time.clock() - start
                self._mem_access += 1

            self._count += 1

    def __contains__(self, key):
        for b in self._get_hashes(key):

            start = time.clock()
            found = self._bitarray[b]
            self._mem_time += time.clock() - start
            self._mem_access += 1

            if found is False:
                return False

        return True

    def __len__(self):
        return self._count

    def _get_hashes(self, key):
        start = time.clock()
        h1 = murmur(key, seed=0)
        h2 = murmur(key, h1)

        bph = self._bits_per_hash

        # doing a modulo now instead of earlier so that h2 could be seeded on a
        # larger space
        h1 = h1 % bph;
        h2 = h2 % bph

        self._hash_init_time += time.clock() - start
        self._hash_init_count += 1
        start = time.clock()

        sum_h = h1
        base = 0
        for i in range(self._num_hashes):
            self._hash_time += time.clock() - start
            self._hash_access += 1
            yield base + sum_h
            start = time.clock()

            base += bph
            sum_h += h2
            if sum_h >= bph:
                sum_h -= bph


class ScalableBloomFilter(object):
    def __init__(self, capacity, error=0.001, expansion_rate=2):
        self.capacity = capacity
        self.error = error
        self.expansion_rate = expansion_rate
        self._error_r = 0.9
        self._bfs = [BloomFilter(capacity, error * (1 - self._error_r))]

    def __len__(self):
        return sum(len(bf) for bf in self._bfs)

    def _memory(self):
        return sum(len(bf._bitarray) for bf in self._bfs)

    def add(self, key):
        if key not in self:
            last = self._bfs[-1]
            if len(last) >= last.capacity:
                new_capacity = self.expansion_rate * last.capacity
                new_error = self._error_r * last.error
                last = BloomFilter(new_capacity, new_error)
                self._bfs.append(last)

            last.add(key)

    def __contains__(self, key):
        for bf in reversed(self._bfs):
            if key in bf:
                return True

        return False
