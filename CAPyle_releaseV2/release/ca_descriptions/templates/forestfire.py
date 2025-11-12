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

def setup(args):
    """Set up the config object used to interact with the GUI"""
    config_path = args[0]
    config = utils.load(config_path)
    # -- THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED --
    config.title = "Forest Fire Simulation - Group 10"
    config.dimensions = 2

    # disabled wrapping
    # this prevents fire from looping from the bottom to the top
    config.wrap = False
    
    # state descriptions
    # 0: ash
    # 1: canyon (scrubland)
    # 2: chaparral
    # 3: dense forest
    # 4: water
    # 5: burning canyon 
    # 6: burning chaparral 
    # 7: burning forest 
    # 8: town
    config.states = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    
    # colours
    config.state_colors = [
        (0.4, 0.4, 0.4), # 0: ash (dark grey)
        (1, 1, 0),       # 1: canyon (yellow)
        (1, 0.6, 0),     # 2: chaparral (orange)
        (0, 0.4, 0),     # 3: forest (dark green)
        (0, 0.4, 1),     # 4: water (blue)
        (1, 0.2, 0),     # 5: burning canyon (bright red)
        (0.8, 0, 0),     # 6: burning chaparral (darker red)
        (0.5, 0, 0),     # 7: burning forest (dark red)
        (0, 0, 0),       # 8: town (black)
        (0, 0, 1),
        (0, 1, 0)
    ]
    
    # grid dimensions
    # 100 x 100 represents the 50km x 50km area with 0.5km per square km
    config.grid_dims = (100, 100)

    # ----------------------------------------------------------------------

    if len(args) == 2:
        config.save()
        sys.exit()
    return config


def transition_function(grid, neighbourstates, neighbourcounts):
    """Function to apply the transition rules and return the new grid"""
    
    # generate random probability number
    roll = np.random.random(grid.shape)
    
    # check for fire neighbour by adding all burning states
    burning_neighbour_count = neighbourcounts[5] + neighbourcounts[6] + neighbourcounts[7]
    has_burning_neighbour = burning_neighbour_count >= 1
    
    # ignition probabilities
    # canyon: 90% chance
    ignite_canyon = (grid == 1) & has_burning_neighbour & (roll < 0.9)
    
    # chaparral: 40% chance
    ignite_chaparral = (grid == 2) & has_burning_neighbour & (roll < 0.4)
    
    # forest: 10% chance
    ignite_forest = (grid == 3) & has_burning_neighbour & (roll < 0.1)


    # how long it burns
    # canyon: 1/5 = 0.2
    burnout_canyon = (grid == 5) & (roll < 0.2)
    
    # chaparral: 1/120 approx 0.0083
    burnout_chaparral = (grid == 6) & (roll < 0.0083)
    
    # forest: 1/720 approx 0.0014
    burnout_forest = (grid == 7) & (roll < 0.0014)


    # grid updates
    # form fuel to burning
    grid[ignite_canyon] = 5
    grid[ignite_chaparral] = 6
    grid[ignite_forest] = 7
    
    # from burning to burn out
    grid[burnout_canyon] = 0
    grid[burnout_chaparral] = 0
    grid[burnout_forest] = 0

    return grid

def generate_initial_grid(grid_dims):

    #power plant
    #grid[0, 10] = 9

    #proposed incinerator
    #grid[0, 100] = 10


    # background colour chaparral
    grid = np.full(grid_dims, 2, dtype=int)
    # grid [y, x] with y top = 0 and y bottom = 100

    # dense forest
    grid[10:70, 10:25] = 3
    grid[10:15, 25:40] = 3 # small top rectangle
    grid[50:70, 25:50] = 3 # bottom rectangle

    # canyon
    grid[20:65, 70:75] = 1

    # lakes
    grid[20:40, 35:40] = 4 # vertical lake
    grid[80:85, 50:80] = 4 # horizontal lake

    # fire
    grid[9, 10] = 6
    
    #town
    grid[88:93, 27:32] = 8
    return grid

def main():
    """ Main function that sets up, runs and saves CA"""
    config = setup(sys.argv[1:])
    grid = Grid2D(config, transition_function)
    grid.grid = generate_initial_grid(config.grid_dims)
    timeline = grid.run()
    config.save()
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
