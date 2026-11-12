
from drafter import *
from dataclasses import dataclass
import random

set_website_title("Minesweeper")
set_site_information(
    author="Sophia Singh",
    description="Find all the safe tiles in a grid.",
    sources="Thanks to the Drafter docs and Chat GPT.",
    planning=["plan.pdf", "design.pdf"],
    links=["https://sophiasingh3120.github.io/minesweeper/"]
)
hide_debug_information()
set_website_framed(False)



# Constants
BOARD_SIZE = 8
MINE_COUNT = 12
SAFE_TILE_COUNT = BOARD_SIZE * BOARD_SIZE - MINE_COUNT

# Represents one tile on the game board.
@dataclass
class Tile:
    row: int
    column: int
    has_mine: bool
    revealed: bool


# Stores all information about the current game.
@dataclass
class State:
    player_name: str
    score: int
    tiles: list[Tile]
    game_status: str
    feedback: str
    message: str


# Creates the 64 tiles and places mines at chosen positions.
def create_board(mine_positions: list[int]) -> list[Tile]:
    """Create an 8 by 8 board using the supplied mine positions."""
    tiles = []

    for position in range(BOARD_SIZE * BOARD_SIZE):
        row = position // BOARD_SIZE
        column = position % BOARD_SIZE

        tile = Tile(
            row,
            column,
            position in mine_positions,
            False
        )

        tiles.append(tile)

    return tiles


# Checks whether every safe tile has been revealed.
def has_won(tiles: list[Tile]) -> bool:
    """Return True when all tiles without mines are revealed."""
    for tile in tiles:
        if not tile.has_mine and not tile.revealed:
            return False

    return True


# Starts a fresh round.
def start_new_round(state: State) -> None:
    """Reset the game and randomly place exactly three mines.

    random.sample chooses three different positions from the 64
    available positions. The exact mine layout is randomized, so
    tests check the board size and mine count instead of exact
    positions.
    """
    mine_positions = random.sample(
        range(BOARD_SIZE * BOARD_SIZE),
        MINE_COUNT
    )

    state.tiles = create_board(mine_positions)
    state.score = 0
    state.game_status = "playing"
    state.feedback = ""
    state.message = ""


# Creates the buttons that make up the 8 by 8 board.
def create_grid(state: State) -> list:
    """Create one button for each unrevealed tile."""
    grid = []

    for position, tile in enumerate(state.tiles):

        if tile.revealed:
            if tile.has_mine:
                grid.append("💣")
            else:
                grid.append("✨")

        else:
            grid.append(
                Button(
                    "?",
                    "choose_tile",
                    [Argument("tile_index", position)]
                )
            )

        # Move to the next line after every eight tiles.
        if (position + 1) % BOARD_SIZE == 0:
            grid.append("\n")

    return grid


# --------------------------------------------------
# ROUTE 1: HOME PAGE
# --------------------------------------------------

@route
def index(state: State) -> Page:
    """Display the home page and collect the player's name."""
    return Page(state, [
        Header("MINESWEEPER"),
        "Welcome to Minesweeper!",
        "Try to uncover all" + " " + str(SAFE_TILE_COUNT) + " " + "safe tiles without hitting a mine.",
        "\n",
        Header("Enter Your Name"),
        TextBox("player_name"),
        Button("Start Game", "start_game"),
        "\n",
        state.message
    ])


# --------------------------------------------------
# ROUTE 2: SAVE NAME AND CONTINUE
# --------------------------------------------------

@route
def start_game(state: State, player_name: str) -> Page:
    """Save the player's name and take them to instructions."""
    if player_name.strip() == "":
        state.player_name = "Player"
    else:
        state.player_name = player_name.strip()

    state.message = ""

    return instructions(state)


# --------------------------------------------------
# ROUTE 3: INSTRUCTIONS PAGE
# --------------------------------------------------

@route
def instructions(state: State) -> Page:
    """Explain the rules before the player begins."""
    return Page(state, [
        Header("How To Play"),
        "Welcome, " + state.player_name + "!",
        "\n",
        "Here are the rules:",
        "\n",
        "1. The board contains 64 tiles arranged in an 8 by 8 grid.",
        "2. There are exactly 12 mines hidden on the board.",
        "3. Click one tile at a time to reveal it.",
        "4. If the tile is safe, you earn 1 point.",
        "5. If the tile contains a mine, the game is over.",
        "6. Reveal all 52 safe tiles to win!",
        "\n",
        state.message,
        CheckBox("ready"),
        " I understand the instructions.",
        "\n",
        Button("Start Playing", "begin_game")
    ])


# --------------------------------------------------
# ROUTE 4: BEGIN THE GAME
# --------------------------------------------------

@route
def begin_game(state: State, ready: bool) -> Page:
    """Check that the player is ready and start a new round."""
    if ready:
        start_new_round(state)
        return game(state)

    else:
        state.message = "Please check the box before playing."
        return instructions(state)


# --------------------------------------------------
# ROUTE 5: ACTUAL GAME PAGE
# --------------------------------------------------

