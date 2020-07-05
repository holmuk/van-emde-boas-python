import json
import logging
import math

from collections.abc import Iterable


class VEBTree:
    def __init__(self, k: int, verbose=True):
        self.logger = logging.getLogger(__name__)
        if k < 0:
            raise ValueError
        self.universe_size: int = 1 << k
        self.max = -1
        self.min = self.universe_size
        self.k = k
        if k > 1:
            p, q = divmod(k, 2)
            if q:
                half_lg = 0.5 * math.log2(self.universe_size)
                children_k = int(math.floor(half_lg))
                upper_root = math.ceil(half_lg)
            else:
                children_k = p
                upper_root = p
            self.low_root = 1 << children_k
            self.children = [VEBTree(children_k, verbose=False) for _ in range(1 << upper_root)]
            self.aux = VEBTree(upper_root, verbose=False)
        else:
            self.children = []
            self.aux = None
        if verbose:
            self.logger.info('Create a VEB tree with params: {0}'.format(
                json.dumps({
                    'max': self.max,
                    'min': self.min,
                    'M': self.universe_size,
                    'k': k
                })
            ))

    def __contains__(self, item):
        if isinstance(item, Iterable):
            return all(map(self.__contains__, item))

        if item == self.min or item == self.max:
            return True
        if self.k == 1:
            return False
        hi, lo = self._hi_lo(item)
        return lo in self.children[hi]

    def __iter__(self):
        if self.min == self.universe_size:
            raise StopIteration
        curr = self.min
        while (True):
            yield curr
            curr = self.find_next(curr)
            if curr == -1:
                raise StopIteration

    def find_next(self, x):
        if self.k == 1:
            if x == 0 and self.max == 1:
                return 1
        elif x < self.min < self.universe_size:
            return self.min
        else:
            hi, lo = self._hi_lo(x)
            mlow = self.children[hi].max
            if mlow != -1 and lo < mlow:
                off = self.children[hi].find_next(lo)
                return hi * self.low_root + off
            else:
                sucl = self.aux.find_next(hi)
                if sucl != -1:
                    off = self.children[sucl].min
                    return sucl * self.low_root + off
        return -1

    def find_prev(self, x):
        if self.k == 1:
            if x == 1 and self.min == 0:
                return 0
        elif x > self.max > -1:
            return self.max
        else:
            hi, lo = self._hi_lo(x)
            mlow = self.children[hi].min
            if mlow != self.children[hi].universe_size and lo > mlow:
                off = self.children[hi].find_prev(lo)
                return hi * self.low_root + off
            else:
                sucl = self.aux.find_prev(hi)
                if sucl != -1:
                    off = self.children[sucl].max
                    return sucl * self.low_root + off
                else:
                    if self.min < self.universe_size and x > self.min:
                        return self.min
        return -1

    def insert(self, x):
        if isinstance(x, Iterable):
            for elem in x:
                self.insert(elem)
            return

        if self.min == self.universe_size:
            self.min = self.max = x
        else:
            if x < self.min:
                x, self.min = self.min, x
            if self.k > 1:
                hi, lo = self._hi_lo(x)
                if self.children[hi].min == self.children[hi].universe_size:
                    self.aux.insert(hi)
                self.children[hi].insert(lo)
            if x > self.max:
                self.max = x

    def delete(self, x) -> bool:
        if isinstance(x, Iterable):
            return all([self.delete(elem) for elem in x])

        if self.min == self.max == x:
            self.__init__(self.k, verbose=False)
            return True
        elif self.k == 1:
            if 0 <= x < 2:
                self.max = self.min = 1 - x
                return True
        else:
            if x == self.min:
                first_child = self.aux.min
                x = first_child * self.low_root + self.children[first_child].min
                self.min = x
            hi, lo = self._hi_lo(x)
            if self.children[hi].delete(lo):
                if self.children[hi].min == self.children[hi].universe_size:
                    if self.aux.delete(hi):
                        if x == self.max:
                            if self.aux.max == -1:
                                self.max = self.min
                            else:
                                smax = self.children[self.aux.max].max
                                self.max = self.aux.max * self.low_root + smax
                        return True
                elif x == self.max:
                    self.max = hi * self.low_root + self.children[hi].max
                    return True
        return False

    def __repr__(self):
        if self.max < self.min:
            return '_'
        return '{{{min}, {max}, {r}}}'.format(
            min=self.min,
            max=self.max,
            r=self.children.__repr__()
        )

    def _hi_lo(self, x):
        sqm = self.low_root
        return math.floor(x / sqm), x % sqm

