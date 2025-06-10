import random
import psycopg2
import uuid
from flask_socketio import SocketIO
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
)


app = Flask(__name__)
app.config["SECRET_KEY"] = "SECRECT"
socketio = SocketIO(app)


# Use Flask's configuration handling for environment variables
app.config.from_pyfile(".env")

# Make a connection to the database
connection = psycopg2.connect(
    host=app.config["DB_HOST"],
    port=app.config["DB_PORT"],
    dbname=app.config["DB_NAME"],
    user=app.config["DB_USER"],
    password=app.config["DB_PASSWORD"],
)
cursor = connection.cursor()

# k marks global variables
# key with which user_id is save; only save id in cookie
# instead of whole game, for easier debugging
kUserIdCookieName = "user_id"
# Dictionary to store active game instances.
kActiveGames = {}
# Dictionary to store active players.
kActivePlayers = {}


class Player:
    def __init__(self, username, initial_data=None) -> None:
        """
        Initialize a Player instance. Either load initial data from a dictionary or initialize with default values.
        Args:
            username (str): The username of the player.
            initial_data (dict): A dictionary containing the initial data to load into the player instance.
        """
        # if there is no id in the session, it generates one
        if kUserIdCookieName not in session:
            print("Generating new id")
            session[kUserIdCookieName] = str(uuid.uuid4())
        self.id = session[kUserIdCookieName]  # Generate a unique player ID
        self._level = 1
        self._score = 0
        self._lives = 3
        self.__seenwords = set()
        self.username = username
        self._seen_hints = set()
        self.game_id = None
        self.hint_history = []
        self.expensive_hint_counter = 0
        self.hint_counter = 0
        self.sid = None
        self.timeout_round = None
        self.rounds_since_last_life = 0  # Track rounds since last received a life

    # takes word instance and checks if there is a hint that has not been used by the player yet
    def try_add_hint(self, word_instance, is_expensive):
        if is_expensive:
            hint = word_instance.get_expensive_hint(self.expensive_hint_counter)
            self.expensive_hint_counter += 1
        else:
            hint = word_instance.get_hint(self.hint_counter)
            self.hint_counter += 1
        # if no new hint is found, do nothing, otherwise save hints
        # expensive costs 4, small 2
        if hint is None:
            return
        self.hint_history.append(hint)
        if is_expensive:
            self.needed_hints(4)
            return
        self.needed_hints(2)

    def set_game_id(self, game_id):
        self.game_id = game_id

    def get_level(self):
        return self._level

    def get_score(self):
        return self._score

    def get_lives(self):
        return self._lives

    def has_seen(self, word):
        return word in self.__seenwords

    def add_seen(self, word):
        self.__seenwords.add(word)

    def wins(self, score):
        self._score += score

    def loses(self):
        self._lives -= 1

    def regain_life(self):
        self._lives = min(self._lives + 1, 3)  # Increment lives but max out at 3
        self.rounds_since_last_life = 0
        self.timeout_round = None

    def needed_hints(self, points):
        self._score -= points

    def level_up(self):
        self._level += 1

    # does not reset for each round anymore, but for each game; before the score was resetted after each round
    def reset(self):
        self.expensive_hint_counter = 0
        self.hint_counter = 0
        self.hint_history = []
        self.__seenwords = set()

    def update(self):
        if self._score >= 1000:
            self.level_up()
            self._score -= 1000

    # anytime there is an update (new player, a player submits guess etc) it emits and updates the play_game.html
    def emit_updated_player_list(self, player_list):
        if self.sid is None:
            return
        print("update_player_list")
        socketio.emit("update_player_list", {"data": player_list}, to=self.sid)

    def emit_game_end(self):
        assert self.sid is not None
        print("update_player_list")
        socketio.emit("game_end", to=self.sid)

    def __str__(self) -> str:
        return (
            f"Player {self.username} is at level {self._level} with {self._score}"
            f"points and {self._lives} lives left."
        )


# [/player]


# [word]

# Get all ids of words that do not contain an underscore or hyphen
# (not smart for big databases or when many people play the game -> we save all word ids in memory)
cursor.execute("SELECT word_id FROM clean_wordnet_data;")
ids = cursor.fetchall()
ids_set = {row[0] for row in ids}


