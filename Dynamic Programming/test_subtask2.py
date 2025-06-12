import pytest
from metric import distance


@pytest.mark.parametrize(
    ["text1", "text2", "expected"],
    [
        ["This is a TEST.", "THIS is not a drill.", 4 / 11],
        ["The quick brown fox jumps over the lazy dog.", "The quick wild brown fox leaps and attacks George.", 17 / 20],
        ["A long time ago there was a girl named Lily.", "Once upon a time Drew had a girl called Lily.", 18 / 22],
        ["", "", 0.0],  # Test with empty strings
        ["Hello", "Hello", 0.0],  # Test with identical strings
        ["We go to school", "We leave the theatre", 1.125],  # Test with different sentences
        ["Mary goes to school", "Tom cold to school", 1],  # Test with similar sentences, but different cost options.
        ["Mary goes to school", "", 3], # Test with one empty
        ["", "Mary goes to school", 3], # Test with one empty
    ]
)
def test_distance_normalized(text1: str, text2: str, expected: float):
    assert distance(text1, text2, normalize=True) == expected
