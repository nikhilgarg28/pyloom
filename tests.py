from pyloom import *

import random
import string
import time

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
        N, E = 10000, 0.0001
        bf = BloomFilter(N, error=E)
        keys1 =  {random_string(50) for _ in range(N)}
        keys2 =  {random_string(50) for _ in range(10*N)}

        add_duration = 0
        hit_duration = 0
        miss_duration = 0
        for k in keys1:
            start = time.clock()
            bf.add(k)
            add_duration += time.clock() - start
            start = time.clock()
            assert k in bf
            hit_duration += time.clock() - start

        error = 0
        total = 0
        for k in keys2:
            if k in keys1:
                continue

            total += 1
            start = time.clock()
            found = k in bf
            miss_duration += time.clock() - start
            if found:
                error += 1

        error_rate = error / total
        assert error_rate <= 2 * E, 'Error rate is %.7f when it should be %.7f' % (error_rate, E)

        print('Time per add:', 10**6 * add_duration / len(keys1))
        print('Time per hit:', 10**6 * hit_duration / len(keys1))
        print('Time per miss:', 10**6 * miss_duration / total)
        print('Time per mem access:', 10**6 * bf._mem_time / bf._mem_access)
        print('Time per hash computation:', 10**6 * bf._hash_time /
                bf._hash_access)
        print('Time per hash init:', 10**6 * bf._hash_init_time /
                bf._hash_init_count)
        count = 2 * len(keys1) + total
        print('Total time in mem :', 10**6 * bf._mem_time / count)
        print('Total time in hash :', 10**6 * bf._hash_time / count)
        print('Total time in hash init:', 10**6 * bf._hash_init_time / count)


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
