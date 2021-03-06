import functools
from typing import Any, Callable, Dict, List, Optional
from vega_sim.null_service import VegaServiceNull
from vega_sim.environment.agent import Agent
from vega_sim.scenario.ideal_market_maker.agents import OptimalMarketMaker
from vega_sim.scenario.ideal_market_maker_v2.agents import (
    OptimalMarketMaker as OptimalMarketMakerV2,
)


BASE_IDEAL_MM_CSV_HEADERS = [
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
    "External Midprice",
    "Markprice",
    "Average Entry price",
    "InsurancePool",
    "LiquifeeAccount",
    "InfrafeeAccount",
    "Market Trading mode",
    "Market State",
]


def ideal_market_maker_single_data_extraction(
    additional_data_fns: Optional[
        List[Callable[[VegaServiceNull, List[Agent]], Dict[str, Any]]]
    ] = None,
) -> Callable[[VegaServiceNull, List[Agent]], Dict[str, Any]]:
    return functools.partial(
        _ideal_market_maker_single_data_extraction,
        additional_data_fns=additional_data_fns,
    )


def _ideal_market_maker_single_data_extraction(
    vega: VegaServiceNull,
    agents: List[Agent],
    additional_data_fns: List[
        Optional[Callable[[VegaServiceNull, List[Agent]], Dict[str, Any]]]
    ] = None,
) -> Dict[str, Any]:
    mm_agent = [
        agent
        for agent in agents
        if isinstance(agent, (OptimalMarketMakerV2, OptimalMarketMaker))
    ][0]

    general_lp, margin_lp, bond_lp = vega.party_account(
        wallet_name=mm_agent.wallet_name,
        asset_id=mm_agent.tdai_id,
        market_id=mm_agent.market_id,
    )

    position = vega.positions_by_market(
        wallet_name=mm_agent.wallet_name, market_id=mm_agent.market_id
    )
    if not position:
        realised_pnl_lp = 0
        unrealised_pnl_lp = 0
        inventory_lp = 0
        entry_price = 0
    else:
        realised_pnl_lp = float(position[0].realised_pnl)
        unrealised_pnl_lp = float(position[0].unrealised_pnl)
        inventory_lp = int(position[0].open_volume)
        entry_price = float(position[0].average_entry_price)

    market_state = vega.market_info(market_id=mm_agent.market_id).state
    market_data = vega.market_data(market_id=mm_agent.market_id)
    markprice = float(market_data.mark_price)
    trading_mode = market_data.market_trading_mode

    liquifee, insurance = [
        int(account.balance)
        for account in vega.market_accounts(
            asset_id=mm_agent.tdai_id, market_id=mm_agent.market_id
        )
    ]

    infrafee = int(
        vega.infrastructure_fee_accounts(asset_id=mm_agent.tdai_id)[0].balance
    )

    realised_pnl_lp /= 10**mm_agent.adp
    unrealised_pnl_lp /= 10**mm_agent.adp
    entry_price /= 10**mm_agent.mdp

    markprice /= 10**mm_agent.mdp
    infrafee /= 10**mm_agent.adp

    additional_fns = additional_data_fns if additional_data_fns is not None else []
    base_logs = {
        "Time Step": mm_agent.current_step,
        "LP: General Account": general_lp,
        "LP: Margin Account": margin_lp,
        "LP: Bond Account": bond_lp,
        "LP: General Pnl": general_lp
        + margin_lp
        + bond_lp
        - mm_agent.initial_asset_mint,
        "LP: RealisedPnl": realised_pnl_lp,
        "LP: UnrealisedPnl": unrealised_pnl_lp,
        "LP: Position": inventory_lp,
        "LP: Bid Depth": -mm_agent.bid_depth,
        "LP: Ask Depth": mm_agent.ask_depth,
        "External Midprice": mm_agent.price_process[mm_agent.current_step - 1],
        "Markprice": markprice,
        "Average Entry price": entry_price,
        "InsurancePool": insurance,
        "LiquifeeAccount": liquifee,
        "InfrafeeAccount": infrafee,
        "Market Trading mode": trading_mode,
        "Market State": market_state,
    }
    for data_fn in additional_fns:
        base_logs.update(data_fn(vega, agents))

    return base_logs


def v1_ideal_mm_additional_data(
    vega: VegaServiceNull,
    agents: List[Agent],
) -> Dict[str, Any]:
    mm_agent = [agent for agent in agents if isinstance(agent, OptimalMarketMaker)][0]

    return {
        "Buying MOs": mm_agent.num_buyMO,
        "Selling MOs": mm_agent.num_sellMO,
        "LOs at bid": mm_agent.num_bidhit,
        "LOs at ask": mm_agent.num_askhit,
    }


def target_stake_additional_data(
    vega: VegaServiceNull,
    agents: List[Agent],
) -> Dict[str, Any]:
    mm_agent = [
        agent
        for agent in agents
        if isinstance(agent, (OptimalMarketMakerV2, OptimalMarketMaker))
    ][0]
    market_data = vega.market_data(market_id=mm_agent.market_id)

    return {
        "Target Stake": float(market_data.target_stake) / 10**mm_agent.adp,
    }


def tau_scaling_additional_data(
    vega: VegaServiceNull,
    agents: List[Agent],
) -> Dict[str, Any]:
    mm_agent = [
        agent
        for agent in agents
        if isinstance(agent, (OptimalMarketMakerV2, OptimalMarketMaker))
    ][0]
    market_data = vega.market_data(market_id=mm_agent.market_id)
    market_info = vega.market_info(market_id=mm_agent.market_id)

    return {
        "Market Open Interest": int(market_data.open_interest)
        / 10**market_info.position_decimal_places
    }