def get_random_word_from_database(seen_ids):
    """
    Retrieve a random word from the database, excluding the seen_ids.

    Parameters:
    - seen_ids (set): A set of word_ids that should be excluded from the random selection.

    Returns:
    - result_tuple (tuple): A tuple containing:
        - seen_ids (set): The updated set of seen word_ids with the newly selected random_id.
        - word_data (tuple): A tuple containing the word data (word_id, word, definition, example,
            hypernym, hyponym, holonym, meronym, synonym, antonym) for the selected random word.
            Returns (None, None) if there are no available words to select.
    """
    global ids_set  # Assuming ids_set is a global variable

    # Calculate the set of available ids (ids_set - seen_ids)
    available_ids = ids_set - seen_ids

    if not available_ids:
        # If there are no available ids, return None or handle it as needed
        return None

    # Choose a random id from the available ids
    random_id = random.choice(list(available_ids))

    # Execute a query to get the word data for the random id
    cursor.execute(
        """
        SELECT 
            word_id,
            word,
            definition,
            example,
            hypernym,
            hyponym,
            holonym,
            meronym,
            synonym,
            antonym 
        FROM 
            wordnet_list 
        WHERE 
            word_id = %s;
        """,
        (random_id,),  # Use a tuple to pass the parameter to the query
    )
    word_data = cursor.fetchone()

    if word_data:
        # Convert certain columns to lists
        list_columns = [
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
        ]  # Columns corresponding to definition, example, hypernym, hyponym, holonym, meronym, synonym, antonym
        for col_index in list_columns:
            if word_data[col_index]:
                word_data = (
                    word_data[:col_index]
                    + (word_data[col_index].split(","),)
                    + word_data[col_index + 1 :]
                )

    # Update the seen_ids set with the newly selected random_id
    seen_ids.add(random_id)

    # for debugging
    print(f"word_data: {word_data}")

    # Return a tuple containing the updated seen_ids set and the word data
    return seen_ids, word_data


def get_jumbled_versions(original_word):
    """
    Generate a set of all jumbled versions of the original word except for the original word itself.

    Parameters:
    - original_word (str): The original word.

    Returns:
    - jumbled_versions (set): A set containing all jumbled versions of the original word.
    """
    # Convert the word to a list of characters for easy manipulation
    word_list = list(original_word)

    # Generate jumbled versions by shuffling the characters
    jumbled_versions = set()
    for _ in range(len(word_list) * 2):
        # Shuffle the characters without repetition
        shuffled_word = (
            original_word[0]
            + "".join(random.sample(word_list[1:-1], len(word_list) - 2))
            + original_word[-1]
        )

        # Ensure the shuffled word is different from the original word
        if shuffled_word != original_word:
            jumbled_versions.add(shuffled_word)

    return tuple(jumbled_versions)


