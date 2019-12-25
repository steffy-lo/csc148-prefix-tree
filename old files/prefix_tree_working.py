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
    _weight_type: str

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
        self._weight_type = weight_type

    def __len__(self) -> int:
        """Returns the number of values stored in this simple prefix tree"""
        if self.is_empty():
            return 0
        elif self.is_leaf():  # this tree is a leaf
            return 1
        else:
            num = 0
            for subtree in self.subtrees:
                num += subtree.__len__()
            return num

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

        >>> tree = SimplePrefixTree('average')
        >>> tree.insert('cat', 3, ['c', 'a', 't'])
        >>> tree.insert('care', 2, ['c', 'a', 'r', 'e'])
        >>> tree.insert('car', 5, ['c', 'a', 'r'])
        >>> tree.insert('door', 1, ['d', 'o', 'o', 'r'])
        >>> tree.insert('danger', 4, ['d', 'a', 'n', 'g', 'e', 'r'])
        >>> tree.insert('cope', 3, ['c', 'o', 'p', 'e'])
        >>> tree.insert('cop', 2, ['c', 'o', 'p'])
        """
        # Each subtree needs to be sorted in a non-increasing weight order
        if prefix == []:
            if self.subtrees != []:
                insert_leaf = True
                for subtree in self.subtrees:
                    if subtree.value == value:
                        self.update_weight(weight)
                        subtree.update_weight(weight)
                        insert_leaf = False
                if insert_leaf is True:
                    self.insert_new_leaf(value, weight)
                    # Don't need to update weight since it will be updated later
            else:
                self.insert_new_leaf(value, weight)
                self.weight = weight

            self.subtrees.sort(key=lambda trees: trees.weight, reverse=True)

        else:
            inserted = False
            for subtree in self.subtrees:
                if subtree.subtrees != []:  # not a leaf
                    if subtree.value == subtree.value[:-1] + prefix[:1]:
                        subtree.insert(value, weight, prefix[1:])
                        subtree.update_weight(weight)
                        if subtree.value == prefix[:1]:
                            self.update_weight(weight)
                        inserted = True

            if inserted is False:
                new_tree = SimplePrefixTree(self._weight_type)
                new_tree.value = self.value + prefix[:1]
                new_tree.weight = weight
                self.subtrees.append(new_tree)
                new_tree.insert(value, weight, prefix[1:])
                if new_tree.value == prefix[:1]:
                    self.update_weight(weight)

            self.subtrees.sort(key=lambda trees: trees.weight, reverse=True)

    def update_weight(self, weight):
        if self._weight_type == 'sum':
            self.weight += weight
        else:
            if len(self) <= 1:
                self.weight += weight
            else:
                self.weight = \
                    ((len(self) - 1) * self.weight + weight) / len(self)

    def insert_new_leaf(self, value, weight):
        new_leaf = SimplePrefixTree(self._weight_type)
        new_leaf.value = value
        new_leaf.weight = weight
        self.subtrees.append(new_leaf)

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.

        >>> tree = SimplePrefixTree('sum')
        >>> tree.insert('cat', 3, ['c', 'a', 't'])
        >>> tree.insert('care', 2, ['c', 'a', 'r', 'e'])
        >>> tree.insert('car', 5, ['c', 'a', 'r'])
        >>> tree.insert('door', 1, ['d', 'o', 'o', 'r'])
        >>> tree.insert('danger', 4, ['d', 'a', 'n', 'g', 'e', 'r'])
        >>> tree.insert('cope', 3, ['c', 'o', 'p', 'e'])
        >>> tree.insert('cop', 2, ['c', 'o', 'p'])
        >>> tree.autocomplete(['c', 'a'])
        [('car', 5), ('cat', 3), ('care', 2)]
        >>> tree.autocomplete(['c'])
        [('car', 5), ('cat', 3), ('cope', 3), ('care', 2), ('cop', 2)]
        >>> tree.autocomplete(['c', 'o'], 1)
        [('cope', 3)]
        >>> tree.autocomplete(['d'], 1)
        [('danger', 4)]
        >>> tree.autocomplete(['c'], 3)
        [('car', 5), ('cat', 3), ('cope', 3)]
        >>> tree.autocomplete(['c', 'a', 'r', 'e'])
        [('care', 2)]
        """

        if self.is_empty():
            return []
        elif self.subtrees == [] and self.weight > 0:
            return [(self.value, self.weight)]
        else:
            autocomp = []
            if limit is None:
                for subtree in self.subtrees:
                    if self.value == prefix[:len(self.value)] or \
                            self.value == prefix + self.value[len(prefix):]:
                        # if subtree.subtrees == [] and
                        # len(self.value) < len(prefix):
                        # This subtree is not valid to be autocompleted
                        # take its negation, we have:
                        if subtree.subtrees != [] or len(self.value) >= len(prefix):
                            autocomp += subtree.autocomplete(prefix)
                    # break ties will be based on alphabetical order
                autocomp.sort(key=lambda t: t[1], reverse=True)
                return autocomp
            else:
                counter = 0
                for subtree in self.subtrees:
                    if self.value == prefix[:len(self.value)] or \
                            self.value == prefix + self.value[len(prefix):]:
                        if subtree.subtrees != [] or len(self.value) >= len(prefix):
                            autocomp += subtree.autocomplete(prefix)
                            counter += len(subtree.autocomplete(prefix))
                        if counter >= limit:
                            return autocomp[:limit]

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        if not self.is_empty():
            if self.value == prefix[:len(self.value)]:
                leaves_weight = 0
                leaves = self.autocomplete(prefix)
                for leaf in leaves:
                    leaves_weight += leaf[1]
                self.update_weight(-leaves_weight)
                subtree_to_remove = []
                for subtree in self.subtrees:
                    if subtree.weight - leaves_weight == 0:
                        subtree_to_remove.append(subtree)
                    else:
                        subtree.remove(prefix)
                # Remove trees
                for subtree in subtree_to_remove:
                    self.subtrees.remove(subtree)

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

        >>> tree = CompressedPrefixTree('sum')
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
        >>> print(tree._str_indented())
        """
        if self.is_empty():
            self.update_weight(weight)
            self.subtrees.append(self.new_tree_leaf(value, weight, prefix))
        else:
            new_old_subtree = []
            insert = False
            for subtree in self.subtrees:
                i = len(subtree.value)
                while insert is False and i > 0:
                    for subtree in self.subtrees:
                        if prefix[:i] == subtree.value[:i]:
                            insert = True
                            if i < len(subtree.value):
                                if len(prefix) >= len(subtree.value):
                                    new_tree = \
                                        CompressedPrefixTree(self._weight_type)
                                    new_tree.value = prefix[:i]
                                    new_tree.subtrees.append(self.new_tree_leaf
                                                             (value,
                                                              weight,
                                                              prefix))
                                    if new_tree._weight_type == 'sum':
                                        new_tree.weight = subtree.weight+weight
                                    else:
                                        new_tree.weight \
                                            = (subtree.weight * len(subtree) +
                                               weight) / (len(subtree) + 1)
                                    new_old_subtree.append(new_tree)
                                    new_old_subtree.append(subtree)
                                else:  # len(prefix) < len(subtree.value)
                                    new_tree = CompressedPrefixTree(
                                        self._weight_type)
                                    new_tree.value = prefix
                                    if new_tree._weight_type == 'sum':
                                        new_tree.weight += subtree.weight+weight
                                    else:
                                        new_tree.weight \
                                            = (subtree.weight * len(subtree) +
                                               weight) / (len(subtree) + 1)
                                        new_tree.insert_new_leaf(value, weight)
                                        new_old_subtree.append(new_tree)
                                        new_old_subtree.append(subtree)
                            else:  # i = len(subtree.value)
                                # len(prefix) >= subtree.value
                                if len(prefix) == len(subtree.value):
                                    inserted = False
                                    for subsubtree in subtree.subtrees:
                                        if subsubtree.value == value:
                                            inserted = True
                                            self.update_weight(weight)
                                            subtree.update_weight(weight)
                                            subsubtree.update_weight(weight)
                                    if inserted is False:
                                        subtree.insert_new_leaf(value, weight)
                                        self.update_weight(weight)
                                        subtree.update_weight(weight)
                                else:  # len(prefix) > subtree.value
                                    if self._weight_type == 'sum':
                                        self.weight += weight
                                    else:
                                        self.weight = \
                                            (len(self) * self.weight + weight) \
                                            / (len(self) + 1)
                                    subtree.insert(value, weight, prefix)
                    i -= 1

            if insert is False:
                self.subtrees.append(self.new_tree_leaf(value,
                                                        weight,
                                                        prefix))
                self.update_weight(weight)
                self.subtrees.sort(key=lambda trees: trees.weight, reverse=True)

            if len(new_old_subtree) == 2:
                self.subtrees.append(new_old_subtree[0])
                self.subtrees.remove(new_old_subtree[1])
                new_old_subtree[0].subtrees.append(new_old_subtree[1])
                self.update_weight(weight)
                self.subtrees.sort(key=lambda trees: trees.weight, reverse=True)
            elif len(new_old_subtree) > 2:
                # means new_old_subtree[0].value == new_old_subtree[2].value,
                # so prefix should exist and we just append directly
                self.subtrees.append(self.new_tree_leaf(value, weight, prefix))
                self.update_weight(weight)
                self.subtrees.sort(key=lambda trees: trees.weight, reverse=True)

    def new_tree_leaf(self, value, weight, prefix):
        new_tree = CompressedPrefixTree(self._weight_type)
        new_tree.value = prefix
        new_tree.weight += weight
        new_leaf = CompressedPrefixTree(self._weight_type)
        new_leaf.value = value
        new_leaf.weight = weight
        new_tree.subtrees.append(new_leaf)
        return new_tree

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        return SimplePrefixTree.autocomplete(self, prefix, limit)

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        SimplePrefixTree.remove(self, prefix)


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    # import python_ta
    # python_ta.check_all(config={
    #     'max-nested-blocks': 4
    # })
