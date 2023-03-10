'''
Calibrate HPVsim to England

To change whether the calibration is run/plotted, comment out the lines in the
"to_run" list below.

Note that running with debug=False requires an HPC and MySQL to be configured.
With debug=True, should take 5-10 min to run.
'''

# Standard imports
import sciris as sc
import hpvsim as hpv
import optuna
from sqlalchemy.pool import NullPool

# Imports from this repository
import run_sim as rs

# Comment out to not run
to_run = [
    'run_calibration',
    # 'plot_calibration',
]


debug = 0 # Smaller runs
do_save = True


# Run settings for calibration (dependent on debug)
n_trials    = [1000, 2][debug]  # How many trials to run for calibration
n_workers   = [40, 4][debug]    # How many cores to use
storage_url     = ["mysql://hpvsim_user@localhost/hpvsim_db", None][debug] # Storage for calibrations


########################################################################
# Run calibration
########################################################################
def run_calib(n_trials=None, n_workers=None,
              do_plot=False, do_save=True):

    sim = rs.make_sim(calib=True)

    calib_pars = dict(
        beta=[0.2, 0.1, 0.3],
        dur_transformed=dict(par1=[5, 3, 10]),
    )

    genotype_pars = dict(
        hpv16=dict(
            sev_fn=dict(k=[0.5, 0.2, 0.7]),
            dur_episomal=dict(par1=[6, 4, 12]),
        ),
        hpv18=dict(
            sev_fn=dict(k=[0.5, 0.2, 0.7]),
            dur_episomal=dict(par1=[6, 4, 12]),
        ),
        hrhpv=dict(
            sev_fn=dict(k=[0.5, 0.2, 0.7]),
            dur_episomal=dict(par1=[6, 4, 12]),
        ),
    )

    datafiles = [
        f'data/england_cancer_cases.csv',
        f'data/england_cancer_types.csv',
        f'data/england_cin1_types.csv',
        f'data/england_cin3_types.csv',
    ]

    if storage_url is None:
        storage = None
    else:
        storage = optuna.storages.RDBStorage(storage_url, engine_kwargs={"poolclass": NullPool})

    calib = hpv.Calibration(sim, calib_pars=calib_pars, genotype_pars=genotype_pars,
                            name=f'england_calib',
                            datafiles=datafiles,
                            total_trials=n_trials, n_workers=n_workers,
                            storage=storage
                            )
    calib.calibrate()
    filename = f'england_calib'
    calib.run_args = None # Remove
    if do_plot:
        calib.plot(do_save=True, fig_path=f'results/england_calib.png')
    if do_save:
        sc.saveobj(f'results/{filename}.obj', calib)

    print(f'Best pars are {calib.best_pars}')

    return sim, calib


########################################################################
# Load pre-run calibration
########################################################################
def load_calib(do_plot=True, which_pars=0, save_pars=True, do_plot_additional=False):

    filename = f'england_calib'
    calib = sc.load(f'results/{filename}.obj')
    if do_plot:
        sc.fonts(add=sc.thisdir(aspath=True) / 'Libertinus Sans')
        sc.options(font='Libertinus Sans')
        fig = calib.plot(res_to_plot=50, plot_type='sns.boxplot', do_save=True,
                         fig_path=f'figures/{filename}')
        fig.suptitle(f'Calibration results, England')
        fig.tight_layout()
        fig.savefig(f'figures/{filename}.png')

    if save_pars:
        calib_pars = calib.trial_pars_to_sim_pars(which_pars=which_pars)
        sc.save(f'results/england_pars.obj', calib_pars)


    return calib


#%% Run as a script
if __name__ == '__main__':

    T = sc.timer()

    # Run calibration - usually on VMs
    if 'run_calibration' in to_run:
        sim, calib = run_calib(n_trials=n_trials, n_workers=n_workers, do_save=do_save, do_plot=False)

    # Load the calibration, plot it, and save the best parameters -- usually locally
    if 'plot_calibration' in to_run:
        calib = load_calib(do_plot=True, save_pars=True, do_plot_additional=False)

    
    T.toc('Done')