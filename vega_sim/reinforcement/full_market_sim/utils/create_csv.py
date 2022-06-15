import os
import csv
from pathlib import Path


def createfile_MMmodel(folder_path, strategy):
    """
    Create a csv file to load the output data from current strategy.
    If the file exists, clear the file; If not, create one.
    """

    Path(folder_path).mkdir(exist_ok=True)
    file_path = folder_path + strategy
    if os.path.isfile(file_path):
        f = open(file_path, "w")
        f.truncate()
        f.close()

    header = [
        "Iteration",
        "Time Step",
        "LP: General Account",
        "LP: Margin Account",
        "LP: Bond Account",
        "LP: General Pnl",
        "LP: RealisedPnl",
        "LP: UnrealisedPnl",
        "LP: Position",
        "LP: Bid Depth",
        "LP: Ask Depth",
        "Buying MOs",
        "Selling MOs",
        "LOs at bid",
        "LOs at ask",
        "External Midprice",
        "Markprice",
        "Average Entry price",
        "InsurancePool",
        "LiquifeeAccount",
        "InfrafeeAccount",
        "Market Trading mode",
        "Market Sate",
    ]

    with open(file_path, "a", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
    return file_path


def createfile_multiLPs(
    strategy="MC_multiLPs_MMmodel.csv",
    num_lps=10,
):
    """
    Create a csv file to load the output data from current strategy.
    If the file exists, clear the file; If not, create one.
    """
    path = os.getcwd() + "/"
    file = path + strategy
    if os.path.isfile(file):
        f = open(file, "w")
        f.truncate()
        f.close()

    header = [
        "Iteration",
        "Time Step",
    ]

    header_GA = ["LP{}: General".format(i + 1) for i in range(num_lps)]
    header_MA = ["LP{}: Margin".format(i + 1) for i in range(num_lps)]
    header_BA = ["LP{}: Bond".format(i + 1) for i in range(num_lps)]
    header_PNL = ["LP{}: GeneralPnl".format(i + 1) for i in range(num_lps)]
    header_Re = ["LP{}: RealisedPnl".format(i + 1) for i in range(num_lps)]
    header_Un = ["LP{}: UnrealisedPnl".format(i + 1) for i in range(num_lps)]
    header_Pos = ["LP{}: Position".format(i + 1) for i in range(num_lps)]
    header_bid = ["LP{}: Bid".format(i + 1) for i in range(num_lps)]
    header_ask = ["LP{}: Ask".format(i + 1) for i in range(num_lps)]
    header_entry = ["LP{}: Entryprice".format(i + 1) for i in range(num_lps)]
    header_els = ["LP{}: ELS".format(i + 1) for i in range(num_lps)]

    header = (
        header
        + header_GA
        + header_MA
        + header_BA
        + header_PNL
        + header_Re
        + header_Un
        + header_Pos
        + header_bid
        + header_ask
        + header_entry
        + header_els
    )

    header += [
        "Buying MOs",
        "Selling MOs",
        "LOs at bid",
        "LOs at ask",
        "External Midprice",
        "Markprice",
        "InsurancePool",
        "LiquifeeAccount",
        "InfrafeeAccount",
        "Market Trading mode",
        "Market Sate",
    ]

    with open(file, "a", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)


def createfile_infotrader(
    strategy,
):
    """
    Create a csv file to load the output data from current strategy.
    If the file exists, clear the file; If not, create one.
    """
    path = os.getcwd() + "/"
    file = path + strategy
    if os.path.isfile(file):
        f = open(file, "w")
        f.truncate()
        f.close()

    header = [
        "Iteration",
        "Time Step",
        "LP: General Account",
        "LP: Margin Account",
        "LP: Bond Account",
        "LP: GeneralPnl",
        "LP: RealisedPnl",
        "LP: UnrealisedPnl",
        "LP: Position",
        "Trader: General Account",
        "Trader: Margin Account",
        "Trader: GeneralPnl",
        "Trader: RealisedPnl",
        "Trader: UnrealisedPnl",
        "Trader: Position",
        "LP: Bid Depth",
        "LP: Ask Depth",
        "Total buyingMO",
        "Total sellingMO",
        "BuyingMO Trader",
        "SellingMO Trader",
        "LOs at bid",
        "LOs at ask",
        "External Midprice",
        "Markprice",
        "Average Entry price",
        "InsurancePool",
        "LiquifeeAccount",
        "InfrafeeAccount",
        "Market Trading mode",
        "Market Sate",
    ]

    with open(file, "a", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
