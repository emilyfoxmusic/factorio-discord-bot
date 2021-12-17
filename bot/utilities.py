import string
import random


def single(fn, iterable):
    filtered = list(filter(fn, iterable))
    if len(filtered) == 0:
        raise Exception('Item not found')
    if len(filtered) > 1:
        raise Exception('More than one item found')
    return filtered[0]


def random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))
