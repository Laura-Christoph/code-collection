import pytest
from dictionary import Dictionary


@pytest.fixture
def dictionary():
    return Dictionary("en-fi.txt")


def test_translate(dictionary):
    assert dictionary.translate("earpick") == ["korvapuikko"]
    assert dictionary.translate("mill") == ["jauhaa", "jyrsiä", "kaivertaa", "mylly", "pyöriä", "tehdas", "tehdasrakennus", "työstää"]
    assert dictionary.translate("notinthedictionary") == []


def test_translate_pos(dictionary):
    assert dictionary.translate("earpick", "n") == ["korvapuikko"]
    assert dictionary.translate("earpick", "v") == []
    assert dictionary.translate("mill", "n") == ["mylly", "tehdas", "tehdasrakennus"]
    assert dictionary.translate("mill", "v") == ["jauhaa", "jyrsiä", "kaivertaa", "pyöriä", "työstää"]
    assert dictionary.translate("notinthedictionary", "adj") == []
