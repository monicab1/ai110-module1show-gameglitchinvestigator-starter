# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
When I first ran the game, the very first thing that stood out to me as 'broken' when I first started it defaults to Normal difficulty. In the left panel, it shows 'attempts allowed: 8'. However, glancing to the right, the screen shows 'attempts left: 7'. I expected attempts left and attempts allowed to match at the start of a game.

- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

  Bug1: (the secret number was out of range)
  One concrete bug I observed was, since the game started on 'Normal' difficulty. I selected 'Easy' difficulty and chose new game. The range for easy is 1-20; therefore, I expected the Developer Debug secret number to fall in the specified range of 1-20; however the updated secret number for 'Easy' was 93, which is out of the stated range.
  Cause in code: the "New Game" handler in app.py hardcoded `random.randint(1, 100)` instead of drawing from the selected difficulty's (low, high) range.

  Bug2: (the hints are incorrect)
  The secret number was 46, I made a guess of 4. The hint told me to go lower. I expected the hint to instruct me to go higher.
  Cause in code: `check_guess` in logic_utils.py paired each outcome with the opposite direction message (a too-low guess said "Go LOWER" instead of "Go HIGHER").

  Bug3: (message attempts left does not update with guess submission)
  On hard difficulty you are allowed 5 attempts. I entered 50,40,30,20,10. Below the hint message box, I was shown the message 'Out of attempts!' However, my attempts left showed 1, even though the game was over. I expected that if I was allowed 5 attempts, after submitting my first guess, the attempts left would be one less but the decrement does not occur until I make another guess after that.
  Cause in code: in `app.py` the "Attempts left" message (`attempt_limit - st.session_state.attempts`) is drawn near the top of the script, but `st.session_state.attempts` is not incremented until the Submit handler runs further down, and the script never re-runs after that increment. As a result the displayed count always reflected the state from *before* the current guess, so it lagged one submission behind. The fix moves the increment into the valid-guess branch of the Submit handler and calls `st.rerun()` afterward, so the display redraws from the updated count.

  BugX: observational not operational
  Not sure if this can count as a bug since it does not affect the functionality of the app but impacts the user experience.
  Easy difficulty is built with a range of 1-20; however there is a hardcoded message in the center of the screen that says, 'Guess a number between 1 and 100', which is clearly an incorrect instruction for the given range.

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
|Easy Difficulty range:1-20 |secret number within range: 1-20 |secret number received: 93 | the secret number provided was outside the range of 1-20|
|my guess: 4 secret number: 46|'go higher' hint | 'go lower' hint shown | the hint output did not match the result of the comparison for my guess vs the secret number Go LOWER!|
| an attempt is made| attempts left is reduced by one|attempts left remained the same | the attempts left does not change until the second attempt after you start|

---

## 2. How did you use AI as a teammate?


- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?


- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).


- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?


- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.

- What is one thing you would do differently next time you work with AI on a coding task?


- In one or two sentences, describe how this project changed the way you think about AI generated code.
