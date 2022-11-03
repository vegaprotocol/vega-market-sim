import functools
import vega_sim.proto.vega as vega_protos
from typing import Any, Callable, Dict, List, Optional
from vega_sim.null_service import VegaServiceNull
from vega_sim.environment.agent import Agent
from vega_sim.scenario.common.agents import ExponentialShapedMarketMaker
from vega_sim.scenario.ideal_market_maker.agents import OptimalMarketMaker
from vega_sim.scenario.ideal_market_maker_v2.agents import (
    OptimalMarketMaker as OptimalMarketMakerV2,
)
from vega_sim.scenario.common.agents import (
    MomentumTrader,
    MarketOrderTrader,
    InformedTrader,
)


BASE_IDEAL_MM_CSV_HEADERS = [
    "Time Step",
    "LP: General Account",
    "LP: Margin Account",
    "LP: Margin Rate",
    "LP: Max Margin",
    "LP: Max Locked Capital",
    "LP: Bond Account",
    "LP: GeneralPnl",
    "LP: Return Over LockedCapital",
    "LP: Annualised Return Over LockedCapital",
    "LP: Relative Return",
    "LP: Annualised Relative Return",
    "LP: RealisedPnl",
    "LP: UnrealisedPnl",
    "LP: Position",
    "LP: Bid",
    "LP: Ask",
    "External Midprice",
    "Midprice",
    "Markprice",
    "LP: entry price",
    "InsurancePool",
    "LiquifeeAccount",
    "InfrafeeAccount",
    "Total Traded Notional",
    "Informed Trader Notional",
    "Target Stake",
    "Market Open Interest",
    "Market Trading mode",
    "Market State",
]

