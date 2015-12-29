from pyloom import *

import random
import string

alphabet = string.ascii_letters


def random_string(N):
    return ''.join([random.choice(alphabet) for _ in range(N)])


class TestBloomFilter(object):
    def test_setup(self):
        bf = BloomFilter(1000)
        assert 10 == bf._num_hashes
        assert 14380 == bf._num_bits
        assert 14380 == len(bf._bitarray)

        # and initially all bits are False
        assert 0 == bf._bitarray.count()

        # test again with a different false positive rate
        bf = BloomFilter(1000, error=0.01)
        assert 7 == bf._num_hashes
        assert 9583 == bf._num_bits
        assert 9583 == len(bf._bitarray)

        # and initially all bits are False
        assert 0 == bf._bitarray.count()

    def test_add_contains(self):
        bf = BloomFilter(1000, error=0.01)
        keys1 =  [random_string(10) for _ in range(1000)]
        keys2 =  [random_string(10) for _ in range(1000)]

        for k in keys1:
            bf.add(k)
            assert k in bf
class TestScalableBloomFilter(object):
    def test_scaling(self):
        S, N, E = 1000, 10000, 0.01

        # create a bloom filter with initial capacity of S
        sbf = ScalableBloomFilter(S, E, 2)
        keys1 =  {random_string(10) for _ in range(N)}
        keys2 =  {random_string(10) for _ in range(N)}

        for k in keys1:
            sbf.add(k)
            assert k in sbf

        error = 0
        total = 0
        for k in keys2:
            if k in keys1:
                continue

            total += 1
            if k in sbf:
                error += 1

        error_rate = error / total
        assert error_rate <= 2 * 0.01, 'Error rate is %.3f when it should be %.3f' % (error_rate, E)
