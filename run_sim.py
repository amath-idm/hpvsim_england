'''
Define the HPVsim simulations for England, which is used as
the basis for the calibration and scenarios.

'''

# Standard imports
import numpy as np
import sciris as sc
import hpvsim as hpv

# Imports from this repository
import pars_data as dp


#%% Settings and filepaths

# Debug switch
debug = 1 # Run with smaller population sizes and in serial
do_shrink = True # Do not keep people when running sims (saves memory)

# Save settings
do_save = False
save_plots = True


#%% Simulation creation functions
def make_sim(calib=False, debug=0, screen_intvs=None, end=None, seed=0):
    ''' Define parameters, analyzers, and interventions for the simulation '''

    if end is None:
        end = 2060
    if calib:
        end = 2020

    # Parameters
    pars = dict(
        n_agents       = [50e3,1e3][debug],
        dt             = [0.25,1.0][debug],
        start          = [1950,1980][debug],
        end            = end,
        network        = 'default',
        location       = 'united kingdom',
        debut          = dp.debut,
        mixing         = dp.mixing,
        layer_probs    = dp.layer_probs,
        genotypes      = [16, 18, 'hrhpv'],
        ms_agent_ratio = 100,
        verbose        = 0.0,
    )

    # Analyzers
    analyzers = sc.autolist()
    interventions = sc.autolist()
    if not calib:
        analyzers += hpv.age_pyramid(
            timepoints=['1990', '2000', '2010', '2020'],
            datafile=f'data/england_age_pyramid.csv',
            edges=np.linspace(0, 100, 21)
        )
        interventions += screen_intvs

    sim = hpv.Sim(pars=pars, analyzers=analyzers, interventions=interventions, rand_seed=seed)
    return sim



#%% Simulation running functions

def run_sim(calib=False, debug=0, screen_intvs=None, end=None, seed=0,
            use_calib_pars=False, verbose=0.1, do_save=False):

    ''' Assemble the parts into a complete sim and run it '''

    sim = make_sim(calib=calib, debug=debug, screen_intvs=screen_intvs, end=end, seed=seed)

    # Make any parameter updates
    if use_calib_pars:
        file = f'results/england_pars.obj'
        try:
            calib_pars = sc.loadobj(file)
        except:
            errormsg = 'Calibration parameters cannot be loaded from disk. Try running load_calib to generate them.'
            raise ValueError(errormsg)

        sim.initialize() # Important to do this here, otherwise the genotype pars get overwritten
        sim.update_pars(calib_pars)

    # Run
    sim['verbose'] = verbose
    sim.run()
    sim.shrink()
        
    if do_save:
        sim.save(f'results/england.sim')
    
    return sim



#%% Run as a script
if __name__ == '__main__':

    T = sc.timer()
    
    # Run a single sim
    sim = run_sim(use_calib_pars=False, end=2020)
    
    T.toc('Done')

