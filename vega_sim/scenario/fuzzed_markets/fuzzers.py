from uuid import uuid4
from numpy.random import RandomState
from vega_sim.service import VegaService

import vega_sim.builders as build
import vega_sim.proto.vega as vega_protos


def valid(rs, bias) -> bool:
    if rs.rand() < bias:
        return True
    return False


def fuzz_dispatch_strategy(
    vega: VegaService, rs: RandomState, bias: float
) -> vega_protos.vega.DispatchStrategy:
    def _pick_metric():
        values = vega_protos.vega.DispatchMetric.values()
        if valid(rs, bias):
            values.pop(0)
        return rs.choice(values)

    def _pick_distribution_strategy():
        values = vega_protos.vega.DistributionStrategy.values()
        if valid(rs, bias):
            if metric == vega_protos.vega.DISPATCH_METRIC_MARKET_VALUE:
                return None
            values.pop(0)
        return rs.choice(values)

    def _pick_entity_scope():
        values = vega_protos.vega.EntityScope.values()
        # TODO: Once team games enabled, remove this field
        values.pop(vega_protos.vega.ENTITY_SCOPE_TEAMS)
        if valid(rs, bias):
            if metric == vega_protos.vega.DISPATCH_METRIC_VALIDATOR_RANKING:
                return vega_protos.vega.ENTITY_SCOPE_INDIVIDUALS
            values.pop(0)
        return rs.choice(values)

    def _pick_individual_scope():
        values = vega_protos.vega.IndividualScope.values()
        if valid(rs, bias):
            if entity_scope != vega_protos.vega.ENTITY_SCOPE_INDIVIDUALS:
                return None
            values.pop(0)
        return rs.choice(values)

    def _pick_asset_for_metric():
        if len(asset_ids) == 0:
            return None
        if valid(rs, bias):
            if metric in [
                vega_protos.vega.DISPATCH_METRIC_MARKET_VALUE,
                vega_protos.vega.DISPATCH_METRIC_VALIDATOR_RANKING,
            ]:
                return None
        return rs.choice(asset_ids)

    def _pick_markets():
        if len(market_ids) == 0:
            return None
        val = [rs.choice(market_ids)]
        return None if rs.rand() < 0.8 else val

    def _pick_team_scope():
        if len(team_ids) == 0:
            return None
        if valid(rs, bias):
            if entity_scope != vega_protos.vega.ENTITY_SCOPE_TEAMS:
                return None
        val = [rs.choice(team_ids)]
        return None if rs.rand() < 0.8 else val

    def _pick_n_top_performers():
        val = rs.rand()
        if valid(rs, bias):
            if entity_scope == vega_protos.vega.ENTITY_SCOPE_INDIVIDUALS:
                return None
            return val
        return None if rs.rand() < 0.5 else val

    def _pick_staking_requirement():
        lower_bound = -10
        if valid(rs, bias):
            if metric in [
                vega_protos.vega.DISPATCH_METRIC_MARKET_VALUE,
                vega_protos.vega.DISPATCH_METRIC_VALIDATOR_RANKING,
            ]:
                return None
            lower_bound = 0
        val = rs.randint(low=lower_bound, high=100)
        return None if rs.rand() < 0.8 else val

    def _pick_notional_time_weighted_average_position_requirement():
        lower_bound = -10
        if valid(rs, bias):
            if metric in [
                vega_protos.vega.DISPATCH_METRIC_MARKET_VALUE,
                vega_protos.vega.DISPATCH_METRIC_VALIDATOR_RANKING,
            ]:
                return None
            lower_bound = 0
        val = rs.randint(low=lower_bound, high=100)
        return None if rs.rand() < 0.8 else val

    def _pick_window_length():
        lower_bound = 0
        if valid(rs, bias):
            lower_bound = 1
            if metric == vega_protos.vega.DISPATCH_METRIC_MARKET_VALUE:
                return None
            if metric == vega_protos.vega.DISPATCH_METRIC_RETURN_VOLATILITY:
                lower_bound = 2
        return rs.randint(low=lower_bound, high=10)

    def _pick_lock_period():
        return rs.randint(low=0, high=10)

    def _pick_rank_table():
        val = [vega_protos.vega.Rank(start_rank=1, share_ratio=rs.randint(1, 10))]
        for _ in range(rs.randint(0, 10)):
            val.append(
                vega_protos.vega.Rank(
                    start_rank=val[-1].start_rank + rs.randint(1, 10),
                    share_ratio=rs.randint(1, 10),
                )
            )
        if valid(rs, bias):
            if distribution_strategy != vega_protos.vega.DISTRIBUTION_STRATEGY_RANK:
                return None
            return val
        return None if rs.rand() < 0.5 else val

    # Get current statistics
    asset_ids = [value for _, value in vega.market_to_asset.items()]
    market_ids = [key for key, _ in vega.market_to_asset.items()]
    team_ids = [team.id for team in vega.list_teams()]

    # Pick driver fields
    metric = _pick_metric()
    asset_for_metric = _pick_asset_for_metric()
    entity_scope = _pick_entity_scope()

    # Pick driven fields
    individual_scope = _pick_individual_scope()
    team_scope = _pick_team_scope()
    n_top_performers = _pick_n_top_performers()
    staking_requirement = _pick_staking_requirement()
    notional_time_weighted_average_position_requirement = (
        _pick_notional_time_weighted_average_position_requirement()
    )
    window_length = _pick_window_length()
    lock_period = _pick_lock_period()
    distribution_strategy = _pick_distribution_strategy()
    rank_table = _pick_rank_table()
    markets = _pick_markets()

    return build.vega.dispatch_strategy(
        asset_for_metric=asset_for_metric,
        metric=metric,
        entity_scope=entity_scope,
        individual_scope=individual_scope,
        team_scope=team_scope,
        n_top_performers=n_top_performers,
        staking_requirement=staking_requirement,
        notional_time_weighted_average_position_requirement=notional_time_weighted_average_position_requirement,
        window_length=window_length,
        lock_period=lock_period,
        distribution_strategy=distribution_strategy,
        markets=markets,
        rank_table=rank_table,
    )


