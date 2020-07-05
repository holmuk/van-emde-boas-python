import math
import random
import sys

sys.path.append('..')

from van_emde_boas import VEBTree

RANDMIN = 12
RANDMAX = 10000


class TestVEBTree():
    @staticmethod
    def _gen_env():
        usize = random.randint(RANDMIN, RANDMAX)
        k = int(math.ceil(math.log2(usize)))
        t = VEBTree(k)
        return t, usize, k

    def test_veb_tree_singleton_even(self):
        t = VEBTree(4)
        t.insert(1)
        assert repr(t) == '{1, 1, [_, _, _, _]}'
        assert t.find_next(1) == -1
        assert t.universe_size == 16

    def test_veb_tree_singleton_odd(self):
        t = VEBTree(5)
        t.insert(1)
        assert repr(t) == '{1, 1, [_, _, _, _, _, _, _, _]}'
        assert t.find_next(1) == -1
        assert t.universe_size == 32

    def test_veb_tree_singleton_delete(self):
        t, _, k = self._gen_env()
        t.insert(1)
        t.delete(1)
        assert list(t) == []

    def test_veb_tree_insert(self):
        t, usize, k = self._gen_env()
        vals = sorted(random.choices(list(range(usize)), k=usize // 3))  # + repetitions
        t.insert(vals)
        assert vals in t
        assert sorted(list(set(vals))) == list(t)

    def test_veb_tree_successor(self):
        t, usize, k = self._gen_env()
        vals = sorted(random.sample(list(range(usize)), k=usize // 3))
        t.insert(vals)
        for i, x in enumerate(vals[0: -2]):
            assert t.find_next(x) == vals[i + 1]

    def test_veb_tree_predecessor(self):
        t, usize, k = self._gen_env()
        vals = sorted(random.sample(list(range(usize)), k=usize // 3))
        t.insert(vals)
        for i, x in enumerate(vals[1:]):
            assert t.find_prev(x) == vals[i]

    def test_veb_tree_delete(self):
        t, usize, k = self._gen_env()
        universe = list(range(usize))
        vals = sorted(random.sample(universe, k=usize // 3))
        vals_del = sorted(random.sample(universe, k=usize // 6))  # + junk
        t.insert(vals)
        t.delete(vals_del)
        assert list(t) == sorted(list(set(vals) - set(vals_del)))
