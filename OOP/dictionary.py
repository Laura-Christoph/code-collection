import re
from collections import defaultdict


class Dictionary:
    """Class for translating lemmas based on Wiktionary."""
    def __init__(self, filename: str):
        """
        Parse Wiktionary data from a file.
        
        Args:
            filename: Path to the file containing Wiktionary data.
        """
        self._dict = defaultdict(set)
        # Structure: {lemma: {translation}}
        self._pos_dict = defaultdict(lambda: defaultdict(set)) # Second dict in case pos is declared with an inner dict
        # Structure: {lemma: {pos: {translation}}}

        with open(filename, encoding="utf-8") as f:
            for line in f:
                # Ignore comments
                if line.startswith("#"):
                    continue
                # Parse line
                lemma, translations = re.match(r"(.+) \{.+\} .*:: (.*)", line).groups()
                for translation in translations.split(","):
                    translation = translation.strip()
                    self._dict[lemma].add(translation)

                    # Put the translations with the pos tag in the specific pos dict, but only if we have a pos tag:
                    match = re.search(r"\{(.*?)\}", line)
                    if match:
                        pos = match.group(1)
                        self._pos_dict[lemma][pos].add(translation)
        
        # Convert defaultdicts to dicts for easier handling
        self._pos_dict = dict(self._pos_dict)
        for key, value in self._pos_dict.items():
            self._pos_dict[key] = dict(value)

    def translate(self, lemma: str, pos=None) -> list:
        """
        Translate a lemma into the target language.
        
        Args:
            lemma: The lemma to translate.
        """
        if pos is None: # If no pos is given, return all translations
            translations = self._dict[lemma]
            return sorted(translations)
        if pos: # If pos is given, return only the translations with the pos tag
            try:
                translations = self._pos_dict[lemma][pos]
                return sorted(translations)
            except KeyError: # If this lemma doesn't have the pos tag, return an empty list
                return []


class BidirDictionary(Dictionary):
    def __init__(self, filename: str):
        """
        Parse Wiktionary data and create the reverse dictionary.

        Args:
            filename: Path to the file containing Wiktionary data.

        Used ChatGPT for the inversion of the dicts: "Reverse the following dicts (snippet of what the dicts look like)" and modified the code
        """
        super().__init__(filename) # Inheriting from the Dictionary class
        self._reverse_dict = defaultdict(set) # Structure: {translation: {lemma}}
        for lemma, translations in self._dict.items(): # Reversing the en-fi dictionary without pos tags
            for translation in translations:
                self._reverse_dict[translation].add(lemma)

        self._reverse_pos_dict = defaultdict(dict) # Structure: {translation: {pos: {lemma}}}
        for lemma, pos_dict in self._pos_dict.items(): # Reversing the en-fi dictionary with pos tags
            for pos, translations in pos_dict.items():
                for translation in translations:
                    self._reverse_pos_dict[translation].setdefault(pos, set()).add(lemma)

        # Convert defaultdicts to dicts for easier handling
        self._reverse_pos_dict = dict(self._reverse_pos_dict)
        for key, value in self._reverse_pos_dict.items():
            self._reverse_pos_dict[key] = dict(value)

    def reverse_translate(self, lemma: str, pos=None) -> list:
        """
        Translate a lemma from Finnish to english.
        
        Args:
            lemma: The lemma to translate.
            pos: The part-of-speech-tag, optional
        """
        if pos is None: # If no pos is given, return all translations
            translations = self._reverse_dict[lemma]
            return sorted(translations)
        if pos: # If pos is given, return only the translations with the pos tag
            try:
                translations = self._reverse_pos_dict[lemma][pos]
                return sorted(translations)
            except KeyError: # If this lemma doesn't have the pos tag, return an empty list
                return []
