import pytest
from dictionary import BidirDictionary


@pytest.fixture
def bidir_dictionary():
    return BidirDictionary("en-fi.txt")


def test_reverse_translate(bidir_dictionary):
    assert bidir_dictionary.reverse_translate("korvapuikko") == ["earpick"]
    assert bidir_dictionary.reverse_translate("mylly") == ["mill"]
    assert bidir_dictionary.reverse_translate("notinthedictionary") == []


def test_reverse_translate_pos(bidir_dictionary):
    assert bidir_dictionary.reverse_translate("korvapuikko", "n") == ["earpick"]
    assert bidir_dictionary.reverse_translate("korvapuikko", "v") == []
    assert bidir_dictionary.reverse_translate("jyrsiä", "n") == []
    assert bidir_dictionary.reverse_translate("jyrsiä", "v") == ["gnaw", "mill"]
    assert bidir_dictionary.reverse_translate("notinthedictionary", "adj") == []
