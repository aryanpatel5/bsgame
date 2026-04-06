# BINARY SEARCH GAME
I chose binary search and this version of a game alongside it because I personally became victim to memorizing bits code instead of grasping a genuine undertanding of the idea. Jumping straight into asking the user how many steps are required in the list to reach the target essentially forces them to run the whole search in their head with the generated set on the screen as a guide.

## Decomposition
1) select a value for the amount of digits you would like in the list via a slider
- Confirm the amount of values
2) pick a preset number set of values (evenly spaced, primes or perfect squares)
- if evenly spaced is selected, add a list customizer that allows users to choose start number and step value
- generate the set and display the indexes and values
- user clicks start game or Reset to back to step 1
3) a random target value is selected. 
- Binary search is run on the list to find the target to identify the total number of steps needed and the relative `low`, `high`, `mid`,’result’ values for each step
4) user guesses as to how many steps are required to reach the random target selected for the list if binary search is applied
5) check if the user is correct.
- if incorrect, prompt with 2 more tries, if the user does not get the answer within 3 total tries; display the step-by-step simulation trace of binary searching the target in the generated list 
- If the user gets the answer correct within the 3 tries; display the step-by-step simulation trace of binary searching the target in the generated list 
6) after 3 tries or a correct answer, a restart game button appears and the users score is updated. A loss is minus 1 point, a win is plus 1. 
## Pattern Recognition
- Each iteration of the binary search checks the middle element and discards half the range.
- If `mid_value < target`, move right (`low = mid + 1`).
- If `mid_value > target`, move left (`high = mid - 1`).
- Stop when `mid_value == target` (`FOUND`).
## Abstraction
- The app guarantees a sorted input via presets, so users can focus on the search behavior 
- It exposes only the key state per step (`low/high/mid`) instead of the indexs to emphasize on the concept and not the math.
- The game mechanic reduces the learning goal to one question: "How many steps will it take?"
## Algorithm Design (Input - Processing -Output)
- **Input:** set size of list, preset(and `start/step` for evenly spaced), user guess
- **Processing:** generate list, select random target, compute actual steps + trace
- **Output:** target value, correct/incorrect feedback, a trace table 

### test cases and demo

test case 1
  - Steps: Preset=`evenly_spaced`, List size=`5`, Start=`3`, Step=`2`, click `Generate Set`.
  - Check: List table shows `(index,value)` = `(0,3) (1,5) (2,7) (3,9) (4,11)`.

![photo](images/image(10).png)

test case 2
  - Steps: Preset=`evenly_spaced`, Step=`0` (or `-1`), click `Generate Set`.
  - Check: Error

![photo](images/image(11).png)

test case 3
  - Steps: Preset=`primes`, List size=`10`, click `Generate Set`.
  - Check: Values are `2, 3, 5, 7, 11, 13, 17, 19, 23, 29` 

![photo](images/image(12).png)

test case 4
  - Steps: Preset=`perfect_squares`, List size=`6`, click `Generate Set`.
  - Check: Values are `1, 4, 9, 16, 25, 36`.

![photo](images/image(13).png)

test case 5: update score on loss
  - Steps: Click `Start Game`, then submit an incorrect guess 3 times 
  - Check: status says incorrect Trace table becomes visible, `Restart Game` button appears, Guess/Submit disable, Score decreases by `1`.

![photo](images/image(14).png)

test case 6: update score on win
  - Steps: Click `Start Game`, then when correct answer is given by user
  Check: Status says correct, Trace is visible, Score increases by `1`, `Restart Game` button appears, Guess/Submit disable

![photo](images/image(15).png)

#### Steps to Run
1) Create and activate a virtual environment:
   - Windows (PowerShell): `python -m venv .venv` then 
   `.venv\Scripts\Activate.ps1`
   - macOS/Linux: `python -m venv .venv` then 
   `source .venv/bin/activate`
2) Install dependencies: `pip install -r requirements.txt`
3) Run the app: `python app.py`
4) Open the local Gradio URL printed in the terminal.

##### Hugging Face Link
- Deployed app : https://huggingface.co/spaces/ap555/bsapp

###### Author 
- Aryan Patel
- 20471645
