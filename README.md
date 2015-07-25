# pyloom
Python Bloom Filter

Usage:

```
import pyloom

# create bloom filter which can store 1000 keys
# can also specify the target error (false positive) rate
bloom = pyloom.BloomFilter(1000, error=0.01)


# add some keys to bloom filter
bloom.add('hello')
bloom.add('world')

# can check if keys are in bloom filter or not
'hello' in bloom
=> True

'world' in bloom
=> True

'random' in bloom
=> False