def fuzz_recurring_transfer(
    vega: VegaService, rs: RandomState, bias: float
) -> vega_protos.commands.v1.commands.RecurringTransfer:
    def _pick_start_epoch():
        low = 1 if valid(rs, bias) else -5
        return current_epoch + rs.randint(low, 10)

    def _pick_end_epoch():
        low = 1 if valid(rs, bias) else -5
        val = start_epoch + rs.randint(low, 10)
        return None if rs.rand() < 0.5 else val

    def _pick_factor():
        return rs.rand()

    def _pick_dispatch_strategy():
        val = fuzz_dispatch_strategy(vega=vega, rs=rs, bias=bias)
        return None if rs.rand() < 0.5 else val

    # Get data
    current_epoch = vega.statistics().epoch_seq

    # Pick driver fields
    start_epoch = _pick_start_epoch()
    factor = _pick_factor()
    dispatch_strategy = _pick_dispatch_strategy()

    # Pick driven fields
    end_epoch = _pick_end_epoch()

    return build.commands.commands.recurring_transfer(
        start_epoch=start_epoch,
        factor=factor,
        end_epoch=end_epoch,
        dispatch_strategy=dispatch_strategy,
    )


def fuzz_transfer(
    vega: VegaService, rs: RandomState, bias: float
) -> vega_protos.commands.v1.commands.Transfer:
    def _pick_from_account_type():
        if valid(rs, bias):
            return rs.choice(
                [
                    vega_protos.vega.ACCOUNT_TYPE_GENERAL,
                    vega_protos.vega.ACCOUNT_TYPE_VESTED_REWARDS,
                ]
            )
        return rs.choice(vega_protos.vega.AccountType.values())

    def _pick_to():
        # TODO: Support fuzzed transfers to general accounts
        return "0000000000000000000000000000000000000000000000000000000000000000"

    def _pick_to_account_type():
        if valid(rs, bias):
            if recurring is not None and recurring.dispatch_strategy is not None:
                if (
                    recurring.dispatch_strategy.metric
                    == vega_protos.vega.DISPATCH_METRIC_MARKET_VALUE
                ):
                    return vega_protos.vega.ACCOUNT_TYPE_REWARD_MARKET_PROPOSERS
                if (
                    recurring.dispatch_strategy.metric
                    == vega_protos.vega.DISPATCH_METRIC_MAKER_FEES_PAID
                ):
                    return vega_protos.vega.ACCOUNT_TYPE_REWARD_MAKER_PAID_FEES
                if (
                    recurring.dispatch_strategy.metric
                    == vega_protos.vega.DISPATCH_METRIC_MAKER_FEES_RECEIVED
                ):
                    return vega_protos.vega.ACCOUNT_TYPE_REWARD_MAKER_RECEIVED_FEES
                if (
                    recurring.dispatch_strategy.metric
                    == vega_protos.vega.DISPATCH_METRIC_LP_FEES_RECEIVED
                ):
                    return vega_protos.vega.ACCOUNT_TYPE_REWARD_LP_RECEIVED_FEES
                if (
                    recurring.dispatch_strategy.metric
                    == vega_protos.vega.DISPATCH_METRIC_AVERAGE_POSITION
                ):
                    return vega_protos.vega.ACCOUNT_TYPE_REWARD_AVERAGE_POSITION
                if (
                    recurring.dispatch_strategy.metric
                    == vega_protos.vega.DISPATCH_METRIC_RELATIVE_RETURN
                ):
                    return vega_protos.vega.ACCOUNT_TYPE_REWARD_RELATIVE_RETURN
                if (
                    recurring.dispatch_strategy.metric
                    == vega_protos.vega.DISPATCH_METRIC_RETURN_VOLATILITY
                ):
                    return vega_protos.vega.ACCOUNT_TYPE_REWARD_RETURN_VOLATILITY
                if (
                    recurring.dispatch_strategy.metric
                    == vega_protos.vega.DISPATCH_METRIC_VALIDATOR_RANKING
                ):
                    return vega_protos.vega.ACCOUNT_TYPE_REWARD_VALIDATOR_RANKING
            return rs.choice(
                [
                    vega_protos.vega.ACCOUNT_TYPE_NETWORK_TREASURY,
                    vega_protos.vega.ACCOUNT_TYPE_GLOBAL_INSURANCE,
                    vega_protos.vega.ACCOUNT_TYPE_GLOBAL_REWARD,
                ]
            )
        return rs.choice(vega_protos.vega.AccountType.values())

    def _pick_asset():
        if len(asset_ids) == 0:
            return None
        return rs.choice(asset_ids)

    def _pick_amount():
        return rs.rand() * 1000

    def _pick_reference():
        return str(uuid4())

    def _pick_one_off():
        return None if rs.rand() < 1 else None

    def _pick_recurring():
        val = fuzz_recurring_transfer(vega=vega, rs=rs, bias=bias)
        return None if rs.rand() < 0 else val

    # Get network info
    asset_ids = [value for _, value in vega.market_to_asset.items()]

    # Pick driving fields
    one_off = _pick_one_off()
    recurring = _pick_recurring()

    # Pick driven fields
    from_account_type = _pick_from_account_type()
    to = _pick_to()
    to_account_type = _pick_to_account_type()
    asset = _pick_asset()
    amount = _pick_amount()
    reference = _pick_reference()

    return build.commands.commands.transfer(
        asset_decimals=vega.asset_decimals,
        from_account_type=from_account_type,
        to=to,
        to_account_type=to_account_type,
        asset=asset,
        amount=amount,
        reference=reference,
        one_off=one_off,
        recurring=recurring,
    )