@route
def game(state: State) -> Page:
    """Display the current score and the 8 by 8 game board."""
    if state.game_status == "lost":
        return game_over(state)

    if state.game_status == "won":
        return congratulations(state)

    content = [
        Header("MINESWEEPER"),
        "Player: " + state.player_name,
        "\n",
        "Score: " + str(state.score) + " / " + str(SAFE_TILE_COUNT), 
        "\n",
        "Choose a tile below!",
        "\n"
    ]

    content += create_grid(state)

    content += [
        "\n",
        "Each safe tile is worth 1 point."
    ]

    return Page(state, content)


# --------------------------------------------------
# ROUTE 6: PLAYER CHOOSES A TILE
# --------------------------------------------------

@route
def choose_tile(state: State, tile_index: int) -> Page:
    """Reveal a tile and update the score or end the game."""
    if state.game_status != "playing":
        return game(state)

    if tile_index < 0 or tile_index >= len(state.tiles):
        return game(state)

    selected_tile = state.tiles[tile_index]

    if selected_tile.revealed:
        return game(state)

    selected_tile.revealed = True

    if selected_tile.has_mine:
        state.game_status = "lost"
        return game_over(state)

    else:
        state.score = state.score + 1

    if has_won(state.tiles):
        state.game_status = "won"
        return congratulations(state)

    return game(state)


# --------------------------------------------------
# ROUTE 7: CONGRATULATIONS PAGE
# --------------------------------------------------

@route
def congratulations(state: State) -> Page:
    """Display the winning page when all safe tiles are revealed."""
    content = [
        Header("CONGRATULATIONS!"),
        "Amazing job, " + state.player_name + "!",
        "\n",
        "You successfully revealed all" + str(SAFE_TILE_COUNT) + "safe tiles!",
        "You won the game!",
        "\n",
        "Final Score: " + str(state.score),
        "\n"
    ]

    if state.feedback != "":
        content.append("Your feedback: " + state.feedback)

    content += [
        "Would you like to play again?",
        Button("Play Again", "restart_game"),
        "\n",
        "Leave feedback about the game:",
        TextArea("player_feedback"),
        Button("Submit Feedback", "submit_feedback"),
        Button("Home", "index")
    ]

    return Page(state, content)


# --------------------------------------------------
# ROUTE 8: GAME OVER PAGE
# --------------------------------------------------

@route
def game_over(state: State) -> Page:
    """Display the game over page when the player hits a mine."""
    content = [
        Header("GAME OVER!"),
        "Sorry, " + state.player_name + "!",
        "\n",
        "You selected a tile containing a mine.",
        "Better luck next time!",
        "\n",
        "Your Final Score: " + str(state.score),
        "\n"
    ]

    if state.feedback != "":
        content.append("Your feedback: " + state.feedback)

    content += [
        Button("Play Again", "restart_game"),
        "\n",
        "Leave feedback about the game:",
        TextArea("player_feedback"),
        Button("Submit Feedback", "submit_feedback"),
        Button("Home", "index")
    ]

    return Page(state, content)


# --------------------------------------------------
# ROUTE 9: SUBMIT PLAYER FEEDBACK
# --------------------------------------------------

@route
def submit_feedback(
    state: State,
    player_feedback: str
) -> Page:
    """Save the player's feedback and return to their result page."""
    state.feedback = player_feedback.strip()

    if state.game_status == "won":
        return congratulations(state)

    else:
        return game_over(state)


# --------------------------------------------------
# ROUTE 10: RESTART THE GAME
# --------------------------------------------------

@route
def restart_game(state: State) -> Page:
    """Start another game with a new random mine layout."""
    start_new_round(state)
    return game(state)


# --------------------------------------------------
# UNIT TESTS
# --------------------------------------------------

# --------------------------------------------------
# UNIT TESTS
# --------------------------------------------------

# Test board creation.
test_tiles = create_board(list(range(MINE_COUNT)))

assert_equal(len(test_tiles), 64)
assert_equal(
    sum(1 for tile in test_tiles if tile.has_mine),
    12
)

# Test that the board contains 52 safe tiles.
assert_equal(
    sum(1 for tile in test_tiles if not tile.has_mine),
    52
)

# Test the winning condition.
for test_tile in test_tiles:
    if not test_tile.has_mine:
        test_tile.revealed = True

assert_equal(has_won(test_tiles), True)

# Test that the game is not won if a safe tile remains.
unfinished_tiles = create_board(list(range(MINE_COUNT)))

for test_tile in unfinished_tiles:
    if not test_tile.has_mine:
        test_tile.revealed = True

unfinished_tiles[20].revealed = False

assert_equal(has_won(unfinished_tiles), False)


# Test Route 1: Home page.
test_state = State("", 0, [], "not_started", "", "")

assert_has(index(test_state), "MINESWEEPER")
assert_has(index(test_state), TextBox("player_name"))


# Test Route 2: Save the player's name.
name_page = start_game(
    State("", 0, [], "not_started", "", ""),
    "Alex"
)

