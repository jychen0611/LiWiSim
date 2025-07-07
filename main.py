import config as cfg
from formula import Formula as f
from location import Location as l
from plot import Plot as p
import mcraic as mc
import marl as rl
import greedy as gr
import rand as rd
import time
import csv
import json
import os

def FoV_Experiments():
    ########################################################################
    # Experiments with FoV angle                                           #
    ########################################################################

    # MARL ##########################################################################
    # FoV 
    MARL_FoV_avg_STP = []
    MARL_FoV_avg_AUS = []
    MARL_FoV_avg_SFI = []
    MARL_FoV_avg_USR = []
    MARL_FoV_avg_OTR = []
    for i in range(30, 91, 5):  # FoV from 30 to 90 with step size 5
        print("Fov: ", i)
        sum_rate = 0
        satisfaction = 0
        fairness = 0
        satisfaction_rate = 0
        outage_ratio = 0
        for j in range(cfg.TIMES):
            [STP, AUS, SFI, USR, OTR] = rl.MARL_EXE(N_UE=cfg.N_UE, FoV=i)
            sum_rate += STP
            satisfaction += AUS
            fairness += SFI
            satisfaction_rate += USR
            outage_ratio += OTR
        MARL_FoV_avg_STP.append(sum_rate/cfg.TIMES) 
        MARL_FoV_avg_AUS.append(satisfaction/cfg.TIMES) 
        MARL_FoV_avg_SFI.append(fairness/cfg.TIMES) 
        MARL_FoV_avg_USR.append(satisfaction_rate/cfg.TIMES)
        MARL_FoV_avg_OTR.append(outage_ratio/cfg.TIMES)
    #################################################################################
    
    # MCRAIC ########################################################################
    # FoV 
    MCRAIC_FoV_avg_STP = []
    MCRAIC_FoV_avg_AUS = []
    MCRAIC_FoV_avg_SFI = []
    MCRAIC_FoV_avg_USR = []
    MCRAIC_FoV_avg_OTR = []
    for i in range(30, 91, 5):  # FoV from 30 to 90 with step size 5
        sum_rate = 0
        satisfaction = 0
        fairness = 0
        satisfaction_rate = 0
        outage_ratio = 0
        for j in range(cfg.TIMES):
            [STP, AUS, SFI, USR, OTR] = mc.MCRAIC_EXE(N_UE=cfg.N_UE, FoV=i)
            sum_rate += STP
            satisfaction += AUS
            fairness += SFI
            satisfaction_rate += USR
            outage_ratio += OTR
        MCRAIC_FoV_avg_STP.append(sum_rate/cfg.TIMES) 
        MCRAIC_FoV_avg_AUS.append(satisfaction/cfg.TIMES) 
        MCRAIC_FoV_avg_SFI.append(fairness/cfg.TIMES) 
        MCRAIC_FoV_avg_USR.append(satisfaction_rate/cfg.TIMES)
        MCRAIC_FoV_avg_OTR.append(outage_ratio/cfg.TIMES)
    #################################################################################
    
    # GREEDY ########################################################################
    # FoV 
    GREEDY_FoV_avg_STP = []
    GREEDY_FoV_avg_AUS = []
    GREEDY_FoV_avg_SFI = []
    GREEDY_FoV_avg_USR = []
    GREEDY_FoV_avg_OTR = []
    for i in range(30, 91, 5):  # FoV from 30 to 90 with step size 5
        sum_rate = 0
        satisfaction = 0
        fairness = 0
        satisfaction_rate = 0
        outage_ratio = 0
        for j in range(cfg.TIMES):
            [STP, AUS, SFI, USR, OTR] = gr.GREEDY_EXE(N_UE=cfg.N_UE, FoV=i)
            sum_rate += STP
            satisfaction += AUS
            fairness += SFI
            satisfaction_rate += USR
            outage_ratio += OTR
        GREEDY_FoV_avg_STP.append(sum_rate/cfg.TIMES) 
        GREEDY_FoV_avg_AUS.append(satisfaction/cfg.TIMES) 
        GREEDY_FoV_avg_SFI.append(fairness/cfg.TIMES) 
        GREEDY_FoV_avg_USR.append(satisfaction_rate/cfg.TIMES)
        GREEDY_FoV_avg_OTR.append(outage_ratio/cfg.TIMES)
    #################################################################################

    # RANDOM ########################################################################
    # FoV 
    RANDOM_FoV_avg_STP = []
    RANDOM_FoV_avg_AUS = []
    RANDOM_FoV_avg_SFI = []
    RANDOM_FoV_avg_USR = []
    RANDOM_FoV_avg_OTR = []
    for i in range(30, 91, 5):  # FoV from 30 to 90 with step size 5
        sum_rate = 0
        satisfaction = 0
        fairness = 0
        satisfaction_rate = 0
        outage_ratio = 0
        for j in range(cfg.TIMES):
            [STP, AUS, SFI, USR, OTR] = rd.RANDOM_EXE(N_UE=cfg.N_UE, FoV=i)
            sum_rate += STP
            satisfaction += AUS
            fairness += SFI
            satisfaction_rate += USR
            outage_ratio += OTR
        RANDOM_FoV_avg_STP.append(sum_rate/cfg.TIMES) 
        RANDOM_FoV_avg_AUS.append(satisfaction/cfg.TIMES) 
        RANDOM_FoV_avg_SFI.append(fairness/cfg.TIMES) 
        RANDOM_FoV_avg_USR.append(satisfaction_rate/cfg.TIMES)
        RANDOM_FoV_avg_OTR.append(outage_ratio/cfg.TIMES)
    #################################################################################

    # Plot results
    p.plot_fov_vs_STP(MARL_FoV_avg_STP, MCRAIC_FoV_avg_STP, GREEDY_FoV_avg_STP, RANDOM_FoV_avg_STP)
    p.plot_fov_vs_AUS(MARL_FoV_avg_AUS, MCRAIC_FoV_avg_AUS, GREEDY_FoV_avg_AUS, RANDOM_FoV_avg_AUS)
    p.plot_fov_vs_SFI(MARL_FoV_avg_SFI, MCRAIC_FoV_avg_SFI, GREEDY_FoV_avg_SFI, RANDOM_FoV_avg_SFI)
    p.plot_fov_vs_USR(MARL_FoV_avg_USR, MCRAIC_FoV_avg_USR, GREEDY_FoV_avg_USR, RANDOM_FoV_avg_USR)
    p.plot_fov_vs_OTR(MARL_FoV_avg_OTR, MCRAIC_FoV_avg_OTR, GREEDY_FoV_avg_OTR, RANDOM_FoV_avg_OTR)

    # Store results
    # Ensure output folder exists
    os.makedirs("data", exist_ok=True)

    # FoV from 30 to 90 with step of 5
    FoV_values = list(range(30, 91, 5))  # [30, 35, 40, ..., 90]

    # Make sure your metric lists are already defined and of same length as FoV_values
    # Example placeholder: MARL_FoV_avg_STP = [0.8, 0.82, ...] (length should be 13)

    # Header
    fov_header = [
        'FoV',
        'MARL_STP', 'MCRAIC_STP', 'GREEDY_STP', 'RANDOM_STP',
        'MARL_AUS', 'MCRAIC_AUS', 'GREEDY_AUS', 'RANDOM_AUS',
        'MARL_SFI', 'MCRAIC_SFI', 'GREEDY_SFI', 'RANDOM_SFI',
        'MARL_USR', 'MCRAIC_USR', 'GREEDY_USR', 'RANDOM_USR',
        'MARL_OTR', 'MCRAIC_OTR', 'GREEDY_OTR', 'RANDOM_OTR',
    ]

    # Construct rows
    fov_rows = []
    for i in range(len(FoV_values)):
        row = [
            FoV_values[i],
            MARL_FoV_avg_STP[i], MCRAIC_FoV_avg_STP[i], GREEDY_FoV_avg_STP[i], RANDOM_FoV_avg_STP[i],
            MARL_FoV_avg_AUS[i], MCRAIC_FoV_avg_AUS[i], GREEDY_FoV_avg_AUS[i], RANDOM_FoV_avg_AUS[i],
            MARL_FoV_avg_SFI[i], MCRAIC_FoV_avg_SFI[i], GREEDY_FoV_avg_SFI[i], RANDOM_FoV_avg_SFI[i],
            MARL_FoV_avg_USR[i], MCRAIC_FoV_avg_USR[i], GREEDY_FoV_avg_USR[i], RANDOM_FoV_avg_USR[i],
            MARL_FoV_avg_OTR[i], MCRAIC_FoV_avg_OTR[i], GREEDY_FoV_avg_OTR[i], RANDOM_FoV_avg_OTR[i],
        ]
        fov_rows.append(row)

    # Write CSV
    with open('data/fov_metrics.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fov_header)
        writer.writerows(fov_rows)

    # Write JSON
    fov_json_data = []
    for row in fov_rows:
        entry = dict(zip(fov_header, row))
        fov_json_data.append(entry)

    with open('data/fov_metrics.json', 'w') as f:
        json.dump(fov_json_data, f, indent=4)

def N_UE_Experiments():
    ########################################################################
    # Experiments with N_UE                                                #
    ########################################################################

    # MARL ##########################################################################
    # N_UE 
    MARL_N_UE_avg_STP = []
    MARL_N_UE_avg_AUS = []
    MARL_N_UE_avg_SFI = []
    MARL_N_UE_avg_USR = []
    MARL_N_UE_avg_OTR = []
    MARL_N_UE_avg_TRAINING_TIME = []
    MARL_N_UE_avg_EXE_TIME = []
    for i in range(1, 26, 1):  # N_UE from 1 to 25 with step size 1
        print("N_UE: ", i)
        sum_rate = 0
        satisfaction = 0
        fairness = 0
        satisfaction_rate = 0
        outage_ratio = 0
        training_time = 0
        execution_time = 0
        for j in range(cfg.TIMES):
            start = time.perf_counter()
            [STP, AUS, SFI, USR, OTR] = rl.MARL_EXE(N_UE=i, FoV=cfg.F_O_V)
            end = time.perf_counter()
            training_time += (end-start)
            sum_rate += STP
            satisfaction += AUS
            fairness += SFI
            satisfaction_rate += USR
            outage_ratio += OTR
        execution_time = training_time/cfg.EPISODE
        MARL_N_UE_avg_STP.append(sum_rate/cfg.TIMES) 
        MARL_N_UE_avg_AUS.append(satisfaction/cfg.TIMES) 
        MARL_N_UE_avg_SFI.append(fairness/cfg.TIMES)
        MARL_N_UE_avg_USR.append(satisfaction_rate/cfg.TIMES)
        MARL_N_UE_avg_OTR.append(outage_ratio/cfg.TIMES)
        MARL_N_UE_avg_TRAINING_TIME.append(training_time/cfg.TIMES)
        MARL_N_UE_avg_EXE_TIME.append(execution_time/cfg.TIMES)
    #################################################################################
    
    # MCRAIC ########################################################################
    # N_UE 
    MCRAIC_N_UE_avg_STP = []
    MCRAIC_N_UE_avg_AUS = []
    MCRAIC_N_UE_avg_SFI = []
    MCRAIC_N_UE_avg_USR = []
    MCRAIC_N_UE_avg_OTR = []
    MCRAIC_N_UE_avg_EXE_TIME = []
    for i in range(1, 26, 1):  # N_UE from 1 to 25 with step size 1
        sum_rate = 0
        satisfaction = 0
        fairness = 0
        satisfaction_rate = 0
        outage_ratio = 0
        execution_time = 0
        for j in range(cfg.TIMES):
            start = time.perf_counter()
            [STP, AUS, SFI, USR, OTR] = mc.MCRAIC_EXE(N_UE=i, FoV=cfg.F_O_V)
            end = time.perf_counter()
            execution_time += (end-start)
            sum_rate += STP
            satisfaction += AUS
            fairness += SFI
            satisfaction_rate += USR
            outage_ratio += OTR
        MCRAIC_N_UE_avg_STP.append(sum_rate/cfg.TIMES) 
        MCRAIC_N_UE_avg_AUS.append(satisfaction/cfg.TIMES) 
        MCRAIC_N_UE_avg_SFI.append(fairness/cfg.TIMES)
        MCRAIC_N_UE_avg_USR.append(satisfaction_rate/cfg.TIMES)
        MCRAIC_N_UE_avg_OTR.append(outage_ratio/cfg.TIMES)
        MCRAIC_N_UE_avg_EXE_TIME.append(execution_time/cfg.TIMES)
    #################################################################################

    # GREEDY ########################################################################
    # N_UE 
    GREEDY_N_UE_avg_STP = []
    GREEDY_N_UE_avg_AUS = []
    GREEDY_N_UE_avg_SFI = []
    GREEDY_N_UE_avg_USR = []
    GREEDY_N_UE_avg_OTR = []
    for i in range(1, 26, 1):  # N_UE from 1 to 25 with step size 1
        sum_rate = 0
        satisfaction = 0
        fairness = 0
        satisfaction_rate = 0
        outage_ratio = 0
        for j in range(cfg.TIMES):
            [STP, AUS, SFI, USR, OTR] = gr.GREEDY_EXE(N_UE=i, FoV=cfg.F_O_V)
            sum_rate += STP
            satisfaction += AUS
            fairness += SFI
            satisfaction_rate += USR
            outage_ratio += OTR
        GREEDY_N_UE_avg_STP.append(sum_rate/cfg.TIMES) 
        GREEDY_N_UE_avg_AUS.append(satisfaction/cfg.TIMES) 
        GREEDY_N_UE_avg_SFI.append(fairness/cfg.TIMES)
        GREEDY_N_UE_avg_USR.append(satisfaction_rate/cfg.TIMES)
        GREEDY_N_UE_avg_OTR.append(outage_ratio/cfg.TIMES)
    #################################################################################

    # RANDOM ########################################################################
    # N_UE 
    RANDOM_N_UE_avg_STP = []
    RANDOM_N_UE_avg_AUS = []
    RANDOM_N_UE_avg_SFI = []
    RANDOM_N_UE_avg_USR = []
    RANDOM_N_UE_avg_OTR = []
    for i in range(1, 26, 1):  # N_UE from 1 to 25 with step size 1
        sum_rate = 0
        satisfaction = 0
        fairness = 0
        satisfaction_rate = 0
        outage_ratio = 0
        for j in range(cfg.TIMES):
            [STP, AUS, SFI, USR, OTR] = rd.RANDOM_EXE(N_UE=i, FoV=cfg.F_O_V)
            sum_rate += STP
            satisfaction += AUS
            fairness += SFI
            satisfaction_rate += USR
            outage_ratio += OTR
        RANDOM_N_UE_avg_STP.append(sum_rate/cfg.TIMES) 
        RANDOM_N_UE_avg_AUS.append(satisfaction/cfg.TIMES) 
        RANDOM_N_UE_avg_SFI.append(fairness/cfg.TIMES)
        RANDOM_N_UE_avg_USR.append(satisfaction_rate/cfg.TIMES)
        RANDOM_N_UE_avg_OTR.append(outage_ratio/cfg.TIMES)
    #################################################################################
    
    # Plot results
    p.plot_nue_vs_STP(MARL_N_UE_avg_STP, MCRAIC_N_UE_avg_STP, GREEDY_N_UE_avg_STP, RANDOM_N_UE_avg_STP)
    p.plot_nue_vs_AUS(MARL_N_UE_avg_AUS, MCRAIC_N_UE_avg_AUS, GREEDY_N_UE_avg_AUS, RANDOM_N_UE_avg_AUS)
    p.plot_nue_vs_SFI(MARL_N_UE_avg_SFI, MCRAIC_N_UE_avg_SFI, GREEDY_N_UE_avg_SFI, RANDOM_N_UE_avg_SFI)
    p.plot_nue_vs_USR(MARL_N_UE_avg_USR, MCRAIC_N_UE_avg_USR, GREEDY_N_UE_avg_USR, RANDOM_N_UE_avg_USR)
    p.plot_nue_vs_OTR(MARL_N_UE_avg_OTR, MCRAIC_N_UE_avg_OTR, GREEDY_N_UE_avg_OTR, RANDOM_N_UE_avg_OTR)
    p.plot_execution_and_training_time(MARL_N_UE_avg_EXE_TIME, MARL_N_UE_avg_TRAINING_TIME)
    p.plot_execution_time_compare(MARL_N_UE_avg_EXE_TIME, MCRAIC_N_UE_avg_EXE_TIME)

    # Store result
    # Ensure output folder exists
    os.makedirs("data", exist_ok=True)

    # Generate N_UE list based on length of any metric
    N_UE = list(range(1, len(MARL_N_UE_avg_STP) + 1))

    # Prepare header
    header = [
        'N_UE',
        'MARL_STP', 'MCRAIC_STP', 'GREEDY_STP', 'RANDOM_STP',
        'MARL_AUS', 'MCRAIC_AUS', 'GREEDY_AUS', 'RANDOM_AUS',
        'MARL_SFI', 'MCRAIC_SFI', 'GREEDY_SFI', 'RANDOM_SFI',
        'MARL_USR', 'MCRAIC_USR', 'GREEDY_USR', 'RANDOM_USR',
        'MARL_OTR', 'MCRAIC_OTR', 'GREEDY_OTR', 'RANDOM_OTR',
    ]

    # Construct rows
    rows = []
    for i in range(len(N_UE)):
        row = [
            N_UE[i],
            MARL_N_UE_avg_STP[i], MCRAIC_N_UE_avg_STP[i], GREEDY_N_UE_avg_STP[i], RANDOM_N_UE_avg_STP[i],
            MARL_N_UE_avg_AUS[i], MCRAIC_N_UE_avg_AUS[i], GREEDY_N_UE_avg_AUS[i], RANDOM_N_UE_avg_AUS[i],
            MARL_N_UE_avg_SFI[i], MCRAIC_N_UE_avg_SFI[i], GREEDY_N_UE_avg_SFI[i], RANDOM_N_UE_avg_SFI[i],
            MARL_N_UE_avg_USR[i], MCRAIC_N_UE_avg_USR[i], GREEDY_N_UE_avg_USR[i], RANDOM_N_UE_avg_USR[i],
            MARL_N_UE_avg_OTR[i], MCRAIC_N_UE_avg_OTR[i], GREEDY_N_UE_avg_OTR[i], RANDOM_N_UE_avg_OTR[i],
        ]
        rows.append(row)

    with open('data/nue_metrics.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    json_data = []
    for row in rows:
        entry = dict(zip(header, row))
        json_data.append(entry)

    with open('data/nue_metrics.json', 'w') as f:
        json.dump(json_data, f, indent=4)

if __name__ == "__main__":
    print("Simulation Start!")
    
    ########################################################################
    # Experiments with FoV angle                                           #
    ########################################################################

    FoV_Experiments()
    
    ########################################################################
    # Experiments with N_UE                                                #
    ########################################################################

    N_UE_Experiments()

    # Test MARL model
    # rl.MARL_EXE(N_UE=cfg.N_UE, FoV=cfg.F_O_V)

    # Test GREEDY algorithm
    # gr.GREEDY_EXE(N_UE=cfg.N_UE, FoV=cfg.F_O_V)

    # Test RANDOM algorithm
    # rd.RANDOM_EXE(N_UE=cfg.N_UE, FoV=cfg.F_O_V)

    
    
    