class Word:
    def __init__(
        self,
        word_id,
        word=None,
        definition=None,
        example=None,
        hypernym=None,
        hyponym=None,
        holonym=None,
        meronym=None,
        synonym=None,
        antonym=None,
    ):
        """
        Initialize a Word instance. Either load initial data from a dictionary or initialize with default values.
        Args:
            word_id (int): The unique identifier of the word.
            word (str): The original word.
            definition (str): The definition of the word.
            example (str): An example usage of the word.
            hypernym (str): The hypernym (more abstract term) of the word.
            hyponym (str): The hyponym (more specific term) of the word.
            holonym (str): The holonym (part-whole relationship) of the word.
            meronym (str): The meronym (part of a whole) of the word.
            synonym (str): A synonym of the word.
            antonym (str): An antonym of the word.
        """
        self._word_id = word_id
        self._word = word.lower()
        self._definition = definition
        self._example = example
        self._hypernym = hypernym
        self._hyponym = hyponym
        self._holonym = holonym
        self._meronym = meronym
        self._antonym = antonym
        self._synonym = synonym
        self._jumbled_tuple = get_jumbled_versions(self._word)
        self.jumbled_word = self._jumbled_tuple[0] if self._jumbled_tuple else None
        self.__hints = []
        self.__expensive_hints = []

    # check if word and guess match; used in submit guess route
    def is_word(self, word_guess):
        print(f"Secret word is {self._word} v.s. {word_guess}")
        return self._word == word_guess.lower()

    def get_masked_definition(self):
        """
        Returns the definition of the word
        """
        if not self._definition:
            return []

        print(f"definition_data: {self._definition}")

        # If self._word is in any definition, replace it with the masked version
        masked_definitions = [
            definition.replace(self._word, "*" * len(self._word))
            for definition in self._definition
        ]

        return masked_definitions

    def get_masked_example(self):
        """
        Returns one randomly chosen masked example of the word
        """
        if not self._example:
            return []

        print(f"definition_data: {self._example}")

        # If self._word is in any definition, replace it with the masked version
        masked_examples = [
            example.replace(self._word, "*" * len(self._word))
            for example in self._example
        ]

        return masked_examples

    def __get_hypernyms(self):
        """
        Returns a random hypernym(More Abstract Term) of the word
        """
        if not self._hypernym:
            return []

        print(f"Hypernyms: {self._hypernym}")

        # Transform each hypernym into a little sentence
        hypernym_sentences = [
            f"The word is a {hypernym}" for hypernym in self._hypernym
        ]

        return hypernym_sentences

    def __get_hyponyms(self):
        """
        Returns a random hyponym(More Specific Term) of the word
        """
        if not self._hyponym:
            return []

        print(f"Hyponyms: {self._hyponym}")

        # Transform each hyponym into a little sentence
        hyponym_sentences = [
            f"{hyponym} is a type of the word" for hyponym in self._hyponym
        ]

        return hyponym_sentences

    def __get_holonyms(self):
        """
        Returns the holonyms(Whole Terms) of the word
        """
        if not self._holonym:
            return []

        print(f"Holonyms: {self._holonym}")

        # Transform each holonym into a little sentence
        holonym_sentences = [
            f"The word is part of {holonym}" for holonym in self._holonym
        ]

        return holonym_sentences

    def __get_meronyms(self):
        """
        Returns the meronyms(Parts of the word) of the word
        """
        if not self._meronym:
            return []

        print(f"Meronyms: {self._meronym}")

        # Transform each meronym into a little sentence
        meronym_sentences = [
            f"The word has a part called {meronym}" for meronym in self._meronym
        ]

        return meronym_sentences

    def __get_synonyms(self):
        """
        Returns the synonyms of the word
        """
        if not self._synonym:
            return []

        print(f"Synonyms: {self._synonym}")

        # Transform each synonym into a little sentence
        synonym_sentences = [
            f"{synonym} is a synonym of the word" for synonym in self._synonym
        ]

        return synonym_sentences

    def __get_antonyms(self):
        """
        Returns the antonyms of the word
        """
        if not self._antonym:
            return []

        print(f"Antonyms: {self._antonym}")

        # Transform each antonym into a little sentence
        antonym_sentences = [
            f"{antonym} is an antonym of the word" for antonym in self._antonym
        ]

        return antonym_sentences

    def generate_hints(self):
        self.__get_random_hint()

    def __get_random_hint(self):
        """
        Fills self.__hints and self.__expensive_hint swith randomly orderer hints.
        """
        hints = [
            self.__get_hypernyms,
            self.__get_hyponyms,
            self.__get_holonyms,
            self.__get_meronyms,
            self.__get_synonyms,
            self.__get_antonyms,
        ]
        expensive_hints = [
            self.get_masked_definition
        ]  # , self.get_masked_example -> verwenden wir nicht, weil useless]
        for hint_generator in hints:
            self.__hints += hint_generator()
        for hint_generator in expensive_hints:
            self.__expensive_hints = hint_generator()
        random.shuffle(self.__hints)
        random.shuffle(self.__expensive_hints)

    # iterates through hints
    def get_expensive_hint(self, expensive_hints_iterator):
        if expensive_hints_iterator >= len(self.__expensive_hints):
            return None
        return self.__expensive_hints[expensive_hints_iterator]

    def get_hint(self, hint_iterator):
        if hint_iterator >= len(self.__hints):
            return None
        return self.__hints[hint_iterator]


# [/word]


