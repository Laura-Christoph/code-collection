import pytest
from metric import distance

# Test inspiration from ChatGPT by entering the exercise description, own examples

@pytest.mark.parametrize(
    ["text1", "text2", "expected"],
    [
        ["This is a TEST.", "THIS is not a drill.", 4],
        ["The quick brown fox jumps over the lazy dog.", "The quick wild brown fox leaps and attacks George.", 17],
        ["A long time ago there was a girl named Lily.", "Once upon a time Drew had a girl called Lily.", 18],
        ["", "", 0],  # Test with empty strings
        ["We go to school", "We leave the theatre", 9],  # Test with different sentences
        ["Mary goes to school", "Tom cold to school", 8],  # Test with similar sentences, different cost options
        ["Mary goes to school", "", 12], # Test with one empty
        ["", "Mary goes to school", 12], # Test with one empty
    ]
)
def test_distance(text1: str, text2: str, expected: float):
    assert distance(text1, text2) == expected