def fuzz_governance_one_off_transfer(
    vega: VegaService, rs: RandomState, bias: float
) -> vega_protos.governance.OneOffTransfer:
    deliver_on = None
    return build.governance.one_off_transfer(deliver_on=deliver_on)


def fuzz_governance_recurring_transfer(
    vega: VegaService, rs: RandomState, bias: float
) -> vega_protos.governance.RecurringTransfer:
    def _pick_start_epoch():
        low = 1 if valid(rs, bias) else -5
        return current_epoch + rs.randint(low, 10)

    def _pick_end_epoch():
        low = 1 if valid(rs, bias) else -5
        val = start_epoch + rs.randint(low, 10)
        return None if rs.rand() < 0.5 else val

    def _pick_factor():
        val = rs.rand()
        return None if rs.rand() < 0.5 else val

    def _pick_dispatch_strategy():
        val = fuzz_dispatch_strategy(vega=vega, rs=rs, bias=bias)
        return None if rs.rand() < 0.5 else val

    # Get data
    current_epoch = vega.statistics().epoch_seq

    # Pick driver fields
    start_epoch = _pick_start_epoch()
    dispatch_strategy = _pick_dispatch_strategy()

    # Pick driven fields
    end_epoch = _pick_end_epoch()

    return build.governance.recurring_transfer(
        start_epoch=start_epoch,
        end_epoch=end_epoch,
        dispatch_strategy=dispatch_strategy,
    )


