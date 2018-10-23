from __future__ import print_function, division
import os
import re
import shutil as sl
import argparse
from mpi4py import MPI
import ag_kwz as agk
import ag_lmplog as agl
import ag_statistics as ags
import vmd
import molecule
import atomsel

"""
Kawska-Zahn approach to aggregate crystals.

This script is doing a Kawska-Zahn approach to crystallize given molecules using
lammps as the driver for molecular dynamics simulations. Equilibration is
checked and the simulation time is elongated if the system has not equilibrated
yet.

Kawska Zahn Approach with lammps. Do not use neigh yes since it leads to segment-
ation faults. Always clear lammps or this will also lead to segmentation faults.
Clearing lammps not necessary if running solely on the cpu.
"""

"""
CAVEAT: DO NOT UNWRAP SOLVENT BOX, IT MUST BE WRAPPED OR OTHERWISE THE DENSITY
        IS WRONG DUE TO THE PERIODIC BOUNDARY CONDITIONS (MOLECULES THAT LEAVE
        THE BOX ARE OUTSIDE AND DO NOT GET MIRRORED BACK -> SOLVATE SHOULD BE IN
        THE MIDDLE OF THE BOX TO NOT BE WRAPPED AS WELL!)

CAVEAT: THE PATTERN STUFF IS ADDED SHOULD BE ACCORDING TO A CERTAIN PROBABILITY.
"""

#==============================================================================#
# Setup MPI
#==============================================================================#

comm = MPI.COMM_WORLD
size = comm.Get_size()  # number of processes in communicator
rank = comm.Get_rank()  # process' id(s) within a communicator

#==============================================================================#
# Helper functions and variables
#==============================================================================#
PWD = os.getcwd()


def get_finished_cycles():
    """
    Gather all finished cycles.

    Returns
    -------
    finished_cycles : list of ints
        all ids of the cycles that were finished
    """
    finished_cycles = []
    folders_pwd = ["{}/{}".format(PWD, i) for i in os.listdir(PWD) if os.path.isdir(i)]

    # get last cycle from directory
    for folder in folders_pwd:
        cycle = re.match(r'.*?([0-9]+)$', folder).group(1)
        cycle = int(cycle)

        # avoid duplicates
        if cycle not in finished_cycles:
            finished_cycles.append(cycle)

    return finished_cycles


def get_next_cycle(finished_cycles):
    """
    requench_out does not exist -> current cycle has not finished yet
    """
    if len(finished_cycles) >= 1:
        current_cycle = max(finished_cycles)

        if os.path.isfile(requench_out) is True:
            next_cycle = current_cycle + 1
        else:
            next_cycle = current_cycle

        #del requench_out
    else:
        next_cycle = 0

    return (current_cycle, next_cycle)


def get_remaining_cycles():
    """
    Scan current folder names for numbers to get the current cycle.

    Returns
    -------
    remaining_cycles : int
        remaining cycles

    """
    finished_cycles = get_finished_cycles()
    current_cycle, next_cycle = get_next_cycle(finished_cycles)
    requench_out = PWD + "/requench_{}/".format(current_cycle) + "requench_{}.dcd".format(current_cycle)
    total_cycles = range(args.cycles)
    idx_next_cycle = total_cycles.index(next_cycle)
    del total_cycles

    #===========================#
    # Molecule to add by pattern
    #===========================#
    id_pattern = 0
    num_patterns = len(args.pa) - 1  # indices start with 0 so one less
    total_cycles = []

    for cycle in range(args.cycles):
        if id_pattern > num_patterns:
            id_pattern = 0
        total_cycles.append((cycle, args.pa[id_pattern]))
        id_pattern += 1

    remaining_cycles = total_cycles[idx_next_cycle:]
    return (remaining_cycles, requench_out)


def create_folder(folder):
    """
    Create folder or skip creation if it already exists
    """
    try:
        os.mkdir(folder, 0755)
    except OSError:
        print("***Info: Folder {} already exists!".format(folder))


def write_to_log(string, filename="kwz_log"):
    """
    Write string 's' to log file named 'kwz.log'.
    """
    with open("kwz_log", "a") as kwz_log:
        kwz_log.write(string)


