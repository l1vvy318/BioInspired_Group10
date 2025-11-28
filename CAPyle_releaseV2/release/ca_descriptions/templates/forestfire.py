# Name: Forest Fire Simulation - Group 10
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, randomise2d
import capyle.utils as utils
import numpy as np
global regrowing
regrowing = False
global fuel
fuel = None
global count
count = 0

def setup(args):
    global fuel

    """Set up the config object used to interact with the GUI"""
    config_path = args[0]
    config = utils.load(config_path)
    # -- THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED --
    config.title = "Forest Fire Simulation - Group 10"
    config.dimensions = 2

    # disabled wrapping
    # this prevents fire from looping from the bottom to the top
    config.wrap = False
    
    config.states = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)
    
    # colours
    config.state_colors = [
        (0.4, 0.4, 0.4),   # 0: ash (dark grey)
        (1, 1, 0),         # 1: canyon (yellow)
        (0.6, 0.65, 0.19), # 2: chaparral (olive green)
        (0.27, 0.29, 0.2), # 3: forest (dark green)
        (0.2, 0.7, 0.9),   # 4: water (blue)
        (0.75, 0, 0),      # 5: burning canyon (crimson red)
        (0.86, 0.08, 0.23),# 6: burning chaparral (apple red)
        (0.44, 0.18, 0.22),# 7: burning forest (dark red)
        (0, 0, 0),         # 8: town (black)
        (0, 0, 0),         # 9: power plant (black)
        (0, 0, 0),         # 10: incinerator (black)
        (0.5, 0.5, 0.5),   # 11: canyon ash
        (0.4, 0.4, 0.4),   # 12: chaparral ash
        (0.3, 0.3, 0.3)    # 13: forest ash
    ]

    config = generate_initial_grid(config)
    fuel = create_fuel_grid(config)
    # ----------------------------------------------------------------------

    if len(args) == 2:
        config.save()
        sys.exit()

    return config

def create_fuel_grid(config):
    grid = config.initial_grid
    fuel = np.zeros_like(grid, dtype=float)

    # canyon
    mask = (grid == 1)
    fuel[mask] = np.clip(
        np.random.normal(6, 1.5, np.sum(mask)),
        1, 12
    )

    # chaparral
    mask = (grid == 2)
    fuel[mask] = np.clip(
        np.random.normal(72, 18, np.sum(mask)),
        24, 120
    )

    # forest
    mask = (grid == 3)
    fuel[mask] = np.clip(
        np.random.normal(444, 111, np.sum(mask)),
        168, 720
    )

    # power plant
    mask = (grid == 6)
    fuel[mask] = 100

    return fuel

def generate_initial_grid(config):

    # 100 x 100 represents the 50km x 50km area with 0.5km per square km
    config.grid_dims = (100, 100)
    # chaparral 
    config.initial_grid = np.full(config.grid_dims, 2, dtype=int) 
    # dense forest
    config.initial_grid[10:70, 10:25] = 3 # main left part
    config.initial_grid[10:15, 25:40] = 3 # small top rectangle
    config.initial_grid[50:70, 25:50] = 3 # bottom rectangle
    # canyon
    config.initial_grid[20:65, 70:75] = 1
    # lakes
    config.initial_grid[20:40, 35:40] = 4 # vertical lake
    config.initial_grid[80:85, 50:80] = 4 # horizontal lake
    # town
    config.initial_grid[88:93, 27:32] = 8
    # power plant
    config.initial_grid[0, 10] = 9
    # proposed incinerator
    config.initial_grid[0, 99] = 10
    # start the fire at the power plant
    config.initial_grid[0, 10] = 6

    # start the fire at the incinerator
    # config.initial_grid[0, 99] = 6

    # extending the dense foreest: long term intervention
    # around the town
    # config.initial_grid[81:87, 26:33] = 3
    # config.initial_grid[81:93, 33:39] = 3
    # config.initial_grid[81:93, 20:26] = 3

    # around the incinerator
    # config.initial_grid[0:10, 90:95] = 3
    # config.initial_grid[5:10, 95:100] = 3

    # around the power plant
    # config.initial_grid[0:5, 4:8] = 3
    # config.initial_grid[2:5, 7:13] = 3
    # config.initial_grid[0:5, 13:17] = 3

    return config

def transition_function(grid, neighbourstates, neighbourcounts):
    """Function to apply the transition rules and return the new grid"""
    global fuel
    global regrowing
    global count

    # dropping water aerially: short term intervention
    count += 1 # keeping track of the time to drop water
    water_drop_time = 80 # testing with 100 time steps
    
    if count >= water_drop_time:
        burning_left_of_forest = grid[68:70, 0:10]
        burning_right_of_forest = grid[67:70, 50:60]

        # checking if any cells are burning to the left of the forest
        canyon_burning_left = (burning_left_of_forest == 5)
        chapparral_burning_left = (burning_left_of_forest == 6)
        forest_burning_left = (burning_left_of_forest == 7)
        burning_cells_left = (canyon_burning_left | chapparral_burning_left | forest_burning_left)  
        
        # checking if any cells are burning to the right of the forest
        canyon_burning_right = (burning_right_of_forest == 5)
        chapparral_burning_right = (burning_right_of_forest == 6)
        forest_burning_right = (burning_right_of_forest == 7)
        burning_cells_right = (canyon_burning_right | chapparral_burning_right | forest_burning_right)

        # set the states of burning cells in target area to water
        burning_left_of_forest[burning_cells_left] = 4 
        burning_right_of_forest[burning_cells_right] = 4

        # updating the grid with the new states in selected positions
        grid[68:70, 0:10] = burning_left_of_forest
        grid[67:70, 50:60] = burning_right_of_forest

    # check if burning has stopped then begin regrowing
    burning_states = (5,6,7)
    if not np.any(np.isin(grid, burning_states)):
        regrowing = True

    # if not regrowing -> burn
    if regrowing == False:
        grid = burn(grid, neighbourstates, neighbourcounts)
    else: # regrow
        grid = regrow(grid, neighbourstates, neighbourcounts)

    return grid