def fuzz_new_transfer_configuration(
    vega: VegaService, rs: RandomState, bias: float
) -> vega_protos.governance.NewTransferConfiguration:
    def _pick_source():
        if valid(rs, bias):
            if source_type == vega_protos.vega.ACCOUNT_TYPE_INSURANCE:
                return rs.choice(market_ids)
        return None

    def _pick_source_type():
        if valid(rs, bias):
            if destination_type == vega_protos.vega.ACCOUNT_TYPE_NETWORK_TREASURY:
                return rs.choice(
                    [
                        vega_protos.vega.ACCOUNT_TYPE_INSURANCE,
                        vega_protos.vega.ACCOUNT_TYPE_GLOBAL_INSURANCE,
                    ]
                )
            if destination_type == vega_protos.vega.ACCOUNT_TYPE_INSURANCE:
                return rs.choice(
                    [
                        vega_protos.vega.ACCOUNT_TYPE_NETWORK_TREASURY,
                        vega_protos.vega.ACCOUNT_TYPE_GLOBAL_INSURANCE,
                    ]
                )
            if destination_type == vega_protos.vega.ACCOUNT_TYPE_GLOBAL_INSURANCE:
                return rs.choice(
                    [
                        vega_protos.vega.ACCOUNT_TYPE_NETWORK_TREASURY,
                        vega_protos.vega.ACCOUNT_TYPE_INSURANCE,
                    ]
                )
            return rs.choice(
                [
                    vega_protos.vega.ACCOUNT_TYPE_NETWORK_TREASURY,
                    vega_protos.vega.ACCOUNT_TYPE_INSURANCE,
                    vega_protos.vega.ACCOUNT_TYPE_GLOBAL_INSURANCE,
                ]
            )
        return rs.choice(vega_protos.vega.AccountType.values())

    def _pick_transfer_type():
        values = vega_protos.governance.GovernanceTransferType.values()
        if valid(rs, bias):
            values.pop(0)
        return rs.choice(values)

    def _pick_amount():
        return rs.rand() * 1000

    def _pick_asset():
        if len(asset_ids) == 0:
            return None
        return rs.choice(asset_ids)

    def _pick_fraction_of_balance():
        return rs.rand()

    def _pick_destination_type():
        if valid(rs, bias):
            if recurring is not None and recurring.dispatch_strategy is not None:
                if (
                    recurring.dispatch_strategy.metric
                    == vega_protos.vega.DISPATCH_METRIC_MARKET_VALUE
                ):
                    return vega_protos.vega.ACCOUNT_TYPE_REWARD_MARKET_PROPOSERS
                if (
                    recurring.dispatch_strategy.metric
                    == vega_protos.vega.DISPATCH_METRIC_MAKER_FEES_PAID
                ):
                    return vega_protos.vega.ACCOUNT_TYPE_REWARD_MAKER_PAID_FEES
                if (
                    recurring.dispatch_strategy.metric
                    == vega_protos.vega.DISPATCH_METRIC_MAKER_FEES_RECEIVED
                ):
                    return vega_protos.vega.ACCOUNT_TYPE_REWARD_MAKER_RECEIVED_FEES
                if (
                    recurring.dispatch_strategy.metric
                    == vega_protos.vega.DISPATCH_METRIC_LP_FEES_RECEIVED
                ):
                    return vega_protos.vega.ACCOUNT_TYPE_REWARD_LP_RECEIVED_FEES
                if (
                    recurring.dispatch_strategy.metric
                    == vega_protos.vega.DISPATCH_METRIC_AVERAGE_POSITION
                ):
                    return vega_protos.vega.ACCOUNT_TYPE_REWARD_AVERAGE_POSITION
                if (
                    recurring.dispatch_strategy.metric
                    == vega_protos.vega.DISPATCH_METRIC_RELATIVE_RETURN
                ):
                    return vega_protos.vega.ACCOUNT_TYPE_REWARD_RELATIVE_RETURN
                if (
                    recurring.dispatch_strategy.metric
                    == vega_protos.vega.DISPATCH_METRIC_RETURN_VOLATILITY
                ):
                    return vega_protos.vega.ACCOUNT_TYPE_REWARD_RETURN_VOLATILITY
                if (
                    recurring.dispatch_strategy.metric
                    == vega_protos.vega.DISPATCH_METRIC_VALIDATOR_RANKING
                ):
                    return vega_protos.vega.ACCOUNT_TYPE_REWARD_VALIDATOR_RANKING
            return rs.choice(
                [
                    vega_protos.vega.ACCOUNT_TYPE_NETWORK_TREASURY,
                    vega_protos.vega.ACCOUNT_TYPE_GLOBAL_INSURANCE,
                    vega_protos.vega.ACCOUNT_TYPE_GLOBAL_REWARD,
                    vega_protos.vega.ACCOUNT_TYPE_INSURANCE,
                ]
            )

    def _pick_destination():
        # TODO: Support fuzzed transfers to general
        if valid(rs, bias):
            if destination_type == vega_protos.vega.ACCOUNT_TYPE_INSURANCE:
                return rs.choice(market_ids)
        return None

    def _pick_one_off():
        val = fuzz_governance_one_off_transfer(vega=vega, rs=rs, bias=bias)
        return None if rs.rand() < 1 else None

    def _pick_recurring():
        val = fuzz_governance_recurring_transfer(vega=vega, rs=rs, bias=bias)
        return None if rs.rand() < 0 else val

    # Get network information
    asset_ids = [value for _, value in vega.market_to_asset.items()]
    market_ids = [key for key, _ in vega.market_to_asset.items()]

    # Pick driver fields
    one_off = _pick_one_off()
    recurring = _pick_recurring()
    destination_type = _pick_destination_type()
    destination = _pick_destination()
    source_type = _pick_source_type()
    source = _pick_source()

    # Pick agnostic fields
    fraction_of_balance = _pick_fraction_of_balance()
    asset = _pick_asset()
    amount = _pick_amount()
    transfer_type = _pick_transfer_type()

    return build.governance.new_transfer_configuration(
        asset_decimals=vega.asset_decimals,
        source_type=source_type,
        transfer_type=transfer_type,
        amount=amount,
        asset=asset,
        fraction_of_balance=fraction_of_balance,
        destination_type=destination_type,
        source=source,
        destination=destination,
        one_off=one_off,
        recurring=recurring,
    )


