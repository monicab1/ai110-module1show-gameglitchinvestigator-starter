import random
import streamlit as st

from logic_utils import (
    get_range_for_difficulty,
    get_attempt_limit,
    parse_guess,
    check_guess,
    update_score,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit = get_attempt_limit(difficulty)

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# FIXME: Logic breaks here
# FIX: corrected logic by adding OR st.session_state.get("secret_difficulty") != difficulty
# FIX: corrected secret number logic to use variable value difficulty
if "secret" not in st.session_state or st.session_state.get("secret_difficulty") != difficulty:
    st.session_state.secret = random.randint(low, high)
    st.session_state.secret_difficulty = difficulty

# FIXME: Logic breaks here
# FIX: corrected on startup, attempts left initialization value
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

# session_state buffer: feedback produced during a submit is stashed here so it
# survives the st.rerun() below (drawing it inline would be erased on re-execution)
if "messages" not in st.session_state:
    st.session_state.messages = []

if "celebrate" not in st.session_state:
    st.session_state.celebrate = False

st.subheader("Make a guess")

st.info(
    # FIXME: Logic breaks here - incorrect hardcoded message
    # FIX: replaced hardcoded "1 and 100" with the {low}/{high} variables so the message matches the actual difficulty range
    f"Guess a number between {low} and {high}. "
    # FIXME: Logic breaks here
    # FIX: count now reflects the post-guess state because the submit handler increments attempts then calls st.rerun(), so this redraws from the fresh value instead of the stale pre-guess one
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

# FIXME: Logic breaks here
# FIX: added logic to set the secret number based on the difficulty
if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.secret_difficulty = difficulty
    # FIXME: Logic breaks here
    # FIX: reset status to "playing" (and clear stashed feedback) so a finished game can actually be replayed; the old code left status as "won"/"lost", so the game-over guard kept stopping the new game
    st.session_state.status = "playing"
    st.session_state.celebrate = False
    st.session_state.messages = [("success", "New game started.")]
    st.rerun()

# FIXME: Logic breaks here
# FIX: render feedback stashed by the previous run's submit BEFORE the game-over guard, so the detailed win / "Out of attempts!" text (and balloons) survive st.rerun() instead of being replaced by the generic game-over message
for kind, text in st.session_state.messages:
    getattr(st, kind)(text)
if st.session_state.celebrate:
    st.balloons()
    st.session_state.celebrate = False
just_finished = bool(st.session_state.messages)
st.session_state.messages = []

if st.session_state.status != "playing":
    # show the generic reminder only on later runs, not on the run that just ended the game
    if not just_finished:
        if st.session_state.status == "won":
            st.success("You already won. Start a new game to play again.")
        else:
            st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        # FIXME: Logic breaks here
        # FIX: stash the error instead of incrementing attempts here, so a blank/non-numeric guess no longer burns an attempt
        st.session_state.messages = [("error", err)]
    else:
        # FIXME: Logic breaks here
        # FIX: increment moved into the valid-guess branch (it used to run at the top of the handler, after the display had already rendered and before input was validated), so only real guesses count and the count is fresh on the next run
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        # FIX: always use the number secret (it was turned into text on even turns, which broke the compare)
        secret = st.session_state.secret

        outcome, message = check_guess(guess_int, secret)

        msgs = []
        if show_hint:
            msgs.append(("warning", message))

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.session_state.status = "won"
            st.session_state.celebrate = True
            msgs.append((
                "success",
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}",
            ))
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                msgs.append((
                    "error",
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}",
                ))

        st.session_state.messages = msgs

    # FIXME: Logic breaks here
    # FIX: re-run after processing so the whole script re-executes against the updated session_state; "Attempts left" above now redraws from the fresh count (this is what removes the off-by-one lag)
    st.rerun()

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