def burn(grid, neighbourstates, neighbourcounts):
    roll = np.random.random(grid.shape) # generate random probability number
    
    # check for fire neighbour by adding all burning states
    burning_neighbour_count = neighbourcounts[5] + neighbourcounts[6] + neighbourcounts[7]
    has_burning_neighbour = burning_neighbour_count >= 1
    

    # ##UNCOMMENT BELOW TO ACTIVATE CA MODEL WITH WIND
    # # wind implementation
    # # values for wind direction: 0=NW, 1=N, 2=NE, 3=W, 4=E, 5=SW, 6=S, 7=SE
    # burning_from_north  = neighbourstates[1]   # upwind  – resists spread of fire
    # burning_from_south  = neighbourstates[6]   # downwind – helps spread of fire
    # burning_from_sides  = neighbourstates[0] + neighbourstates[2] + neighbourstates[3] + \
    #                       neighbourstates[4] + neighbourstates[5] + neighbourstates[7]

    # # Wind probability - ALSO UNCOMMENT BELOW TO ACTIVATE CA MODEL WITH WIND
    # wind_factor = 0.2
    # wind_factor += 0.4 * burning_from_south      # strong boost from downwind
    # wind_factor += 0.05 * burning_from_sides       # mild boost from sides/boundaries
    # wind_factor -= 0.3 * burning_from_north       # resist spread from upwind
    # wind_factor = np.clip(wind_factor, 0.7, 1.6)   # keep it gentle and bounded

    # ignition probabilities 
    ignite_canyon = (grid == 1) & has_burning_neighbour & (roll < 0.9)  #canyon 90%
    ignite_chaparral = (grid == 2) & has_burning_neighbour & (roll < 0.4)  #chaparral %40
    ignite_forest = (grid == 3) & has_burning_neighbour & (roll < 0.1)  #forest %10

    # ##UNCOMMENT BELOW TO ACTIVATE CA Model with wind and COMMENT 3 LINES ABOVE (ignition probabilities)
    # # ignition probabilities including wind factor
    # ignite_canyon = (grid == 1) & has_burning_neighbour & (roll < 0.9 * wind_factor)  #canyon 90%
    # ignite_chaparral = (grid == 2) & has_burning_neighbour & (roll < 0.4 * wind_factor)  #chaparral %40
    # ignite_forest = (grid == 3) & has_burning_neighbour & (roll < 0.1 * wind_factor)  #forest %10

    # Set on Fire
    grid[ignite_canyon] = 5
    grid[ignite_chaparral] = 6
    grid[ignite_forest] = 7

    # Burning masks
    burning_canyon = (grid == 5)
    burning_chaparral = (grid == 6)
    burning_forest = (grid == 7)
    burning = burning_canyon | burning_chaparral | burning_forest 

    # Consumption
    fuel[burning] -= 1
    fuel[fuel < 0] = 0

    # cells that have burned all fuel → turn into empty (0)
    burn_out = burning & (fuel <= 0)

    grid[burn_out & burning_canyon] = 11
    grid[burn_out & burning_chaparral] = 12
    grid[burn_out & burning_forest] = 13

    return grid

def regrow(grid, neighbourstates, neighbourcounts):
    roll = np.random.random(grid.shape)
    # Mask for ash or empty land
    ash_mask = np.isin(grid, [0, 11, 12, 13])

    # --- 1. Spontaneous sprouting based on ash type ---
    # Where each type of vegetation used to be
    canyon_ash = grid == 11
    chap_ash = grid == 12
    # Probabilities for spontaneous return
    sprout_canyon = canyon_ash & (roll < 0.02)
    sprout_chaparral = chap_ash & (roll < 0.0001)
    # Apply spontaneous growth
    grid[sprout_canyon] = 1
    grid[sprout_chaparral] = 2
    # --- 2. Spreading from neighbours ---
    has_canyon_neighbour = neighbourcounts[1] >= 1
    has_chaparral_neighbour = neighbourcounts[2] >= 1
    grow_canyon = ash_mask & has_canyon_neighbour & (roll < 0.01)
    grow_chaparral = ash_mask & has_chaparral_neighbour & (roll < 0.002)
    # Spread vegetation
    grid[grow_canyon] = 1
    grid[grow_chaparral] = 2

    return grid

def main():
    """ Main function that sets up, runs and saves CA"""
    config = setup(sys.argv[1:])
    grid = Grid2D(config, transition_function)
    timeline = grid.run()
    config.save()
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