def fuzz_order_submission(
    vega: VegaService, rs: RandomState, bias: float
) -> vega_protos.commands.v1.commands.OrderSubmission:
    def _pick_market_id():
        if len(market_ids) == 0:
            return None
        return rs.choice(market_ids)

    def _pick_type():
        return rs.choice(
            [
                vega_protos.vega.Order.Type.TYPE_MARKET,
                vega_protos.vega.Order.Type.TYPE_LIMIT,
            ],
            p=[0.2, 0.8],
        )

    def _pick_time_in_force():
        if rs.rand() < bias:
            if type_ == vega_protos.vega.Order.Type.TYPE_MARKET:
                return rs.choice(
                    [
                        vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_FOK,
                        vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_IOC,
                    ]
                )
        return rs.choice(vega_protos.vega.Order.TimeInForce.values())

    def _pick_price():
        if rs.rand() < bias:
            if type_ == vega_protos.vega.Order.Type.TYPE_MARKET:
                return None
            if pegged_order is not None:
                return None
        return rs.choice(
            [
                market_data.mid_price + rs.normal(loc=0, scale=10),
                rs.beta(a=0.001, b=0.001)
                * (2**64 - 1)
                / 10 ** vega.market_pos_decimals[market_id],
            ],
            p=[0.9, 0.1],
        )

    def _pick_size():
        min_order_size = 10 ** vega.market_pos_decimals[market_id]
        if (
            vega.market_data_from_feed(market_id).market_trading_mode
            != vega_protos.markets.Market.TradingMode.TRADING_MODE_CONTINUOUS
        ):
            return rs.choice(rs.poisson(100 * min_order_size))
        return rs.choice(
            [
                rs.poisson(100 * min_order_size),
                rs.beta(a=0.001, b=0.001)
                * (2**64 - 1)
                / 10 ** vega.market_pos_decimals[market_id],
            ],
            p=[0.9, 0.1],
        )

    def _pick_side():
        opts = vega_protos.vega.Side.values()
        if rs.rand() < bias:
            opts.pop(0)
        return rs.choice(opts)

    def _pick_pegged_order():
        return rs.choice(
            [
                build.commands.commands.pegged_order(
                    market_price_decimals=vega.market_price_decimals,
                    market_id=market_id,
                    reference=rs.choice(vega_protos.vega.PeggedReference.values()),
                    offset=rs.normal(loc=0, scale=10),
                ),
                None,
            ],
            p=[0.1, 0.9],
        )

    def _pick_reduce_only():
        if rs.rand() < bias:
            if (
                type_ == vega_protos.vega.Order.Type.TYPE_LIMIT
                and time_in_force
                not in [
                    vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_FOK,
                    vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_IOC,
                ]
            ):
                return False
        return rs.choice([True, False], p=[0.2, 0.8])

    def _pick_post_only():
        if rs.rand() < bias:
            if type_ == vega_protos.vega.Order.Type.TYPE_MARKET:
                return False
            if time_in_force in [
                vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_FOK,
                vega_protos.vega.Order.TimeInForce.TIME_IN_FORCE_IOC,
            ]:
                return False
        return rs.choice([True, False], p=[0.2, 0.8])

    def _pick_iceberg_opts():
        return rs.choice(
            [
                build.commands.commands.iceberg_opts(
                    market_pos_decimals=vega.market_pos_decimals,
                    market_id=market_id,
                    peak_size=rs.uniform(0, 1.1) * size,
                    minimum_visible_size=rs.uniform(0, 0.6) * size,
                ),
                None,
            ],
            p=[0.1, 0.9],
        )

    # Get network information
    market_ids = list(vega.market_to_asset.keys())
    market_id = _pick_market_id()
    market_data = vega.market_data_from_feed(market_id)

    # Pick driver fields
    type_ = _pick_type()
    time_in_force = _pick_time_in_force()
    pegged_order = _pick_pegged_order()

    # Pick driven fields
    price = _pick_price()
    size = _pick_size()
    side = _pick_side()
    post_only = _pick_post_only()
    reduce_only = _pick_reduce_only()
    iceberg_opts = _pick_iceberg_opts()

    return build.commands.commands.order_submission(
        market_size_decimals=vega.market_pos_decimals,
        market_price_decimals=vega.market_price_decimals,
        market_id=market_id,
        price=price,
        size=size,
        side=side,
        time_in_force=time_in_force,
        type=type_,
        reference=None,
        pegged_order=pegged_order,
        post_only=post_only,
        reduce_only=reduce_only,
        iceberg_opts=iceberg_opts,
    )


