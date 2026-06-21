"""
Tests for Bug3: the "Attempts left" count must update on the SAME submission,
not lag one guess behind.

Bug3 is a Streamlit state/render bug, not a pure-logic bug -- the arithmetic
`attempt_limit - attempts` was always correct, the defect was *when* it was
read. A plain unit test against logic_utils.py would therefore pass on both the
broken and the fixed code (a false green). The only honest way to verify the
fix is to drive the real app through its reruns, which is what streamlit's
AppTest does here.
"""
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_DIR = Path(__file__).resolve().parent.parent
# app.py does `from logic_utils import ...`; make that resolvable when AppTest
# executes the script.
sys.path.insert(0, str(APP_DIR))
APP = str(APP_DIR / "app.py")


def _start_hard():
    """Launch the app and switch to Hard difficulty (5 attempts, range 1-50)."""
    at = AppTest.from_file(APP).run()
    at.selectbox[0].set_value("Hard").run()
    return at


def test_attempts_left_decrements_on_each_submission():
    at = _start_hard()
    # Pin the secret to a value none of the guesses below match, so a random
    # secret can't turn a guess into a win and make this test flaky.
    at.session_state["secret"] = 7
    assert "Attempts left: 5" in at.info[0].value

    for n, guess in enumerate([50, 40, 30, 20, 10], start=1):
        at.text_input[0].set_value(str(guess))
        at.button[0].click().run()  # Submit
        # The count reflects THIS guess immediately -- no one-guess lag.
        assert at.session_state["attempts"] == n
        assert f"Attempts left: {5 - n}" in at.info[0].value

    # The game ends exactly when the count reaches 0 -- "Attempts left: 0" and
    # "Out of attempts!" now agree (this was the original contradiction).
    assert "Attempts left: 0" in at.info[0].value
    assert at.session_state["status"] == "lost"
    assert any("Out of attempts" in e.value for e in at.error)


def test_invalid_guess_does_not_consume_an_attempt():
    at = _start_hard()
    assert at.session_state["attempts"] == 0

    at.text_input[0].set_value("")  # blank submission
    at.button[0].click().run()      # Submit

    # Edge-case-proof fix: invalid input must not burn an attempt.
    assert at.session_state["attempts"] == 0
    assert "Attempts left: 5" in at.info[0].value
    assert any("Enter a guess" in e.value for e in at.error)