LOB_CSV_HEADERS = [
    "Time Step",
    "Order Book Bid Side",
    "Order Book Ask Side",
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
    state_values: List = None,
    additional_data_fns: List[
        Optional[Callable[[VegaServiceNull, List[Agent]], Dict[str, Any]]]
    ] = None,
) -> Dict[str, Any]:
    mm_agent = [
        agent
        for agent in agents
        if isinstance(
            agent,
            (OptimalMarketMakerV2, OptimalMarketMaker, ExponentialShapedMarketMaker),
        )
    ][0]

    # informed_agent = [
    #     agent
    #     for agent in agents
    #     if isinstance(
    #         agent,
    #         (InformedTrader),
    #     )
    # ][0]

    general_lp, margin_lp, bond_lp = vega.party_account(
        wallet_name=mm_agent.wallet_name,
        asset_id=mm_agent.asset_id,
        market_id=mm_agent.market_id,
        key_name=mm_agent.key_name,
    )

    position = vega.positions_by_market(
        wallet_name=mm_agent.wallet_name,
        market_id=mm_agent.market_id,
        key_name=mm_agent.key_name,
    )
    if not position:
        realised_pnl_lp = 0
        unrealised_pnl_lp = 0
        inventory_lp = 0
        entry_price = 0
    else:
        realised_pnl_lp = round(float(position[0].realised_pnl), mm_agent.adp)
        unrealised_pnl_lp = round(float(position[0].unrealised_pnl), mm_agent.adp)
        inventory_lp = float(position[0].open_volume)
        entry_price = float(position[0].average_entry_price) / 10**mm_agent.mdp

    market_state = vega.market_info(market_id=mm_agent.market_id).state
    market_data = vega.market_data(market_id=mm_agent.market_id)
    markprice = float(market_data.mark_price) / 10**mm_agent.mdp
    mid_price = float(market_data.mid_price) / 10**mm_agent.mdp
    trading_mode = market_data.market_trading_mode

    liquifee, insurance = [
        int(account.balance)
        for account in vega.market_accounts(
            asset_id=mm_agent.asset_id, market_id=mm_agent.market_id
        )
    ]

    infrafee = int(
        vega.infrastructure_fee_accounts(asset_id=mm_agent.asset_id)[0].balance
    )
    if hasattr(mm_agent, "adp"):
        infrafee /= 10**mm_agent.adp
    infrafee_rate = float(
        vega.market_info(market_id=mm_agent.market_id).fees.factors.infrastructure_fee
    )
    traded_notional = round(infrafee / infrafee_rate, 3)
    margin_rate = float(margin_lp / (margin_lp + bond_lp + general_lp))

    additional_fns = additional_data_fns if additional_data_fns is not None else []

    if len(state_values) == 0:
        max_locked_capital = margin_lp + bond_lp
        max_margin = margin_lp
    else:
        old_logs = state_values[mm_agent.current_step - 2]
        max_locked_capital = old_logs["LP: Max Locked Capital"]
        max_locked_capital = max(margin_lp + bond_lp, max_locked_capital)
        max_margin = old_logs["LP: Max Margin"]
        max_margin = max(margin_lp, max_margin)

    base_logs = {
        "Time Step": mm_agent.current_step,
        "LP: General Account": general_lp,
        "LP: Margin Account": margin_lp,
        "LP: Margin Rate": margin_rate,
        "LP: Bond Account": bond_lp,
        "LP: GeneralPnl": general_lp
        + margin_lp
        + bond_lp
        - mm_agent.initial_asset_mint,
        "LP: Return Over LockedCapital": (
            general_lp + margin_lp + bond_lp - mm_agent.initial_asset_mint
        )
        / (max_locked_capital + 0.000000001),
        "LP: Annualised Return Over LockedCapital": (
            general_lp + margin_lp + bond_lp - mm_agent.initial_asset_mint
        )
        * 365
        / (max_locked_capital + 0.000000001),
        "LP: Relative Return": (
            general_lp + margin_lp + bond_lp - mm_agent.initial_asset_mint
        )
        / (mm_agent.initial_asset_mint + 0.00000001),
        "LP: Annualised Relative Return": (
            general_lp + margin_lp + bond_lp - mm_agent.initial_asset_mint
        )
        * 365
        / (mm_agent.initial_asset_mint + 0.00000001),
        "LP: Max Margin": max_margin,
        "LP: Max Locked Capital": max_locked_capital,
        "LP: RealisedPnl": realised_pnl_lp,
        "LP: UnrealisedPnl": unrealised_pnl_lp,
        "LP: Position": inventory_lp,
        "LP: Bid": -round(mm_agent.bid_depth, mm_agent.mdp),
        "LP: Ask": round(mm_agent.ask_depth, mm_agent.mdp),
        "External Midprice": mm_agent.price_process[mm_agent.current_step - 1]
        if hasattr(mm_agent, "price_process")
        else None,
        "Midprice": mid_price,
        "Markprice": markprice,
        "LP: entry price": entry_price,
        "InsurancePool": insurance,
        "LiquifeeAccount": liquifee,
        "InfrafeeAccount": infrafee,
        "Total Traded Notional": traded_notional,
        "Informed Trader Notional": traded_notional,
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
        if isinstance(
            agent,
            (OptimalMarketMakerV2, OptimalMarketMaker, ExponentialShapedMarketMaker),
        )
    ][0]
    market_data = vega.market_data(market_id=mm_agent.market_id)
    scaling = 1 / 10 ** mm_agent.adp if hasattr(mm_agent, "adp") else 1

    return {
        "Target Stake": float(market_data.target_stake) * scaling,
    }


def tau_scaling_additional_data(
    vega: VegaServiceNull,
    agents: List[Agent],
) -> Dict[str, Any]:
    mm_agent = [
        agent
        for agent in agents
        if isinstance(
            agent,
            (OptimalMarketMakerV2, OptimalMarketMaker, ExponentialShapedMarketMaker),
        )
    ][0]
    market_data = vega.market_data(market_id=mm_agent.market_id)
    market_info = vega.market_info(market_id=mm_agent.market_id)

    return {
        "Market Open Interest": int(market_data.open_interest)
        / 10**market_info.position_decimal_places
    }


