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
The assignment required us to make git commits, and I wanted to see all of those changes show up in my own GitHub account. I had never forked a project before, so I thought I had set it up correctly. But once I was ready to start committing, Claude pointed out that my project in VS Code was not actually connected to my GitHub account the way I wanted it to be. Even though I had already started working in VS Code, Claude took the lead and walked me through fixing the connection. That way I was properly set up to track my work going forward.

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
I used Claude: Sonnet and Claude Opus 4.8


- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).

The AI correctly diagnosed that the "Guess a number between 1 and 100" banner was wrong because the bounds were hardcoded as literal text instead of being pulled from the low/high variables that get_range_for_difficulty already produces. It suggested replacing the line with f"Guess a number between {low} and {high}." so the message would always match the active difficulty (Easy 1–20, Hard 1–50). I verified the fix two ways: the AI wrote ast-based regression tests in tests/test_game_logic.py asserting the banner no longer contains "1 and 100" and that it interpolates low and high, and the full suite passed (13/13). This confirmed the displayed range now tracks the real game range rather than a static, incorrect number.

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

One AI suggestion that turned out to be misleading was about my third bug, the one where the "attempts left" count didn't go down right away. The AI told me the cause was that the attempts counter started at 1 instead of 0, and that this was why the number looked off. I verified this by changing the starting value to 0 and playing the game again — it fixed the very first screen (attempts allowed and attempts left finally matched at the start), but the real problem was still there. When I played on Hard and used all 5 guesses, the screen still said "Out of attempts!" while showing 1 attempt left, so the fix hadn't actually solved Bug3. That showed me the AI had explained the wrong cause: the count was really lagging because the screen showed the number before my guess was counted, not because of the starting value.


---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?

1. I evaluated the results of the tests. I made sure I saw PASSED results.
2. I used the diff tool to compare the before and after changes in the code to manually inspect/debug to determine whether the bug was fixed.
3. I re-ran the game to view the change(s) in real time to verify the correct expected behavior occurred

- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
The main test I ran was a manual one. On Hard difficulty I get 5 attempts, so I entered 50, 40, 30, 20, and 10 one at a time and watched the "attempts left" number after each guess. Before the fix, the count lagged behind — it still said "1 left" at the same moment the game showed "Out of attempts!", which didn't make sense. After the fix, I replayed the exact same five guesses and the count dropped correctly each time, landing on 0 right when the game ended. This showed me the display was finally reading the count after my guess was counted, instead of before it.


- Did AI help you design or understand any tests? How?

Yes, AI helped a lot on the testing side. At first I assumed a normal pytest checking the math would prove my fix, but the AI pointed out that kind of test would pass on both the broken and the fixed code, so it wouldn't actually catch the bug. It explained that my bug lived in how the screen updated, not in a simple calculation, so a real test had to run the app and click through the guesses like I did. With that in mind, the AI helped design an automated test that plays the game the same way and checks the count after each guess. That taught me to ask whether a test can actually fail before I trust that it passed.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.

- What is one thing you would do differently next time you work with AI on a coding task?


- In one or two sentences, describe how this project changed the way you think about AI generated code.
