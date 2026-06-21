import ast
import os

from logic_utils import check_guess

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win.
    # check_guess returns a (outcome, message) pair, so we read the outcome.
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, the outcome should be "Too High"
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, the outcome should be "Too Low"
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"


# ---------------------------------------------------------------------------
# Regression test for the startup "Attempts left" glitch.
#
# The bug: app.py initialized `st.session_state.attempts = 1` on a fresh game,
# so the display (attempt_limit - attempts) showed one fewer than it should
# (e.g. "Attempts left: 7" for a Normal game whose limit is 8).
#
# The attempts counter is set up in module-level Streamlit code, and importing
# app.py would try to launch Streamlit. So instead of importing it, we read the
# source and inspect the initializer directly with the `ast` module. This makes
# the test target the exact line that was fixed, with no Streamlit runtime.
# ---------------------------------------------------------------------------

APP_PATH = os.path.join(os.path.dirname(__file__), "..", "app.py")


def _initial_attempts_value():
    """Return the constant `attempts` is initialized to inside the
    `if "attempts" not in st.session_state:` guard in app.py."""
    with open(APP_PATH, encoding="utf-8") as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        # Match the guard:  if "attempts" not in st.session_state:
        if (
            isinstance(test, ast.Compare)
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.NotIn)
            and isinstance(test.left, ast.Constant)
            and test.left.value == "attempts"
        ):
            # Find:  st.session_state.attempts = <constant>
            for stmt in node.body:
                if (
                    isinstance(stmt, ast.Assign)
                    and isinstance(stmt.targets[0], ast.Attribute)
                    and stmt.targets[0].attr == "attempts"
                    and isinstance(stmt.value, ast.Constant)
                ):
                    return stmt.value.value

    raise AssertionError(
        'Could not find the `if "attempts" not in st.session_state:` '
        "initializer in app.py"
    )


def test_fresh_game_initializes_attempts_to_zero():
    # A brand-new game must start with 0 attempts used. The glitch set this to
    # 1, which is what made the startup counter read one too low.
    assert _initial_attempts_value() == 0


def test_fresh_normal_game_shows_full_attempts_left():
    # "Attempts left" is attempt_limit - attempts. For a fresh Normal game
    # (limit 8) a correct start shows all 8 remaining; the bug produced 7.
    NORMAL_ATTEMPT_LIMIT = 8
    attempts_left = NORMAL_ATTEMPT_LIMIT - _initial_attempts_value()
    assert attempts_left == NORMAL_ATTEMPT_LIMIT


# ---------------------------------------------------------------------------
# Regression test for the "secret out of range for the selected difficulty"
# glitch.
#
# The bug had two sources in app.py:
#   1. The secret was generated only once at startup, so changing difficulty
#      never re-drew it inside the new range.
#   2. The "New Game" handler hardcoded `random.randint(1, 100)` instead of
#      using the difficulty's (low, high) range, so a new game on Easy (1-20)
#      or Hard (1-50) could produce an out-of-range secret.
#
# The fix makes every `st.session_state.secret = random.randint(...)` draw
# from the `low`/`high` variables. As before, we inspect the source with `ast`
# rather than importing app.py (which would launch Streamlit).
# ---------------------------------------------------------------------------


def _secret_randint_arg_names():
    """Return a list of arg-name pairs for every
    `st.session_state.secret = random.randint(<a>, <b>)` assignment in app.py.

    Each element is a tuple like ("low", "high") for name args, or the literal
    constant (e.g. 1, 100) when the argument is a hardcoded number.
    """
    with open(APP_PATH, encoding="utf-8") as f:
        tree = ast.parse(f.read())

    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        target = node.targets[0]
        # Match:  st.session_state.secret = ...
        if not (isinstance(target, ast.Attribute) and target.attr == "secret"):
            continue
        call = node.value
        # Match the right-hand side:  random.randint(<a>, <b>)
        if (
            isinstance(call, ast.Call)
            and isinstance(call.func, ast.Attribute)
            and call.func.attr == "randint"
            and len(call.args) == 2
        ):
            args = []
            for arg in call.args:
                if isinstance(arg, ast.Name):
                    args.append(arg.id)
                elif isinstance(arg, ast.Constant):
                    args.append(arg.value)
                else:
                    args.append(None)
            found.append(tuple(args))

    return found


def test_secret_is_always_drawn_from_difficulty_range():
    # Every secret assignment must use the (low, high) range variables, never a
    # hardcoded numeric literal like the old `random.randint(1, 100)`.
    assignments = _secret_randint_arg_names()
    assert assignments, "No `st.session_state.secret = random.randint(...)` found in app.py"

    for args in assignments:
        assert args == ("low", "high"), (
            f"secret should be drawn from (low, high); found random.randint{args}"
        )


# ---------------------------------------------------------------------------
# Regression test for the "hint points the wrong way" glitch.
#
# The bug: check_guess paired each outcome with the WRONG direction message.
# A guess that was too high said "Go HIGHER!" and a guess that was too low said
# "Go LOWER!" -- the exact opposite of what the player should do. On even
# attempts the secret also arrived as a string ("50"), which made the numbers
# compare alphabetically instead of by value.
#
# These tests confirm the hint now matches the comparison.
# ---------------------------------------------------------------------------


def test_too_high_guess_tells_player_to_go_lower():
    outcome, message = check_guess(60, 50)  # 60 is higher than 50
    assert outcome == "Too High"
    assert "LOWER" in message.upper(), f"a too-high guess should say LOWER, got: {message}"


def test_too_low_guess_tells_player_to_go_higher():
    outcome, message = check_guess(40, 50)  # 40 is lower than 50
    assert outcome == "Too Low"
    assert "HIGHER" in message.upper(), f"a too-low guess should say HIGHER, got: {message}"


def test_hint_is_correct_even_when_secret_is_a_string():
    # Reproduces the even-attempt path where the secret came in as a string.
    # 9 is less than 10, so the player should be told to go HIGHER.
    outcome, message = check_guess(9, "10")
    assert outcome == "Too Low"
    assert "HIGHER" in message.upper(), f"9 vs 10 should say HIGHER, got: {message}"