def limit_order_book(
    vega: VegaServiceNull,
    agents: List[Agent],
) -> Dict[str, Any]:
    mm_agent = [
        agent
        for agent in agents
        if isinstance(
            agent,
            (OptimalMarketMakerV2, OptimalMarketMaker, ExponentialShapedMarketMaker),
        )
    ][0]
    order_book = []
    for _, orders in (
        vega.order_status_from_feed(live_only=True).get(mm_agent.market_id, {}).items()
    ):
        order_book += list(orders.values())

    LOB_bids = {}
    LOB_asks = {}

    for order in order_book:
        order_remaining = (
            round(order.remaining, mm_agent.market_position_decimal)
            if hasattr(mm_agent, "market_position_decimal")
            else order.remaining
        )
        if order.side == vega_protos.vega.Side.SIDE_BUY:
            if order.price not in LOB_bids:
                LOB_bids[order.price] = order_remaining
            else:
                LOB_bids[order.price] += order_remaining
        else:
            if order.price not in LOB_asks:
                LOB_asks[order.price] = order_remaining
            else:
                LOB_asks[order.price] += order_remaining

    return {
        "Order Book Bid Side": LOB_bids,
        "Order Book Ask Side": LOB_asks,
    }


def momentum_trader_data_extraction(
    vega: VegaServiceNull,
    agents: List[Agent],
) -> Dict[str, Any]:
    trader = [agent for agent in agents if isinstance(agent, MomentumTrader)][0]

    general, margin, _ = vega.party_account(
        wallet_name=trader.wallet_name,
        asset_id=trader.asset_id,
        market_id=trader.market_id,
    )

    position = vega.positions_by_market(
        wallet_name=trader.wallet_name, market_id=trader.market_id
    )

    if not position:
        realised_pnl = 0
        unrealised_pnl = 0
        inventory = 0
        entry_price = 0
    else:
        realised_pnl = round(float(position[0].realised_pnl), trader.adp)
        unrealised_pnl = round(float(position[0].unrealised_pnl), trader.adp)
        inventory = float(position[0].open_volume)
        entry_price = float(position[0].average_entry_price) / 10**trader.mdp

    market_data = vega.market_data(market_id=trader.market_id)
    markprice = float(market_data.mark_price) / 10**trader.mdp
    mid_price = float(market_data.mid_price) / 10**trader.mdp
    trading_mode = market_data.market_trading_mode

    market_state = vega.market_info(market_id=trader.market_id).state

    logs = {
        "MT: General Account": general,
        "MT: Margin Account": margin,
        "MT: GeneralPnl": general + margin - trader.initial_asset_mint,
        "MT: RealisedPnl": realised_pnl,
        "MT: UnrealisedPnl": unrealised_pnl,
        "MT: Position": inventory,
        "MT: entry price": entry_price,
        "MT: Indicator": trader.indicators[-1],
        "MidPrice": mid_price,
        "Markprice": markprice,
        "Market State": market_state,
        "Market Trading Mode": trading_mode,
    }
    return logs


def uninformed_tradingbot_data_extraction(
    vega: VegaServiceNull,
    agents: List[Agent],
) -> Dict[str, Any]:
    trader = [agent for agent in agents if isinstance(agent, MarketOrderTrader)][0]

    general, margin, _ = vega.party_account(
        wallet_name=trader.wallet_name,
        asset_id=trader.asset_id,
        market_id=trader.market_id,
    )

    position = vega.positions_by_market(
        wallet_name=trader.wallet_name, market_id=trader.market_id
    )

    if not position:
        realised_pnl = 0
        unrealised_pnl = 0
        inventory = 0
        entry_price = 0
    else:
        realised_pnl = round(float(position[0].realised_pnl), trader.adp)
        unrealised_pnl = round(float(position[0].unrealised_pnl), trader.adp)
        inventory = float(position[0].open_volume)
        entry_price = float(position[0].average_entry_price) / 10**trader.mdp

    logs = {
        "UT: General Account": general,
        "UT: Margin Account": margin,
        "UT: GeneralPnl": general + margin - trader.initial_asset_mint,
        "UT: RealisedPnl": realised_pnl,
        "UT: UnrealisedPnl": unrealised_pnl,
        "UT: Position": inventory,
        "UT: entry price": entry_price,
    }
    return logs
