from argparse import OPTIONAL
import csv
from doctest import REPORT_ONLY_FIRST_FAILURE
import os


def log_simple_MMmodel(
    iteration,
    time_step,
    general_account,
    margin_account,
    bond_account,
    generalPnl,
    realisedPnl,
    unrealisedPnl,
    inventory,
    bid_depth,
    ask_depth,
    buying_MO,
    selling_MO,
    LOs_bid,
    LOs_ask,
    midprice,
    markprice,
    Averageentryprice,
    insurance,
    liquifee,
    infrafee,
    market_trading_mode,
    market_state,
    adp,
    mdp,
    file,
    els=None,
):
    """
    Record output data from current LP strategy in a CSV file.

    Args:
         Input data have 2 types: float or list
    """
    if isinstance(realisedPnl, list):
        realisedPnl = [i / 10**adp for i in realisedPnl]
    else:
        realisedPnl /= 10**adp

    if isinstance(unrealisedPnl, list):
        unrealisedPnl = [i / 10**adp for i in unrealisedPnl]
    else:
        unrealisedPnl /= 10**adp

    if isinstance(Averageentryprice, list):
        Averageentryprice = [i / 10**mdp for i in Averageentryprice]
    else:
        Averageentryprice /= 10**mdp

    markprice /= 10**mdp
    infrafee /= 10**adp

    if isinstance(inventory, list):
        num_lps = len(inventory)

        data = [
            iteration,
            time_step,
        ]

        GA = [general_account[i] for i in range(num_lps)]
        MA = [margin_account[i] for i in range(num_lps)]
        BA = [bond_account[i] for i in range(num_lps)]
        PNL = [generalPnl[i] for i in range(num_lps)]
        REPNL = [realisedPnl[i] for i in range(num_lps)]
        UNPNL = [unrealisedPnl[i] for i in range(num_lps)]
        POS = [inventory[i] for i in range(num_lps)]
        BID = [bid_depth[i] for i in range(num_lps)]
        ASK = [ask_depth[i] for i in range(num_lps)]
        ENTRY = [Averageentryprice[i] for i in range(num_lps)]
        ELS = [els[i] for i in range(num_lps)]

        data = data + GA + MA + BA + PNL + REPNL + UNPNL + POS + BID + ASK + ENTRY + ELS

        data += [
            buying_MO,
            selling_MO,
            LOs_bid,
            LOs_ask,
            midprice,
            markprice,
            insurance,
            liquifee,
            infrafee,
            market_trading_mode,
            market_state,
        ]

    else:
        data = [
            iteration,
            time_step,
            general_account,
            margin_account,
            bond_account,
            generalPnl,
            realisedPnl,
            unrealisedPnl,
            inventory,
            bid_depth,
            ask_depth,
            buying_MO,
            selling_MO,
            LOs_bid,
            LOs_ask,
            midprice,
            markprice,
            Averageentryprice,
            insurance,
            liquifee,
            infrafee,
            market_trading_mode,
            market_state,
        ]

    with open(file, "a", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(data)


def log_infotrader_MMmodel(
    iteration,
    time_step,
    general_account_lp,
    margin_account_lp,
    bond_account_lp,
    pnl_lp,
    realisedPnl_lp,
    unrealisedPnl_lp,
    inventory_lp,
    general_account_info,
    margin_account_info,
    pnl_info,
    realisedPnl_info,
    unrealisedPnl_info,
    inventory_info,
    bid_depth,
    ask_depth,
    buying_MO,
    selling_MO,
    buying_MO_info,
    selling_MO_info,
    LOs_bid,
    LOs_ask,
    midprice,
    markprice,
    Averageentryprice,
    insurance,
    liquifee,
    infrafee,
    market_trading_mode,
    market_state,
    adp,
    mdp,
    file,
):
    """
    Record output data from current sim in a CSV file.
    """

    realisedPnl_lp /= 10**adp
    unrealisedPnl_lp /= 10**adp
    Averageentryprice /= 10**mdp

    realisedPnl_info /= 10**adp
    unrealisedPnl_info /= 10**adp

    markprice /= 10**mdp
    infrafee /= 10**adp

    data = [
        iteration,
        time_step,
        general_account_lp,
        margin_account_lp,
        bond_account_lp,
        pnl_lp,
        realisedPnl_lp,
        unrealisedPnl_lp,
        inventory_lp,
        general_account_info,
        margin_account_info,
        pnl_info,
        realisedPnl_info,
        unrealisedPnl_info,
        inventory_info,
        bid_depth,
        ask_depth,
        buying_MO,
        selling_MO,
        buying_MO_info,
        selling_MO_info,
        LOs_bid,
        LOs_ask,
        midprice,
        markprice,
        Averageentryprice,
        insurance,
        liquifee,
        infrafee,
        market_trading_mode,
        market_state,
    ]

    with open(file, "a", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(data)
