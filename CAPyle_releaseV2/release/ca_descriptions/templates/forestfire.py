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
global fuel
fuel = None

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
    
    config.states = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    
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
        (0, 0, 0)          # 10: incinerator (black)
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
        np.random.normal(6, 1.2, np.sum(mask)),
        1, 12
    )

    # chaparral
    mask = (grid == 2)
    fuel[mask] = np.clip(
        np.random.normal(72, 14.4, np.sum(mask)),
        24, 120
    )

    # forest
    mask = (grid == 3)
    fuel[mask] = np.clip(
        np.random.normal(444, 88.8, np.sum(mask)),
        168, 720
    )

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
    # config.initial_grid[81:87, 26:33] = 3
    # config.initial_grid[81:93, 33:39] = 3
    # config.initial_grid[81:93, 20:26] = 3

    # dropping water aerially: short term intervention
    # config.initial_grid[84:86, 15:40] = 4 # 2 x 25 strip of water (wide, thin)
    # config.initial_grid[81:86, 24:34] = 4 # 5 x 10 strip of water (narrow, thick)

    return config

def transition_function(grid, neighbourstates, neighbourcounts):
    global fuel
    """Function to apply the transition rules and return the new grid"""
    
    # generate random probability number
    roll = np.random.random(grid.shape)
    
    # check for fire neighbour by adding all burning states
    burning_neighbour_count = neighbourcounts[5] + neighbourcounts[6] + neighbourcounts[7]
    has_burning_neighbour = burning_neighbour_count >= 1
    
    # ignition probabilities
    ignite_canyon = (grid == 1) & has_burning_neighbour & (roll < 0.9)  #canyon 90%
    ignite_chaparral = (grid == 2) & has_burning_neighbour & (roll < 0.4)  #chaparral %40
    ignite_forest = (grid == 3) & has_burning_neighbour & (roll < 0.1)  #forest %10

    # Set on Fire
    grid[ignite_canyon] = 5
    grid[ignite_chaparral] = 6
    grid[ignite_forest] = 7

    # Burning mask
    burning = (grid == 5) | (grid == 6) | (grid == 7)

    # Consumption
    fuel[burning] -= 1
    fuel[fuel < 0] = 0

    # cells that have burned all fuel → turn into empty (0)
    burn_out = burning & (fuel <= 0)
    grid[burn_out] = 0

    return grid

    # #burnout probabilities
    # canyon_burn_duration = (grid == 5) & (roll < 0.0833) # canyon: 1/12 = 0.0833
    # chaparral_burn_duration = (grid == 6) & (roll < 0.0083) # chaparral: 1/120 approx 0.0083
    # forest_burn_duration = (grid == 7) & (roll < 0.0014) # forest: 1/720 approx 0.0014
    
    # # from burning to burn out
    # grid[canyon_burn_duration] = 0
    # grid[chaparral_burn_duration] = 0
    # grid[forest_burn_duration] = 0

    #return grid

def main():
    """ Main function that sets up, runs and saves CA"""
    config = setup(sys.argv[1:])
    grid = Grid2D(config, transition_function)
    timeline = grid.run()
    config.save()
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
