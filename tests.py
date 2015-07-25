import pyloom
BloomFilter = pyloom.BloomFilter

import random
import string

alphabet = string.ascii_letters


def random_string(N):
    return ''.join([random.choice(alphabet) for _ in range(N)])


class TestBloomFilter(object):
    def test_setup(self):
        bf = BloomFilter(1000)
        assert 10 == bf._num_hashes
        assert 14377 == bf._num_bits
        assert 14377 == len(bf._bitarray)

        # and initially all bits are False
        assert 0 == bf._bitarray.count()

        # test again with a different false positive rate
        bf = BloomFilter(1000, error=0.01)
        assert 7 == bf._num_hashes
        assert 9585 == bf._num_bits
        assert 9585 == len(bf._bitarray)

        # and initially all bits are False
        assert 0 == bf._bitarray.count()

    def test_add_contains(self):
        bf = BloomFilter(1000, error=0.01)
        keys1 =  [random_string(10) for _ in range(1000)]
        keys2 =  [random_string(10) for _ in range(1000)]

        for k in keys1:
            bf.add(k)
            assert k in bf

        error = 0
        total = 0
        for k in keys2:
            if k in keys1:
                continue

            total += 1
            if k in bf:
                error += 1

        error_rate = error / total
        assert error_rate <= 2 * 0.01