# [game]
class Game:
    MAX_PLAYERS_PER_GAME = 4

    def __init__(self, game_id, initial_data=None):
        """
        Initialize a game instance. Either load initial data from a dictionary or initialize with default values.
        Args:
            game_id (str): The unique ID of the game.
            initial_data (dict): A dictionary containing the initial data to load into the game instance.
        """

        self.game_id = game_id
        self.players = {}
        self.used_words = set()
        self.__current_word = None
        self.__current_round = 1
        self.__num_players = len(self.players)
        self.playing = False

    # game interface updates for all players when something happens (when game state changes)
    # does not change for player who makes the change
    # otherwise the update would also be sent to this player, resulting in a conflict between old and new site
    def emit_updated_player_list(self, skip_id):
        data = []
        for player in self.players.values():
            data.append(
                f"{player.username} - Level: {player.get_level()}, Score: {player.get_score()},"
                f"Lives: {player.get_lives()}"
            )
        for player in self.players.values():
            if skip_id is not None and player.id == skip_id:
                continue
            player.emit_updated_player_list(data)

    def get_word(self):
        return self.__current_word

    def __get_word(self):
        """
        Get a random word from the database that hasn't been used yet.
        and add it to the set of used words.
        Args:
            used_words (set): A set of words that have already been used.
        Returns:
            True if a word was successfully retrieved, False otherwise.
        """
        self.used_words, word_data = get_random_word_from_database(self.used_words)
        try:
            self.__current_word = Word(*word_data)
            return True
        except TypeError:
            return False

    def add_player(self, player):
        if len(self.players) < Game.MAX_PLAYERS_PER_GAME:
            assert self.game_id is not None
            player.game_id = self.game_id
            self.players[player.id] = player
            return True
        return False

    def start_round(self):
        """
        Start a new round by selecting a word and notifying all players
        """
        print(f"Round {self.__current_round}")
        try:
            self.__get_word()  # get a new word
            self.__current_word.generate_hints()  # generate hints for the word
            self.playing = True
            return True
        except ValueError:
            # No more words available
            print("No more words available")
            self.playing = False
            return False

    def process_guess(self, player_id, guess):
        """
        Process a player's guess and update scores accordingly
        """
        assert self.__current_word is not None
        if self.__current_word.is_word(guess):
            # The player guessed correctly
            # Award points based on the order of correct guesses
            points = 10 - self.__num_players + 1
            self.players[player_id].wins(points)
            self.end_round(player_id)
        else:
            # Notify the player that their guess was incorrect
            self.players[player_id].loses()
            if self.players[player_id].get_lives() <= 0:
                self.players[player_id].timeout_round = self.__current_round + 3

    # if a player requests hint, all player see update in score
    def request_hint(self, player_id, is_expensive=False):
        """
        Process a player's request for a hint and update scores accordingly
        """
        self.players[player_id].try_add_hint(self.__current_word, is_expensive)
        self.emit_updated_player_list(None)

    def end_round(self, player_id):
        """
        End the current round and prepare for the next round
        Clean up hint history,  and start the next round
        """
        # Print scores for the current round
        print("Round Scores:")
        scores = [
            f"{player.username}: {player.get_score()} points"
            for player in self.players.values()
        ]

        # Increment the round counter
        self.__current_round += 1

        for player in self.players.values():
            # Increment the rounds since last life if the player is not on timeout
            if not player.timeout_round or player.timeout_round < self.__current_round:
                player.rounds_since_last_life += 1

            # Regain a life if the player's timeout is over
            if player.timeout_round == self.__current_round:
                player.regain_life()

            # Regain a life every 8 rounds if the player is not already at max lives
            elif player.get_lives() < 3 and player.rounds_since_last_life >= 8:
                player.regain_life()

            # Reset hints and other per-round states
            player.reset()

            # Emit game end to all players except the one who ended the round
            if player_id != player.id:
                player.emit_game_end()

        # Start the next round
        self.start_round()


def get_or_create_game(game_id):
    if game_id not in kActiveGames:
        kActiveGames[game_id] = Game(game_id)
    return kActiveGames[game_id]


# [/game]


# The first time I connect to the server I get an ID, which is saved in player class
@socketio.on("connected")
def connected():
    print("%s connected" % request.sid)
    if kUserIdCookieName in session:
        kActivePlayers[session[kUserIdCookieName]].sid = request.sid
    else:
        print("No session data")


