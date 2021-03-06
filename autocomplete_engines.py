"""CSC148 Assignment 2: Autocomplete engines

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This file contains starter code for the three different autocomplete engines
you are writing for this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
import csv
from typing import Any, Dict, List, Optional, Tuple

from melody import Melody
from prefix_tree import SimplePrefixTree, CompressedPrefixTree


################################################################################
# Text-based Autocomplete Engines (Task 4)
################################################################################

def get_value_prefix_sentence(line: str) -> Tuple[str, List[str]]:
    """Return a tuple of lists for the Sentence Engine, where the first list
    contains the string input and the second list contains the value's prefix
    """
    str_input = ''
    for char in line:
        if char.isalnum() or char == " ":
            str_input += char
    prefix = str_input.lower().split()
    val = ''
    for word in prefix:
        val += word + " "
    val = val.rstrip()
    return val, prefix


def get_value_prefix_letter(line: str) -> Tuple[str, List[str]]:
    """Return a tuple of lists for the letter Engine, where the first list
    contains the string input and the second list contains the value's prefix
    """
    prefix = []
    str_input = ''
    for char in line:
        if char.isalnum() or char == " ":
            prefix.append(char.lower())
            str_input += char
    return str_input, prefix


class LetterAutocompleteEngine:
    """An autocomplete engine that suggests strings based on a few letters.

    The *prefix sequence* for a string is the list of characters in the string.
    This can include space characters.

    This autocomplete engine only stores and suggests strings with lowercase
    letters, numbers, and space characters; see the section on
    "Text sanitization" on the assignment handout.

    === Attributes ===
    autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
            - 'file': the path to a text file
            - 'autocompleter': either the string 'simple' or 'compressed',
              specifying which subclass of Autocompleter to use.
            - 'weight_type': either 'sum' or 'average', which specifies the
              weight type for the prefix tree.

        Each line of the specified file counts as one input string.
        Note that the line may or may not contain spaces.
        Each string must be sanitized, and if the resulting string contains
        at least one alphanumeric character, it is inserted into the
        Autocompleter.

        *Skip lines that do not contain at least one alphanumeric character!*

        When each string is inserted, it is given a weight of one.
        Note that it is possible for the same string to appear on more than
        one line of the input file; this would result in that string getting
        a larger weight (because of how Autocompleter.insert works).
        """
        # We've opened the file for you here. You should iterate over the
        # lines of the file and process them according to the description in
        # this method's docstring.

        string_data = {}  # type: Dict[str, [float, List[str]]]
        with open(config['file'], encoding='utf8') as f:
            for line in f.read().splitlines():
                if any(ch.isalnum() for ch in line):
                    # if there is an alphanumeric character in the line
                    str_input, prefix = get_value_prefix_letter(line)
                    if str_input in string_data:
                        string_data[str_input][0] += 1
                    else:
                        string_data[str_input] = [1]
                        string_data[str_input].append(prefix)

        if config['autocompleter'] == 'simple':
            self.autocompleter = SimplePrefixTree(config['weight_type'])
        else:
            self.autocompleter = CompressedPrefixTree(config['weight_type'])

        for string, data in string_data.items():
            self.autocompleter.insert(string, data[0], data[1])

    def autocomplete(self, prefix: str,
                     limit: Optional[int] = None) -> List[Tuple[str, float]]:
        """Return up to <limit> matches for the given prefix string.

        The return value is a list of tuples (string, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Note that the given prefix string must be transformed into a list
        of letters before being passed to the Autocompleter.

        Preconditions:
            limit is None or limit > 0
            <prefix> contains only lowercase alphanumeric characters and spaces
        """
        prefix_list = []
        for ch in prefix:
            prefix_list.append(ch)

        return self.autocompleter.autocomplete(prefix_list, limit)

    def remove(self, prefix: str) -> None:
        """Remove all strings that match the given prefix string.

        Note that the given prefix string must be transformed into a list
        of letters before being passed to the Autocompleter.

        Precondition: <prefix> contains only lowercase alphanumeric characters
                      and spaces.
        """
        prefix_list = []
        for ch in prefix:
            prefix_list.append(ch)

        self.autocompleter.remove(prefix_list)


class SentenceAutocompleteEngine:
    """An autocomplete engine that suggests strings based on a few words.

    A *word* is a string containing only alphanumeric characters.
    The *prefix sequence* for a string is the list of words in the string
    (separated by whitespace). The words themselves do not contain spaces.

    This autocomplete engine only stores and suggests strings with lowercase
    letters, numbers, and space characters; see the section on
    "Text sanitization" on the assignment handout.

    === Attributes ===
    autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
            - 'file': the path to a CSV file
            - 'autocompleter': either the string 'simple' or 'compressed',
              specifying which subclass of Autocompleter to use.
            - 'weight_type': either 'sum' or 'average', which specifies the
              weight type for the prefix tree.

        Precondition:
        The given file is a *CSV file* where each line has two entries:
            - the first entry is a string
            - the second entry is the a number representing the weight of that
              string

        Note that the line may or may not contain spaces.
        Each string must be sanitized, and if the resulting string contains
        at least one word, it is inserted into the Autocompleter.

        *Skip lines that do not contain at least one alphanumeric character!*

        When each string is inserted, it is given THE WEIGHT SPECIFIED ON THE
        LINE FROM THE CSV FILE. (Updated Nov 19)
        Note that it is possible for the same string to appear on more than
        one line of the input file; this would result in that string getting
        a larger weight.
        """
        # We haven't given you any starter code here! You should review how
        # you processed CSV files on Assignment 1.

        csv_data = {}  # type: Dict[str, [float, List[str]]]
        with open(config['file']) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                if any(ch.isalnum() for ch in line[0]):
                    # if there is an alphanumeric character in the line
                    val, prefix = get_value_prefix_sentence(line[0])
                    if val in csv_data:
                        csv_data[val][0] += float(line[1])
                    else:
                        csv_data[val] = [float(line[1])]
                        csv_data[val].append(prefix)

        if config['autocompleter'] == 'simple':
            self.autocompleter = SimplePrefixTree(config['weight_type'])
        else:
            self.autocompleter = CompressedPrefixTree(config['weight_type'])

        for words in csv_data:
            self.autocompleter.insert(words,
                                      csv_data[words][0],
                                      csv_data[words][1])

    def autocomplete(self, prefix: str,
                     limit: Optional[int] = None) -> List[Tuple[str, float]]:
        """Return up to <limit> matches for the given prefix string.

        The return value is a list of tuples (string, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Note that the given prefix string must be transformed into a list
        of words before being passed to the Autocompleter.

        Preconditions:
            limit is None or limit > 0
            <prefix> contains only lowercase alphanumeric characters and spaces
        """
        return self.autocompleter.autocomplete(prefix.split(), limit)

    def remove(self, prefix: str) -> None:
        """Remove all strings that match the given prefix.

        Note that the given prefix string must be transformed into a list
        of words before being passed to the Autocompleter.

        Precondition: <prefix> contains only lowercase alphanumeric characters
                      and spaces.
        """
        self.autocompleter.remove(prefix.split())


################################################################################
# Melody-based Autocomplete Engines (Task 5)
################################################################################
class MelodyAutocompleteEngine:
    """An autocomplete engine that suggests melodies based on a few intervals.

    The values stored are Melody objects, and the corresponding
    prefix sequence for a Melody is its interval sequence.

    Because the prefix is based only on interval sequence and not the
    starting pitch or duration of the notes, it is possible for different
    melodies to have the same prefix.

    # === Private Attributes ===
    autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
            - 'file': the path to a CSV file
            - 'autocompleter': either the string 'simple' or 'compressed',
              specifying which subclass of Autocompleter to use.
            - 'weight_type': either 'sum' or 'average', which specifies the
              weight type for the prefix tree.

        Precondition:
        The given file is a *CSV file* where each line has the following format:
            - The first entry is the name of a melody (a string).
            - The remaining entries are grouped into pairs (as in Assignment 1)
              where the first number in each pair is a note pitch,
              and the second number is the corresponding duration.

            HOWEVER, there may be blank entries (stored as an empty string '');
            as soon as you encounter a blank entry, stop processing this line
            and move onto the next line the CSV file.

        Each melody is be inserted into the Autocompleter with a weight of 1.
        """

        csv_data = []
        with open(config['file']) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                name = line[0]
                notes = []
                for i in range(1, len(line), 2):
                    if line[i] != '':
                        notes.append((int(line[i]), int(line[i+1])))
                    else:
                        break
                prefix = []
                for j in range(1, len(notes)):
                    interval = notes[j][0] - notes[j-1][0]
                    prefix.append(interval)
                csv_data.append([Melody(name, notes), prefix])

        if config['autocompleter'] == 'simple':
            self.autocompleter = SimplePrefixTree(config['weight_type'])
        else:
            self.autocompleter = CompressedPrefixTree(config['weight_type'])

        for data in csv_data:
            self.autocompleter.insert(data[0], 1, data[1])

    def autocomplete(self, prefix: List[int],
                     limit: Optional[int] = None) -> List[Tuple[Melody, float]]:
        """Return up to <limit> matches for the given interval sequence.

        The return value is a list of tuples (melody, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given interval sequence.

        Precondition:
            limit is None or limit > 0
        """
        return self.autocompleter.autocomplete(prefix, limit)

    def remove(self, prefix: List[int]) -> None:
        """Remove all melodies that match the given interval sequence.
        """
        self.autocompleter.remove(prefix)


###############################################################################
# Sample runs
###############################################################################
def sample_letter_autocomplete() -> List[Tuple[str, float]]:
    """A sample run of the letter autocomplete engine."""
    engine = LetterAutocompleteEngine({
        # NOTE: you should also try 'data/google_no_swears.txt' for the file.
        'file': 'data/google_no_swears.txt',
        'autocompleter': 'simple',
        'weight_type': 'sum'
    })
    return engine.autocomplete('postal', 20)


def sample_sentence_autocomplete() -> List[Tuple[str, float]]:
    """A sample run of the sentence autocomplete engine."""
    engine = SentenceAutocompleteEngine({
        'file': 'data/google_searches.csv',
        'autocompleter': 'simple',
        'weight_type': 'sum'
    })
    return engine.autocomplete('how to', 20)


def sample_melody_autocomplete() -> None:
    """A sample run of the melody autocomplete engine."""
    engine = MelodyAutocompleteEngine({
        'file': 'data/random_melodies_c_scale.csv',
        'autocompleter': 'simple',
        'weight_type': 'sum'
    })
    melodies = engine.autocomplete([2, 2], 20)
    for melody, _ in melodies:
        melody.play()


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['__init__'],
        'extra-imports': ['csv', 'prefix_tree', 'melody']
    })

    # import doctest
    # doctest.testmod()
    # This is used to increase the recursion limit so that your sample runs
    # work even for fairly tall simple prefix trees.
    # import sys
    # sys.setrecursionlimit(5000)

    print(sample_letter_autocomplete())
    # print(sample_sentence_autocomplete())
    # sample_melody_autocomplete()