assert_equal(name_page.state.player_name, "Alex")


# Test Route 2: Empty player name.
empty_name_page = start_game(
    State("", 0, [], "not_started", "", ""),
    "   "
)

assert_equal(empty_name_page.state.player_name, "Player")


# Test Route 3: Instructions page.
instruction_state = State(
    "Alex", 0, [], "not_started", "", ""
)

assert_has(instructions(instruction_state), "How To Play")
assert_has(instructions(instruction_state), CheckBox("ready"))
assert_has(instructions(instruction_state), "52 safe tiles")


# Test Route 4: Player cannot start without checking the box.
not_ready_state = State(
    "Alex", 0, [], "not_started", "", ""
)

not_ready_page = begin_game(not_ready_state, False)

assert_equal(
    not_ready_page.state.message,
    "Please check the box before playing."
)


# Test Route 4: Starting a game creates 64 tiles and 12 mines.
ready_state = State(
    "Alex", 0, [], "not_started", "", ""
)

ready_page = begin_game(ready_state, True)

assert_equal(len(ready_page.state.tiles), 64)
assert_equal(ready_page.state.score, 0)
assert_equal(ready_page.state.game_status, "playing")

assert_equal(
    sum(1 for tile in ready_page.state.tiles if tile.has_mine),
    12
)


# Test Route 5: Game page.
game_test_state = State(
    "Alex",
    0,
    create_board(list(range(MINE_COUNT))),
    "playing",
    "",
    ""
)

assert_has(game(game_test_state), "Score: 0")
assert_has(
    game(game_test_state),
    Button("[ ]", "choose_tile", [Argument("tile_index", 20)])
)


# Test Route 6: Selecting a safe tile increases the score.
safe_test_state = State(
    "Alex",
    0,
    create_board(list(range(MINE_COUNT))),
    "playing",
    "",
    ""
)

safe_page = choose_tile(safe_test_state, 20)

assert_equal(safe_page.state.score, 1)
assert_equal(safe_page.state.tiles[20].revealed, True)
assert_equal(safe_page.state.game_status, "playing")


# Test Route 6: Selecting an already revealed tile.
already_revealed_state = State(
    "Alex",
    1,
    create_board(list(range(MINE_COUNT))),
    "playing",
    "",
    ""
)

already_revealed_state.tiles[20].revealed = True

already_revealed_page = choose_tile(already_revealed_state, 20)

assert_equal(already_revealed_page.state.score, 1)


# Test Route 6: Selecting a mine ends the game.
mine_test_state = State(
    "Alex",
    0,
    create_board(list(range(MINE_COUNT))),
    "playing",
    "",
    ""
)

mine_page = choose_tile(mine_test_state, 0)

assert_equal(mine_page.state.game_status, "lost")
assert_equal(mine_page.state.score, 0)
assert_has(mine_page, "GAME OVER")


# Test Route 6: Invalid tile selection.
invalid_test_state = State(
    "Alex",
    0,
    create_board(list(range(MINE_COUNT))),
    "playing",
    "",
    ""
)

invalid_page = choose_tile(invalid_test_state, 100)

assert_equal(invalid_page.state.score, 0)
assert_equal(invalid_page.state.game_status, "playing")


# Test Route 7: Congratulations page.
winning_tiles = create_board(list(range(MINE_COUNT)))

for tile in winning_tiles:
    if not tile.has_mine:
        tile.revealed = True

winning_state = State(
    "Alex",
    SAFE_TILE_COUNT,
    winning_tiles,
    "won",
    "",
    ""
)

assert_has(congratulations(winning_state), "CONGRATULATIONS")
assert_has(congratulations(winning_state), "52 safe tiles")


# Test Route 8: Game over page.
losing_state = State(
    "Alex",
    10,
    create_board(list(range(MINE_COUNT))),
    "lost",
    "",
    ""
)

assert_has(game_over(losing_state), "GAME OVER")
assert_has(
    game_over(losing_state),
    Button("Play Again", "restart_game")
)


# Test Route 9: Feedback is saved.
feedback_state = State(
    "Alex",
    10,
    create_board(list(range(MINE_COUNT))),
    "lost",
    "",
    ""
)

feedback_page = submit_feedback(
    feedback_state,
    "I enjoyed the game!"
)

assert_equal(
    feedback_page.state.feedback,
    "I enjoyed the game!"
)


# Test Route 10: Restarting resets the score
# and creates a new board.
restart_state = State(
    "Alex",
    10,
    create_board(list(range(MINE_COUNT))),
    "lost",
    "",
    ""
)

restart_page = restart_game(restart_state)

assert_equal(restart_page.state.score, 0)
assert_equal(restart_page.state.game_status, "playing")
assert_equal(len(restart_page.state.tiles), 64)

assert_equal(
    sum(1 for tile in restart_page.state.tiles if tile.has_mine),
    12
)


# --------------------------------------------------
# START THE WEBSITE
# --------------------------------------------------

start_server(
    State("", 0, [], "not_started", "", "")
)

