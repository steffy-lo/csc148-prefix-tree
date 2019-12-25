"""CSC148 Assignment 2: Autocompleter classes

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===
This file contains the design of a public interface (Autocompleter) and two
implementation of this interface, SimplePrefixTree and CompressedPrefixTree.
You'll complete both of these subclasses over the course of this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
from typing import Any, List, Optional, Tuple


################################################################################
# The Autocompleter ADT
################################################################################
class Autocompleter:
    """An abstract class representing the Autocompleter Abstract Data Type.
    """
    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        raise NotImplementedError

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        raise NotImplementedError

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        raise NotImplementedError

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        raise NotImplementedError


################################################################################
# SimplePrefixTree (Tasks 1-3)
################################################################################
class SimplePrefixTree(Autocompleter):
    """A simple prefix tree.

    This class follows the implementation described on the assignment handout.
    Note that we've made the attributes public because we will be accessing them
    directly for testing purposes.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - ("prefixes grow by 1")
      If len(self.subtrees) > 0, and subtree in self.subtrees, and subtree
      is non-empty and not a leaf, then

          subtree.value == self.value + [x], for some element x

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Any
    weight: float
    subtrees: List[SimplePrefixTree]

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty simple prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        self.value = []
        self.subtrees = []
        self.weight = 0.0
        self.weight_type = weight_type

    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return self.weight == 0.0

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return self.weight > 0 and self.subtrees == []

    def __str__(self) -> str:
        """Return a string representation of this tree.

        You may find this method helpful for debugging.
        """
        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.value} ({self.weight})\n'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s

    def __len__(self) -> int:
        """Return the number of values stored in this simple prefix tree.
        """
        if self.is_empty():
            return 0
        elif self.is_leaf():
            return 1
        else:
            length = 0
            for subtree in self.subtrees:
                length += subtree.__len__()
            return length

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.
        >>> tree = SimplePrefixTree('average')
        >>> tree.insert('cat', 3, ['c', 'a', 't'])
        >>> tree.insert('care', 2, ['c', 'a', 'r', 'e'])
        >>> tree.insert('car', 5, ['c', 'a', 'r'])
        >>> tree.insert('door', 1, ['d', 'o', 'o', 'r'])
        >>> tree.insert('danger', 4, ['d', 'a', 'n', 'g', 'e', 'r'])
        >>> tree.insert('cope', 3, ['c', 'o', 'p', 'e'])
        >>> tree.insert('cop', 2, ['c', 'o', 'p'])
        >>> tree.insert('cop', 2, ['c', 'o', 'p'])
        >>> print(tree._str_indented())
        """
        if self.value == prefix:
            for sub in self.subtrees:
                if sub.value == value:
                    sub.weight += weight
                    self._update_weight()
                    return
            new_node = SimplePrefixTree(self.weight_type)
            new_node.value = value
            new_node.weight = weight
            self._insert_helper(weight, new_node)
            self._update_weight()
        else:
            for sub in self.subtrees:
                if sub.value == prefix[:len(sub.value)]:
                    sub.insert(value, weight, prefix)
                    self._update_weight()
                    self.subtrees.remove(sub)
                    self._insert_helper(sub.weight, sub)
                    return
            new_node = SimplePrefixTree(self.weight_type)
            new_node.weight = weight
            new_node.value = prefix[:len(self.value) + 1]
            self._insert_helper(weight, new_node)
            new_node.insert(value, weight, prefix)
            self._update_weight()

    def _insert_helper(self, weight: float, new_node: SimplePrefixTree)->None:
        for i, subtree in enumerate(self.subtrees):
            if subtree.weight <= weight:
                self.subtrees.insert(i, new_node)
                return
        self.subtrees.append(new_node)

    def _update_weight(self)->None:
        num, weight = self._get_weight()
        if self.weight_type == "sum":
            self.weight = weight
        else:
            self.weight = weight / num

    def _get_weight(self)->Tuple:
        if self.is_leaf():
            return 1, self.weight
        else:
            num = 0
            weight = 0.0
            for subtree in self.subtrees:
                d = subtree._get_weight()
                num += d[0]
                weight += d[1]
            return num, weight

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight.

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """

        if limit is not None and limit <= 0:
            return []

        autocompleted = []
        if self.is_leaf():
            autocompleted.append((self.value, self.weight))
        elif len(self.value) >= len(prefix):
            if self.value[:len(prefix)] == prefix:
                for sub in self.subtrees:
                    temp = sub.autocomplete(prefix, limit)
                    autocompleted = self._merge(autocompleted, temp)
                    if limit is not None:
                        limit -= len(temp)
        else:
            if self.value == prefix[:len(self.value)]:
                for sub in self.subtrees:
                    if sub.value == prefix[:len(sub.value)]:
                        autocompleted += sub.autocomplete(prefix, limit)
                        break
        return autocompleted

    def _merge(self, lst1: List, lst2: List)->List:
        """
        Precondition: lst1 and lst are lists of tuples sorted in non-increasing order
        """
        lst = []
        index1 = 0
        index2 = 0
        while index1 < len(lst1) and index2 < len(lst2):
            if lst1[index1][1] >= lst2[index2][1]:
                lst.append(lst1[index1])
                index1 += 1
            else:
                lst.append(lst2[index2])
                index2 += 1
        if index1 == len(lst1):
            lst += lst2[index2:]
        else:
            lst += lst1[index1:]
        return lst

    def remove(self, prefix: List):
        if len(self.value) == len(prefix) - 1:
            for sub in self.subtrees:
                if sub.value == prefix:
                    self.subtrees.remove(sub)
        else:
            for sub in self.subtrees:
                if sub.value == prefix[:len(sub.value)]:
                    sub.remove(prefix)
                    if sub.subtrees == []:
                        self.subtrees.remove(sub)

        if self.subtrees == []:
            self.weight = 0.0
        else:
            num, weight = self._get_weight()
            if self.weight_type == "sum":
                self.weight = weight
            else:
                self.weight = weight / num


