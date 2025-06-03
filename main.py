import config as cfg
from formula import Formula as f
from location import Location as l
from plot import Plot as p
import mcraic as mc
import marl as rl
import greedy as gr

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
    for i in range(30, 91, 5):  # FoV from 30 to 90 with step size 5
        print("Fov: ", i)
        sum_rate = 0
        satisfaction = 0
        fairness = 0
        satisfaction_rate = 0
        for j in range(cfg.TIMES):
            [STP, AUS, SFI, USR] = rl.MARL_EXE(N_UE=cfg.N_UE, FoV=i)
            sum_rate += STP
            satisfaction += AUS
            fairness += SFI
            satisfaction_rate += USR
        MARL_FoV_avg_STP.append(sum_rate/cfg.TIMES) 
        MARL_FoV_avg_AUS.append(satisfaction/cfg.TIMES) 
        MARL_FoV_avg_SFI.append(fairness/cfg.TIMES) 
        MARL_FoV_avg_USR.append(satisfaction_rate/cfg.TIMES)
    #################################################################################
    
    # MCRAIC ########################################################################
    # FoV 
    MCRAIC_FoV_avg_STP = []
    MCRAIC_FoV_avg_AUS = []
    MCRAIC_FoV_avg_SFI = []
    MCRAIC_FoV_avg_USR = []
    for i in range(30, 91, 5):  # FoV from 30 to 90 with step size 5
        sum_rate = 0
        satisfaction = 0
        fairness = 0
        satisfaction_rate = 0
        for j in range(cfg.TIMES):
            [STP, AUS, SFI, USR] = mc.MCRAIC_EXE(N_UE=cfg.N_UE, FoV=i)
            sum_rate += STP
            satisfaction += AUS
            fairness += SFI
            satisfaction_rate += USR
        MCRAIC_FoV_avg_STP.append(sum_rate/cfg.TIMES) 
        MCRAIC_FoV_avg_AUS.append(satisfaction/cfg.TIMES) 
        MCRAIC_FoV_avg_SFI.append(fairness/cfg.TIMES) 
        MCRAIC_FoV_avg_USR.append(satisfaction_rate/cfg.TIMES)
    #################################################################################
    
    # GREEDY ########################################################################
    # FoV 
    GREEDY_FoV_avg_STP = []
    GREEDY_FoV_avg_AUS = []
    GREEDY_FoV_avg_SFI = []
    GREEDY_FoV_avg_USR = []
    for i in range(30, 91, 5):  # FoV from 30 to 90 with step size 5
        sum_rate = 0
        satisfaction = 0
        fairness = 0
        satisfaction_rate = 0
        for j in range(cfg.TIMES):
            [STP, AUS, SFI, USR] = gr.GREEDY_EXE(N_UE=cfg.N_UE, FoV=i)
            sum_rate += STP
            satisfaction += AUS
            fairness += SFI
            satisfaction_rate += USR
        GREEDY_FoV_avg_STP.append(sum_rate/cfg.TIMES) 
        GREEDY_FoV_avg_AUS.append(satisfaction/cfg.TIMES) 
        GREEDY_FoV_avg_SFI.append(fairness/cfg.TIMES) 
        GREEDY_FoV_avg_USR.append(satisfaction_rate/cfg.TIMES)
    #################################################################################

    # Plot results
    p.plot_fov_vs_STP(MARL_FoV_avg_STP, MCRAIC_FoV_avg_STP, GREEDY_FoV_avg_STP)
    p.plot_fov_vs_AUS(MARL_FoV_avg_AUS, MCRAIC_FoV_avg_AUS, GREEDY_FoV_avg_AUS)
    p.plot_fov_vs_SFI(MARL_FoV_avg_SFI, MCRAIC_FoV_avg_SFI, GREEDY_FoV_avg_SFI)
    p.plot_fov_vs_USR(MARL_FoV_avg_USR, MCRAIC_FoV_avg_USR, GREEDY_FoV_avg_USR)

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
    for i in range(1, 25, 1):  # N_UE from 1 to 25 with step size 1
        print("N_UE: ", i)
        sum_rate = 0
        satisfaction = 0
        fairness = 0
        satisfaction_rate = 0
        for j in range(cfg.TIMES):
            [STP, AUS, SFI, USR] = rl.MARL_EXE(N_UE=i, FoV=cfg.F_O_V)
            sum_rate += STP
            satisfaction += AUS
            fairness += SFI
            satisfaction_rate += USR
        MARL_N_UE_avg_STP.append(sum_rate/cfg.TIMES) 
        MARL_N_UE_avg_AUS.append(satisfaction/cfg.TIMES) 
        MARL_N_UE_avg_SFI.append(fairness/cfg.TIMES)
        MARL_N_UE_avg_USR.append(satisfaction_rate/cfg.TIMES)
    #################################################################################
    
    # MCRAIC ########################################################################
    # N_UE 
    MCRAIC_N_UE_avg_STP = []
    MCRAIC_N_UE_avg_AUS = []
    MCRAIC_N_UE_avg_SFI = []
    MCRAIC_N_UE_avg_USR = []
    for i in range(1, 25, 1):  # N_UE from 1 to 25 with step size 1
        sum_rate = 0
        satisfaction = 0
        fairness = 0
        satisfaction_rate = 0
        for j in range(cfg.TIMES):
            [STP, AUS, SFI, USR] = mc.MCRAIC_EXE(N_UE=i, FoV=cfg.F_O_V)
            sum_rate += STP
            satisfaction += AUS
            fairness += SFI
            satisfaction_rate += USR
        MCRAIC_N_UE_avg_STP.append(sum_rate/cfg.TIMES) 
        MCRAIC_N_UE_avg_AUS.append(satisfaction/cfg.TIMES) 
        MCRAIC_N_UE_avg_SFI.append(fairness/cfg.TIMES)
        MCRAIC_N_UE_avg_USR.append(satisfaction_rate/cfg.TIMES)
    #################################################################################

    # GREEDY ########################################################################
    # N_UE 
    GREEDY_N_UE_avg_STP = []
    GREEDY_N_UE_avg_AUS = []
    GREEDY_N_UE_avg_SFI = []
    GREEDY_N_UE_avg_USR = []
    for i in range(1, 25, 1):  # N_UE from 1 to 25 with step size 1
        sum_rate = 0
        satisfaction = 0
        fairness = 0
        satisfaction_rate = 0
        for j in range(cfg.TIMES):
            [STP, AUS, SFI, USR] = gr.GREEDY_EXE(N_UE=i, FoV=cfg.F_O_V)
            sum_rate += STP
            satisfaction += AUS
            fairness += SFI
            satisfaction_rate += USR
        GREEDY_N_UE_avg_STP.append(sum_rate/cfg.TIMES) 
        GREEDY_N_UE_avg_AUS.append(satisfaction/cfg.TIMES) 
        GREEDY_N_UE_avg_SFI.append(fairness/cfg.TIMES)
        GREEDY_N_UE_avg_USR.append(satisfaction_rate/cfg.TIMES)
    #################################################################################
    
    # Plot results
    p.plot_nue_vs_STP(MARL_N_UE_avg_STP, MCRAIC_N_UE_avg_STP, GREEDY_N_UE_avg_STP)
    p.plot_nue_vs_AUS(MARL_N_UE_avg_AUS, MCRAIC_N_UE_avg_AUS, GREEDY_N_UE_avg_AUS)
    p.plot_nue_vs_SFI(MARL_N_UE_avg_SFI, MCRAIC_N_UE_avg_SFI, GREEDY_N_UE_avg_SFI)
    p.plot_nue_vs_USR(MARL_N_UE_avg_USR, MCRAIC_N_UE_avg_USR, GREEDY_N_UE_avg_USR)

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

    
    
    