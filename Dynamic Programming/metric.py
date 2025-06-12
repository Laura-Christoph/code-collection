import spacy

nlp = spacy.load("en_core_web_sm")


def get_specific_cost(pos):
    if pos == 'VERB':
        return 5
    elif pos in ['NOUN', 'PROPN']:
        return 3
    elif pos == 'ADJ':
        return 2
    else:
        return 1


def distance(text1: str, text2: str, normalize: bool = False) -> float:
    """
    Calculates the distance between two strings using the Levenshtein distance algorithm.
    Parameters:
        text1: The first string.
        text2: The second string.
        normalize: Whether to normalize the distance or not.
    Return: 
        The distance between the two strings.

    """
    tokens1 = [token.text for token in nlp(text1)]
    tokens2 = [token.text for token in nlp(text2)]

    pos1 = [token.pos_ for token in nlp(text1)]
    pos2 = [token.pos_ for token in nlp(text2)]

    table = [[0 for _ in range(len(tokens2) + 1)] for _ in range(len(tokens1) + 1)]

    # Filling in the first row and column
    for i in range(len(tokens1) + 1):
        table[i][0] = i * get_specific_cost(pos1[i - 1]) if i > 0 else 0 
    for j in range(len(tokens2) + 1):
        table[0][j] = j * get_specific_cost(pos2[j - 1]) if j > 0 else 0 

    # Filling in the rest of the table
    for i in range(1, len(tokens1) + 1):
        for j in range(1, len(tokens2) + 1):
            if tokens1[i - 1].lower() == tokens2[j - 1].lower() and pos1[i - 1] == pos2[j - 1]:
                table[i][j] = table[i - 1][j - 1]
            else:
                special_cost = max(get_specific_cost(pos1[i - 1]), get_specific_cost(pos2[j - 1]))
                table[i][j] = min(
                    table[i - 1][j] + get_specific_cost(pos1[i - 1]),  # deletion cost
                    table[i][j - 1] + get_specific_cost(pos2[j - 1]),  # insertion cost
                    table[i - 1][j - 1] + special_cost,  # substitution cost
                )

    distance_value = table[len(tokens1)][len(tokens2)] 
    if normalize: # If you want to normalize it
        total_tokens = len(tokens1) + len(tokens2) # Total number of tokens
        if (total_tokens != 0) and (distance_value != 0): # Making sure neither number is 0 to avoid ZeroDivisionError
            normalized_distance = distance_value / total_tokens
        else: # If either number was zero, it would be zero anyways
            normalized_distance = 0
        return normalized_distance
    else:
        return distance_value