@app.route("/")
def intro():
    return render_template("intro.html", title="Intro Page")


@app.route("/home")
def homepage():
    return render_template("home.html", title="Welcome Player")


@app.route("/about")
def about():
    return render_template("about.html", title="About")


# Global list to store contact form submissions
contact_form_submissions = []


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/submit_contact_form", methods=["POST"])
def submit_contact_form():
    topic = request.form["topic"]
    email = request.form["email"]
    message = request.form["message"]

    # Append the submission to the global list
    contact_form_submissions.append(
        {"topic": topic, "email": email, "message": message}
    )

    # Redirect to a thank you page or back to the contact page
    return redirect("/thank_you")


@app.route("/thank_you")
def thanks():
    return render_template("thank_you.html")


# route for both hints
@app.route("/get_hint/<is_expensive>", methods=["GET"])
def get_hint(is_expensive):
    if kUserIdCookieName not in session:
        return redirect("/")
    assert session[kUserIdCookieName] in kActivePlayers, kActivePlayers.keys()
    player = kActivePlayers[session[kUserIdCookieName]]
    assert player is not None
    game = kActiveGames[player.game_id]
    assert game is not None, player
    game.request_hint(player.id, is_expensive == "true")
    return redirect(f"/play_game/{player.id}")


@app.route("/game", methods=["GET", "POST"])
def game_interface():
    """
    Handles the creation or joining of a game and redirects the player accordingly.

    Returns:
        If the request method is 'POST':
            - If the player is already in a game, redirects to the game page.
            - If the player successfully joins an existing game, redirects to the game page.
            - If no suitable game is found, creates a new game and redirects to the game page.
        If the request method is not 'POST', renders the 'error.html' template.
    """
    if request.method == "POST":
        username = request.form.get("username")
        player = Player(username)
        if player.id in kActivePlayers:
            kActivePlayers[player.id].username = username
        else:
            kActivePlayers[player.id] = player

        # Check if the player is already in a game
        for game_id, game in kActiveGames.items():
            for _, _player in game.players.items():
                if _player.id == player.id:
                    print("Back to your previous game")
                    return redirect(f"/play_game/{player.id}")
        # Try to join an existing game or create a new one
        for game_id, game in kActiveGames.items():
            if game.add_player(player):
                game.emit_updated_player_list(player.id)
                print("Join existing game!")
                return redirect(f"/play_game/{player.id}")
        print("Create new game")
        # If no suitable game is found, create a new one
        game_id = f"game_{len(kActiveGames) + 1}"
        kActiveGames[game_id] = Game(game_id)
        kActiveGames[game_id].add_player(player)
        kActiveGames[game_id].start_round()
        return redirect(f"/play_game/{player.id}")

    return render_template("error.html")


@app.route("/process-user", methods=["POST"])
def process_login():
    return game_interface()


@app.route("/play_game/<id>", methods=["GET", "POST"])
def play_game(id):
    """
    Play the word jumble game.

    Args:
        id (str): The id of the player. (unique)

    Returns:
        If the request method is POST, it handles game actions and redirects the player back to the game page
        with the updated URL.
        If the request method is GET, it renders the play_game template and passes relevant data to be displayed
        in the template.
    """

    # If there is no game ID in the session, redirect the player to the home page
    if kUserIdCookieName not in session:
        return redirect("/")

    current_player_id = session[kUserIdCookieName]
    # Recreate the Game instance using the saved data
    player = kActivePlayers[session[kUserIdCookieName]]
    print(player, list(kActivePlayers.keys()))
    assert player is not None
    game = kActiveGames[player.game_id]
    assert game is not None, player
    # Check if the request method is POST (i.e., the player submitted a form)
    # After 0 lives guessing is not possible
    if request.method == "POST" and player.get_lives() > 0:
        # Handle game actions for POST requests (e.g., guesses, hint requests)
        guess = request.form.get("user_guess")
        assert guess is not None
        game.process_guess(player.id, guess)
    game.emit_updated_player_list(player.id)
    return render_template(
        "play_game.html",
        players=game.players.values(),
        current_word=game.get_word(),
        current_player_id=current_player_id,
        hint_history=player.hint_history,
    )


if __name__ == "__main__":
    # app.run(debug=True)
    socketio.run(app, debug=True)