if __name__ == "__main__":
    percentage_to_check = 80
    #==============================================================================#
    # Argument Parsing
    #==============================================================================#
    parser = argparse.ArgumentParser(prog="kawska_zahn.py", formatter_class=argparse.RawTextHelpFormatter, description="Kawska-Zahn-Approach for accelerated crystallization simulations.")

    # arguments description
    lmpm_help = "Lammps' data-file of the main system."
    lmpa_help = """
    Lammps' data-file with atom-cube_sidetypes and coordinates for one single molecule to
    add to the current system. Atom types have to be defined already by the first
    data/restart file loaded!
    """
    lmps_help = "Create a solvent box for MD-Simulation. Data-file with one single solvent molecule to add."
    lmps_dcd_help = "DCD file of solvent box."
    set_help = "lammps' input-file/-script with basic simulation settings"
    settings_solvent_help = "lammps' input-file/-script with basic simulation settings for the solvent system"
    pair_coeffs_help = "lammps'  script with lj, dreiding, etc. parameters"
    solvent_pc_help = "lammps'  script with lj, dreiding, etc. parameters for the solvent"
    logsteps_help = "log thermodynamic-, steps- and restart-files every" + "'logsteps' steps"
    gpu_help = "utilize lammps' GPU package."
    cycles_help = "Number of aggregations."
    timeout_help = "allowed duration of simulation, for resubmitting purposes;  should be < 24h"
    pa_help = "The pattern in which looping order lmpa will be added, e.g. 0 1 2 3 3 1, repeats every 6 cycles"

    # general
    parser.add_argument("-lmpm", default=None, metavar="*.lmpdat", help=lmpm_help)
    parser.add_argument("-lmpa", default=None, nargs="*", metavar="*.lmpdat", help=lmpa_help)
    parser.add_argument("-lmps", default=None, metavar="*.lmpdat", help=lmps_help)
    parser.add_argument("-lmps_dcd", default=None, metavar="*.lmpdat", help=lmps_dcd_help)
    #parser.add_argument("-solvate_resnames, metavar='cbz sac'")
    parser.add_argument("-set", metavar="*.lmpcfg", required=True, help=set_help)
    parser.add_argument("-settings_solvent", metavar="*.lmpcfg", help=settings_solvent_help)
    parser.add_argument("-pair_coeffs", default=None, metavar="*.lmpcfg", required=True, help=pair_coeffs_help)
    parser.add_argument("-solvent_paircoeffs", default=None, metavar="*.lmpcfg", help=solvent_pc_help)
    parser.add_argument("-logsteps", type=int, default=1000, help=logsteps_help)
    parser.add_argument("-gpu", default=False, action="store_true", help=gpu_help)
    parser.add_argument("-cycles", type=int, default=5, help=cycles_help)
    parser.add_argument("-timeout", metavar="00:01:00", default="00:00:05", help=timeout_help)
    parser.add_argument("-pa", "-pattern_add", nargs="*", default=0, type=int, help=pa_help)

    # quenching
    parser.add_argument("-quench_temp_start", type=int, default=5)
    parser.add_argument("-quench_temp_stop", type=int, default=5)
    parser.add_argument("-quench_steps", type=int, default=250000)
    parser.add_argument("-quench_logsteps", type=int, default=1000)

    # relax cut solvent
    parser.add_argument("-relax_cut_tstart", type=int, default=200)
    parser.add_argument("-relax_cut_tstop", type=int, default=250)
    parser.add_argument("-relax_cut_pstart", type=int, default=40)
    parser.add_argument("-relax_cut_pstop", type=int, default=10)
    parser.add_argument("-relax_cut_steps", type=int, default=50000)
    parser.add_argument("-relax_cut_logsteps", type=int, default=1000)

    # create voids in relaxed solvent
    parser.add_argument("-void_tstart", type=int, default=250)
    parser.add_argument("-void_tstop", type=int, default=300)
    parser.add_argument("-void_pstart", type=int, default=10)
    parser.add_argument("-void_pstop", type=int, default=1)
    parser.add_argument("-void_steps", type=int, default=2000)
    parser.add_argument("-void_logsteps", type=int, default=1000)

    # relax solvent in solution
    parser.add_argument("-relax_solv_tstart", type=int, default=250)
    parser.add_argument("-relax_solv_tstop", type=int, default=300)
    parser.add_argument("-relax_solv_pstart", type=int, default=10)
    parser.add_argument("-relax_solv_pstop", type=int, default=1)
    parser.add_argument("-relax_solv_steps", type=int, default=2000)
    parser.add_argument("-relax_solv_logsteps", type=int, default=1000)

    # equilibrate solvate and solvent
    parser.add_argument("-heat_tstart", type=int, default=200)
    parser.add_argument("-heat_tstop", type=int, default=300)
    parser.add_argument("-heat_pstart", type=int, default=50)
    parser.add_argument("-heat_pstop", type=int, default=1)
    parser.add_argument("-heat_steps", type=int, default=50000)
    parser.add_argument("-heat_logsteps", type=int, default=1000)

    # annealing
    parser.add_argument("-anneal_tstart", type=int, default=300)
    parser.add_argument("-anneal_tstop", type=int, default=300)
    parser.add_argument("-anneal_pstart", type=int, default=1)
    parser.add_argument("-anneal_pstop", type=int, default=1)
    parser.add_argument("-anneal_steps", type=int, default=2000000)
    parser.add_argument("-anneal_steps_plus", type=int, default=500000)
    parser.add_argument("-anneal_logsteps", type=int, default=500)

    # requenching
    parser.add_argument("-requench_steps", type=int, default=150000)

    args = parser.parse_args()

    #==============================================================================#
    # Remaining cycles and molecule to add pattern
    #==============================================================================#
    remaining_cycles, requench_out = get_remaining_cycles()
    #resnames = set(args.solvate_resnames.split())

    #==============================================================================#
    # Kawska Zahn Approach
    #==============================================================================#

    for curcycle, idx_lmpa in remaining_cycles:

        #==========================================================#
        # Define folders and files, retrieve stage of current cycle
        #==========================================================#
        if rank == 0:
            write_to_log("Cycle: {:d}\n".format(curcycle))

        # declare folder names for each cycle
        sysprep_dir = PWD + "/sysprep_{}/".format(curcycle)
        quench_dir = PWD + "/quench_{}/".format(curcycle)
        anneal_dir = PWD + "/anneal_{}/".format(curcycle)
        requench_dir = PWD + "/requench_{}/".format(curcycle)

        # system preparation
        sysprep_out_lmpdat = sysprep_dir + "sysprep_out_{}.lmpdat".format(curcycle)

        # quench
        quench_out = quench_dir + "quench_out_{}.lmprst".format(curcycle)
        quench_rst = quench_dir + "quench_rst_{}.lmprst".format(curcycle)
        quench_dcd = quench_dir + "quench_{}.dcd".format(curcycle)
        quench_log = quench_dir + "quench_{}.lmplog".format(curcycle)
        lmpsettings_quench = agk.LmpShortcuts(tstart=args.quench_temp_start, tstop=args.quench_temp_stop, logsteps=args.quench_logsteps, runsteps=args.quench_steps, pc_file=args.pair_coeffs, settings_file=args.set, input_lmpdat=sysprep_out_lmpdat, inter_lmprst=quench_rst, output_lmprst=quench_out, output_dcd=quench_dcd, output_lmplog=quench_log, gpu=args.gpu)

        # anneal -> solvent
        cut_solv_lmpdat = anneal_dir + "cut_solv_{}".format(curcycle) + "_out.lmpdat"
        cut_solv_rst = anneal_dir + "cut_solv_{}".format(curcycle) + "_tmp.rst"
        cut_solv_out = anneal_dir + "cut_solv_{}".format(curcycle) + "_out.lmprst"
        cut_solv_dcd = anneal_dir + "cut_solv_{}".format(curcycle) + ".dcd"
        cut_solv_log = anneal_dir + "cut_solv_{}".format(curcycle) + ".lmplog"
        lmpsettings_relax_cut = agk.LmpShortcuts(tstart=args.relax_cut_tstart, tstop=args.relax_cut_tstop, pstart=args.relax_cut_pstart, pstop=args.relax_cut_pstop, logsteps=args.relax_cut_logsteps, runsteps=args.relax_cut_steps, pc_file=args.pair_coeffs, settings_file=args.settings_solvent, input_lmpdat=cut_solv_lmpdat, inter_lmprst=cut_solv_rst, output_lmprst=cut_solv_out, output_dcd=cut_solv_dcd, output_lmplog=cut_solv_log, gpu=args.gpu)

        void_solv_rst = anneal_dir + "void_solv_{}".format(curcycle) + "_tmp.rst"
        void_solv_out = anneal_dir + "void_solv_{}".format(curcycle) + "_out.lmprst"
        void_solv_dcd = anneal_dir + "void_solv_{}".format(curcycle) + ".dcd"
        void_solv_log = anneal_dir + "void_solv_{}".format(curcycle) + ".lmplog"
        lmpsettings_void = agk.LmpShortcuts(tstart=args.void_tstart, tstop=args.void_tstop, pstart=args.void_pstart, pstop=args.void_pstop,logsteps=args.void_logsteps, runsteps=args.void_steps, pc_file=args.pair_coeffs,settings_file=args.settings_solvent, input_lmprst=lmpsettings_relax_cut.output_lmprst, inter_lmprst=void_solv_rst, output_lmprst=void_solv_out, output_dcd=void_solv_dcd,output_lmplog=void_solv_log, gpu=args.gpu)

        if args.lmps is not None:
            solution_lmpdat = anneal_dir + "solution_{}".format(curcycle) + "_out.lmpdat"
        else:
            solution_lmpdat = sysprep_out_lmpdat

        #relax_solv_in = anneal_dir + "relax_solv_{}".format(curcycle) + "_in.lmpdat"
        relax_solv_out = anneal_dir + "relax_solv_{}".format(curcycle) + "_out.lmprst"
        relax_solv_rst = anneal_dir + "relax_solv_{}".format(curcycle) + "_tmp.lmprst"
        relax_solv_dcd = anneal_dir + "relax_solv_{}".format(curcycle) + ".dcd"
        relax_solv_log = anneal_dir + "relax_solv_{}".format(curcycle) + ".lmplog"
        lmpsettings_relax_solv = agk.LmpShortcuts(tstart=args.relax_solv_tstart, tstop=args.relax_solv_tstop, pstart=args.relax_solv_pstart, pstop=args.relax_solv_pstop,logsteps=args.relax_solv_logsteps, runsteps=args.relax_solv_steps, pc_file=args.pair_coeffs, settings_file=args.set,input_lmpdat=solution_lmpdat, inter_lmprst=relax_solv_rst,output_lmprst=relax_solv_out, output_dcd=relax_solv_dcd, output_lmplog=relax_solv_log,gpu=args.gpu)

        # anneal -> equilibration/heating
        heat_out = anneal_dir + "equil_anneal_{}".format(curcycle) + "_out.lmprst"
        heat_rst = anneal_dir + "equil_anneal_{}".format(curcycle) + "_tmp.lmprst"
        heat_dcd = anneal_dir + "equil_anneal_{}".format(curcycle) + ".dcd"
        heat_log = anneal_dir + "equil_anneal_{}".format(curcycle) + ".lmplog"
        lmpsettings_heat = agk.LmpShortcuts(tstart=args.heat_tstart, tstop=args.heat_tstop,pstart=args.heat_pstart, pstop=args.heat_pstop,logsteps=args.heat_logsteps, runsteps=args.heat_steps,pc_file=args.pair_coeffs, settings_file=args.set, input_lmpdat=solution_lmpdat, input_lmprst=lmpsettings_relax_solv.output_lmprst, inter_lmprst=heat_rst,output_lmprst=heat_out,output_dcd=heat_dcd, output_lmplog=heat_log,gpu=args.gpu)

        if args.lmps is None:
            lmpsettings_heat.input_lmprst = lmpsettings_quench.output_lmprst
            #lmpsettings_heat.input_lmpdat = None
            #lmpsettings_heat.pstart = None
            #lmpsettings_heat.pstop = None

        # anneal -> productive
        anneal_out = anneal_dir + "anneal_{}".format(curcycle) + "_out.lmprst"
        anneal_rst = anneal_dir + "anneal_{}".format(curcycle) + "_tmp.lmprst"
        anneal_dcd = anneal_dir + "anneal_{}".format(curcycle) + ".dcd"
        anneal_log = anneal_dir + "anneal_{}".format(curcycle) + ".lmplog"
        lmpsettings_anneal = agk.LmpShortcuts(tstart=args.anneal_tstart, tstop=args.anneal_tstop,pstart=args.anneal_pstart, pstop=args.anneal_pstop,logsteps=args.anneal_logsteps, runsteps=args.anneal_steps,pc_file=args.pair_coeffs, settings_file=args.set, input_lmpdat=solution_lmpdat, input_lmprst=lmpsettings_heat.output_lmprst, inter_lmprst=anneal_rst,output_lmprst=anneal_out,output_dcd=anneal_dcd, output_lmplog=anneal_log,gpu=args.gpu)

        # requench
        tmp_solvate_anneal_out = requench_dir + "requench_{}".format(curcycle) + "_tmp_solvate_out.lmpdat"
        #requench_out = requench_dir + "requench_{}".format(curcycle) + "_out.lmpdat"
        requench_dcd = requench_dir + "requench_{}".format(curcycle) + ".dcd"
        requench_log = requench_dir + "requench_{}".format(curcycle) + ".lmplog"

        # important files from previous run
        pre_sysprep_out = "{0}/sysprep_{1}/sysprep_out_{1}.lmpdat".format(PWD, curcycle - 1)
        pre_solvent_anneal_out = "{0}/anneal_{1}/anneal_{0}_solvent_out.xyz".format(PWD, curcycle - 1)
        pre_requench_dcd = "{0}/requench_{1}/requench_{1}.dcd".format(PWD, curcycle - 1)

        quench_success = os.path.isfile(lmpsettings_quench.output_lmprst)
        anneal_success = os.path.isfile(lmpsettings_anneal.output_lmprst)

        #==========================================================================#
        # Aggregation
        #==========================================================================#

        # define main system
        if os.path.isfile(pre_requench_dcd) is True:
            main_prep_lmpdat = pre_sysprep_out
        else:
            main_prep_lmpdat = os.path.abspath(args.lmpm)

        while not os.path.isfile(lmpsettings_anneal.output_lmprst):
            anneal_attempts = 0
            while not os.path.isfile(lmpsettings_quench):
                quench_attempts = 0
                while not os.path.isfile(sysprep_out_lmpdat):
                    sysprep_attempts = 0
                    #==================================================================#
                    # 1. System Preparation
                    #==================================================================#
                    if rank == 0:
                        create_folder(sysprep_dir)
                        sysprep_success = agk.sysprep(sysprep_out_lmpdat, main_prep_lmpdat, args.lmpa[idx_lmpa], dcd_add=requench_dcd, frame_idx=-1)

                        if sysprep_success is False:
                            sl.move(sysprep_dir, sysprep_dir + "failed_{}".format(sysprep_attempts))
                            sysprep_attempts += 1

                    if sysprep_success is False and sysprep_attempts > 20:
                        exit(100)

                #===================================================================
                # 2. System Quenching
                #===================================================================

                if os.path.isfile(quench_out) is False:
                    if rank == 0:
                        create_folder(quench_dir)
                    quench_success = agk.quench(lmpsettings_quench, main_prep_lmpdat)

                    if quench_success is False:
                        fail_appendix = "failed_{}".format(quench_attempts)
                        sl.move(sysprep_dir, sysprep_dir.rstrip("/") + fail_appendix)
                        sl.move(quench_dir, quench_dir.rstrip("/") + fail_appendix)
                        del fail_appendix
                        quench_attempts += 1
                    else:
                        print("***Quenching-Info: Quenching done!")
                        del quench_attempts

                    if quench_attempts > 20 and quench_success is False:
                        exit(101)

            #======================================================================#
            # 3. ANNEALING
            #======================================================================#
            if os.path.isfile(lmpsettings_anneal.output_lmprst) is False:
                if rank == 0:
                    create_folder(anneal_dir)
                    solvate_sys = agk.read_system(lmpsettings_quench.input_lmpdat, dcd=lmpsettings_quench.output_dcd)
                    solvate_sys_natoms = len(solvate_sys.atoms)
                    atm_idxs_solvate = range(solvate_sys_natoms)
                else:
                    solvate_sys = None

                solvate_sys = comm.bcast(solvate_sys, 0)

                # check if solvent is needed
                if args.lmps is not None:

                    # write data file for cut out solvent box
                    if rank == 0 and not os.path.isfile(cut_solv_lmpdat):
                        agk.cut_box(cut_solv_lmpdat, args.lmps, solvate_sys.ts_boxes[-1], args.lmps_dcd, frame_idx=-1)

                    # relax cut box
                    if not os.path.isdir(lmpsettings_relax_cut.output_lmprst):
                        agk.berendsen_md(lmpsettings_relax_cut)

                    # create voids and write lammps data with solvate and solvent combined
                    if not os.path.isfile(lmpsettings_void.output_lmprst):
                        for _ in xrange(5):
                            no_clashes = agk.create_voids(lmpsettings_void, lmpsettings_quench.input_lmpdat, lmpsettings_quench.output_dcd)

                            if no_clashes is True:
                                break

                        else:
                            print("Could not create large enough voids, void creation needs revision")
                            sl.move(lmpsettings_void.output_lmprst, lmpsettings_void.inter_lmprst)
                            exit(102)

                    # combine solute and solvent
                    if rank == 0 and not os.path.isfile(solution_lmpdat):
                        agk.write_data(solution_lmpdat, sysprep_out_lmpdat, lmpdat_b=lmpsettings_relax_cut.input_lmpdat, dcd_a=lmpsettings_quench.output_dcd, dcd_b=lmpsettings_void.output_dcd, pair_coeffs=args.pair_coeffs)

                    # relax solvent molecules in solution, since solvent is always appended
                    # every atom id greater than the last one of the solvate has to be
                    # a solvent atom
                    agk.berendsen_md(lmpsettings_relax_solv, group="group solvate id > {}".format(solvate_sys_natoms))

                # heat whole solution
                agk.berendsen_md(lmpsettings_heat)

                # check if aggregate is still ok
                if rank == 0:
                    solution_sys = agk.read_system(lmpsettings_heat.input_lmpdat, lmpsettings_heat.output_dcd)
                    solution_sys_atoms_idxs = range(len(solution_sys.atoms))
                    aggregate_ok = solution_sys.check_aggregate(solvate_sys, excluded_atm_idxs=solution_sys_atoms_idxs[solvate_sys_natoms:])

                    # stop further calculations and start from the beginning
                    if not aggregate_ok:
                        sl.move(sysprep_dir, sysprep_dir.rstrip("/") + "failed_{}".format(sysprep_attempts))
                        sl.move(quench_dir, quench_dir.rstrip("/") + "failed_{}".format(quench_attempts))
                        sl.move(anneal_dir, anneal_dir.rstrip("/") + "failed_{}".format(anneal_attempts))
                else:
                    aggregate_ok = False

                aggregate_ok = comm.bcast(aggregate_ok, 0)

                # reset all failed attempts and restart
                if not aggregate_ok:
                    anneal_attempts = 0
                    quench_attempts = 0
                    sysprep_attempts = 0
                    continue

                # productive run
                anneal_success = agk.anneal_productive(lmpsettings_anneal, atm_idxs_solvate, percentage_to_check)

                if not anneal_success:
                    anneal_attempts = 0
                    quench_attempts = 0
                    sysprep_attempts = 0
                    sl.move(sysprep_dir, sysprep_dir.rstrip("/") + "failed_{}".format(sysprep_attempts))
                    sl.move(quench_dir, quench_dir.rstrip("/") + "failed_{}".format(quench_attempts))
                    sl.move(anneal_dir, anneal_dir.rstrip("/") + "failed_{}".format(anneal_attempts))
                    continue
                else:
                    # vmd clustering
                    pass