################################################################################
# CompressedPrefixTree (Task 6)
################################################################################
class CompressedPrefixTree(SimplePrefixTree):
    """A compressed prefix tree implementation.

    While this class has the same public interface as SimplePrefixTree,
    (including the initializer!) this version follows the implementation
    described on Task 6 of the assignment handout, which reduces the number of
    tree objects used to store values in the tree.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - **NEW**
      This tree does not contain any compressible internal values.
      (See the assignment handout for a definition of "compressible".)

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Optional[Any]
    weight: float
    subtrees: List[CompressedPrefixTree]
    _weight_type: str

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty compressed prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        SimplePrefixTree.__init__(self, weight_type)

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence

        >>> tree = CompressedPrefixTree('average')
        >>> tree.insert('cat', 3, ['c', 'a', 't'])
        >>> tree.insert('care', 2, ['c', 'a', 'r', 'e'])
        >>> tree.insert('car', 5, ['c', 'a', 'r'])
        >>> tree.insert('door', 1, ['d', 'o', 'o', 'r'])
        >>> tree.insert('danger', 4, ['d', 'a', 'n', 'g', 'e', 'r'])
        >>> tree.insert('cope', 3, ['c', 'o', 'p', 'e'])
        >>> tree.insert('cop', 2, ['c', 'o', 'p'])
        >>> tree.insert('copy', 2, ['c', 'o', 'p', 'y'])
        >>> tree.insert('can', 4, ['c', 'a', 'n'])
        >>> tree.insert('cane', 4, ['c', 'a', 'n', 'e'])
        >>> tree.insert('cute', 1, ['c', 'u', 't', 'e'])
        >>> tree.insert('cut', 2, ['c', 'u', 't'])
        >>> tree.insert('cut', 3, ['c', 'u', 't'])
        >>> print(tree._str_indented())
        ''
        """


if __name__ == '__main__':
    import doctest
    doctest.testmod()
#     import python_ta
#     python_ta.check_all(config={
#         'max-nested-blocks': 4
#     })