def fuzz_order_amendment(
    vega: VegaService, rs: RandomState, bias: float
) -> vega_protos.commands.v1.commands.OrderSubmission:

    def _pick_market_id():
        if len(market_ids) == 0:
            return None
        return rs.choice(market_ids)

    def _pick_order_id():
        return None

    def _pick_price():
        return rs.choice(
            [
                market_data.mid_price + rs.normal(loc=0, scale=10),
                rs.beta(a=0.001, b=0.001)
                * (2**64 - 1)
                / 10 ** vega.market_pos_decimals[market_id],
            ],
            p=[0.9, 0.1],
        )

    def _pick_size():
        return rs.choice(
            [
                rs.poisson(100),
                rs.beta(a=0.001, b=0.001)
                * (2**64 - 1)
                / 10 ** vega.market_pos_decimals[market_id],
            ],
            p=[0.9, 0.1],
        )

    def _pick_size_delta():
        return rs.choice(
            [
                rs.normal(0, 10),
                rs.beta(a=0.001, b=0.001)
                * (2**64 - 1)
                / 10 ** vega.market_pos_decimals[market_id],
            ],
            p=[0.9, 0.1],
        )

    # Get network information
    market_ids = [key for key, _ in vega.market_to_asset.items()]
    market_id = _pick_market_id()
    market_data = vega.market_data_from_feed(market_id)

    # Pick driven fields
    order_id = _pick_order_id()
    size = _pick_size()
    size_delta = _pick_size_delta()
    (size, size_delta) = (size, None) if rs.rand() < 0.5 else (None, size_delta)
    price = _pick_price()

    return build.commands.commands.order_amendment(
        market_size_decimals=vega.market_pos_decimals,
        market_price_decimals=vega.market_price_decimals,
        order_id=order_id,
        market_id=market_id,
        size=size,
        size_delta=size_delta,
        price=price,
    )
