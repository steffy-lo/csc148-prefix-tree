from prefix_tree import SimplePrefixTree
import unittest

################################################################################
# Inserting on empty SimplePrefixTree
################################################################################


def test_insert_n_prefix() -> None:
    value = "CSC148"
    weight = 3
    prefix = ['C', 'S', 'C', '1', '4', '8']

    tree = SimplePrefixTree('sum')
    tree.insert(value, weight, prefix)

    assert tree.weight == 3
    assert tree.subtrees[0].value == ['C']
    assert tree.subtrees[0].subtrees[0].value == ['C', 'S']
    assert tree.subtrees[0].subtrees[0].subtrees[0].value == ['C', 'S', 'C']
    assert tree.__len__() == 1


def test_insert_one_prefix() -> None:
    value = 10
    weight = 1
    prefix = [1]

    tree = SimplePrefixTree('sum')
    tree.insert(value, weight, prefix)

    assert tree.weight == 1
    assert tree.subtrees[0].value == [1]
    assert tree.subtrees[0].weight == 1
    assert tree.subtrees[0].subtrees[0].value == 10
    assert tree.subtrees[0].subtrees[0].subtrees == []
    assert tree.subtrees[0].subtrees[0].weight == 1
    assert tree.__len__() == 1


def test_insert_empty_prefix() -> None:
    value = 5
    weight = 1
    prefix = []

    tree = SimplePrefixTree('sum')
    tree.insert(value, weight, prefix)

    assert tree.weight == 1
    assert tree.value == []
    assert tree.subtrees[0].value == 5
    assert tree.__len__() == 1

################################################################################
# Inserting on non-empty SimplePrefixTree
################################################################################


def test_insert_sum_non_empty() -> None:
    value1 = "CSC148"
    weight1 = 3
    prefix1 = ['C', 'S', 'C', '1', '4', '8']

    tree = SimplePrefixTree('sum')
    tree.insert(value1, weight1, prefix1)

    value2 = "CSC165"
    weight2 = 3
    prefix2 = ['C', 'S', 'C', '1', '6', '5']

    tree.insert(value2, weight2, prefix2)

    assert tree.weight == 6
    assert tree.subtrees[0].weight == 6
    assert tree.subtrees[0].value == ['C']
    assert tree.subtrees[0].subtrees[0].value == ['C', 'S']
    assert tree.subtrees[0].subtrees[0].subtrees[0].value == ['C', 'S', 'C']
    assert tree.subtrees[0].subtrees[0].subtrees[0].subtrees[0].subtrees[0].subtrees[0].value == ['C', 'S', 'C', '1', '4', '8']
    assert tree.subtrees[0].subtrees[0].subtrees[0].subtrees[0].subtrees[1].subtrees[0].value == ['C', 'S', 'C', '1', '6', '5']
    assert tree.subtrees[0].subtrees[0].subtrees[0].subtrees[0].subtrees[0].subtrees[0].weight == 3
    assert tree.subtrees[0].subtrees[0].subtrees[0].subtrees[0].subtrees[1].subtrees[0].weight == 3
    assert tree.__len__() == 2


def test_insert_avg_non_empty() -> None:
    value1 = "CSC148"
    weight1 = 3
    prefix1 = ['C', 'S', 'C', '1', '4', '8']

    tree = SimplePrefixTree('average')
    tree.insert(value1, weight1, prefix1)

    value2 = "CSC165"
    weight2 = 3
    prefix2 = ['C', 'S', 'C', '1', '6', '5']

    tree.insert(value2, weight2, prefix2)

    assert tree.weight == 3.0
    assert tree.subtrees[0].weight == 3.0
    assert tree.subtrees[0].value == ['C']
    assert tree.subtrees[0].subtrees[0].value == ['C', 'S']
    assert tree.subtrees[0].subtrees[0].subtrees[0].value == ['C', 'S', 'C']
    assert tree.subtrees[0].subtrees[0].subtrees[0].subtrees[0].subtrees[0].subtrees[0].value == ['C', 'S', 'C', '1', '4', '8']
    assert tree.subtrees[0].subtrees[0].subtrees[0].subtrees[0].subtrees[1].subtrees[0].value == ['C', 'S', 'C', '1', '6', '5']
    assert tree.subtrees[0].subtrees[0].subtrees[0].subtrees[0].subtrees[0].subtrees[0].weight == 3
    assert tree.subtrees[0].subtrees[0].subtrees[0].subtrees[0].subtrees[1].subtrees[0].weight == 3
    assert tree.__len__() == 2


def test_insert_sum_inserted() -> None:
    value1 = "CSC148"
    weight1 = 3
    prefix1 = ['C', 'S', 'C', '1', '4', '8']

    tree = SimplePrefixTree('sum')
    tree.insert(value1, weight1, prefix1)

    value2 = "CSC148"
    weight2 = 4
    prefix2 = ['C', 'S', 'C', '1', '4', '8']

    tree.insert(value2, weight2, prefix2)
    assert tree.weight == 7
    assert tree.subtrees[0].weight == 7
    assert tree.__len__() == 1

################################################################################
# Unlimited Autocomplete
################################################################################


class MyTest(unittest.TestCase):
    maxDiff = None

    def test_unlimited_autocomplete(self) -> None:
        tree = SimplePrefixTree('sum')

        value1 = "cat"
        weight1 = 3
        prefix1 = ['c', 'a', 't']

        tree.insert(value1, weight1, prefix1)

        value2 = "care"
        weight2 = 2
        prefix2 = ['c', 'a', 'r', 'e']

        tree.insert(value2, weight2, prefix2)

        value3 = "car"
        weight3 = 5
        prefix3 = ['c', 'a', 'r']

        tree.insert(value3, weight3, prefix3)

        value4 = "door"
        weight4 = 1
        prefix4 = ['d', 'o', 'o', 'r']

        tree.insert(value4, weight4, prefix4)

        value5 = "danger"
        weight5 = 4
        prefix5 = ['d', 'a', 'n', 'g', 'e', 'r']

        tree.insert(value5, weight5, prefix5)

        value6 = "cope"
        weight6 = 3
        prefix6 = ['c', 'o', 'p', 'e']

        tree.insert(value6, weight6, prefix6)

        value7 = "cop"
        weight7 = 2
        prefix7 = ['c', 'o', 'p']

        tree.insert(value7, weight7, prefix7)

        assert tree.autocomplete(['c', 'a']) == [('car', 5), ('cat', 3), ('care', 2)]
        assert tree.autocomplete(['c']) == [('car', 5), ('cat', 3), ('cope', 3), ('care', 2), ('cop', 2)]
