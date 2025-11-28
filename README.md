# Modelling a Forest Fire using Cellular Automata - Team 10
This repository contains the code for Team 10's assignment, using Python to model a forest fire using Cellular Automata. The code simulates the spread of a forest fire across a landscape with varied terrains and assesses the risk of forest fire to a small town in the USA.

## Set Up
1. Make sure you have followed all of the steps in the [COM3524](https://github.com/ac1asana/COM3524) repository's `README.md` file. You need to have Docker and X Server running in the background.

2. Open a new PowerShell window and clone this repository:
```sh
git clone https://github.com/l1vvy318/BioInspired_Group10.git
```

## Running the file
1. Open another PowerShell window and cd into the `COM3524` directory. Enter the following command:
```sh
python run_tool.py
```
Select option 3.

2. Once the GUI opens, go to the top-left corner of the window and go to:
- File
- Open
- Navigate to the `BioInspired_Group10\CAPyle_releaseV2\release\ca_descriptions\templates\forestfire.py`
- The file should be named `forestfire.py`

3. Click on `Simulation`, located at the top-left corner of the window and press `Run Configuration`.


## Wind Implementation
To simulate wind in the model the following lines must be commented and uncommented.
1. Navigate to the function `def burn(grid, neighbourstates, neighbourcounts):`

2. Scroll to the comment section labelled `wind implementation`
-  Uncomment this section

3. Scroll to the comment section labelled `wind probability`
- Uncomment this section

4. Scroll to the comment section labelled `ignition probabilities`
- Comment out this section

5. Scroll to the comment section labelled `ignition probabilities including wind factor`
- Uncomment this section

From here, repeat the process above in the previous chapter, Running the file.

## Short-term Intervention Implementation
To simulate the short-term intervention in the model, uncomment the following lines:
1. Navigate to the function `transition_function(grid, neighbourstates, neighbourcounts):`

2. Scroll to the comment section labelled `dropping water aerially: short term intervention`
- Uncomment this section (lines 154-179)

From here, repeat the process above in the previous chapter, Running the file.

3. Likewise, to test the model without the intervention, comment the same section.

## Long-term Intervention Implementation
To simulate the long-term intervention in the model, uncomment the following lines:
1. Navigate to the function `generate_initial_grid(config):`

2. Scroll to the comment section labelled `extending the dense foreest: long term intervention`
- Uncomment all code under the labels:
  - `around the town`
  - `around the incinerator`
  - `around the power plant`

From here, repeat the process above in the previous chapter, Running the file.

3. Likewise, to test the model without the intervention, comment the same sections of code.

## Code Explanations
Our CA model uses 14 distinct states to represent the map:
- State 0: Ash (Burnt out land)
- State 1: Canyon
- State 2: Chaparral
- State 3: Dense forest
- State 4: Water
- State 5: Burning canyon
- State 6: Burning chaparral
- State 7: Burning forest
- State 8: Town
- State 9: Power plant
- State 10: Incinerator
- State 11: Canyon ash
- State 12: Chaparal ash
- State 13: Forest ash

We modelled the burning duration for each type of terrain. 
- Canyon (burns for several hours): takes 12 time steps to turn into ash (P = 1/12)
- Chapparral (burns for several days): takes 120 time steps to turn into ash (P = 1/120)
- Dense forest (burns for up to a month): takes 720 time steps to turn into ash (P = 1/720)