import logging

import vega_sim.api.data as data
import vega_sim.api.data_raw as data_raw

from vega_sim.proto.data_node.api.v2.trading_data_pb2 import GetVegaTimeRequest

from vega_sim.network_service import VegaServiceNetwork
from vega_sim.scenario.constants import Network

PARTY_ID = "3994b190dd62b51f3c08c85f7d914906d9acbd47ec830be4427746c3719bd5ca"
MARKET_ID = "84025e68387cf61c2b91228d768dcdd4f10a9ee5cd2824fdea35b259976f59c1"

# Margin calculations split into three components (slippage, volume, orders)


def calc_maintenance(
    open_volume,
    open_orders_long,
    open_orders_short,
    risk_factor_long,
    risk_factor_short,
    mark_price,
    linear_slippage_factor,
    quadratic_slippage_factor,
    order_book,
):
    # Calculate riskiest long and short position
    riskiest_long = max([mm_open_volume + open_orders_long, 0])
    riskiest_short = abs(min([mm_open_volume - open_orders_short, 0]))

    # Calculate maintenance margin components for a long position
    slippage_per_unit_long = calculate_spu(
        riskiest_position=riskiest_long,
        order_book=order_book,
        mark_price=mark_price,
        side="long",
    )
    capped_slippage_long = calc_capped_slippage(
        riskiest_long,
        mark_price,
        linear_slippage_factor,
        quadratic_slippage_factor,
    )
    uncapped_slippage_long = calc_uncapped_slippage(
        riskiest_long, mark_price, slippage_per_unit_long
    )
    volume_maintenance_long = calc_volume_maintenance(
        max(open_volume, 0), mark_price, risk_factor_long
    )
    orders_maintenance_long = calculate_orders_maintenance(
        open_orders_long, mark_price, risk_factor_long
    )
    capped_maintenance_long = (
        capped_slippage_long + volume_maintenance_long + orders_maintenance_long
    )
    uncapped_maintenance_long = (
        uncapped_slippage_long + volume_maintenance_long + orders_maintenance_long
    )
    maintenance_long = min([uncapped_maintenance_long, capped_maintenance_long])
    logging.debug(
        f"long: capped_maintenance={capped_maintenance_long} ({capped_slippage_long} + {volume_maintenance_long} + {orders_maintenance_long})"
    )
    logging.debug(
        f"long: uncapped_maintenance={uncapped_maintenance_long} ({uncapped_slippage_long} + {volume_maintenance_long} + {orders_maintenance_long})"
    )

    # Calculate maintenance margin components for a short position
    slippage_per_unit_short = calculate_spu(
        riskiest_position=riskiest_short,
        order_book=order_book,
        mark_price=mark_price,
        side="short",
    )
    capped_slippage_short = calc_capped_slippage(
        riskiest_short,
        mark_price,
        linear_slippage_factor,
        quadratic_slippage_factor,
    )
    uncapped_slippage_short = calc_uncapped_slippage(
        riskiest_short, mark_price, slippage_per_unit_short
    )
    volume_maintenance_short = calc_volume_maintenance(
        abs(min(open_volume, 0)), mark_price, risk_factor_short
    )
    orders_maintenance_short = calculate_orders_maintenance(
        open_orders_short, mark_price, risk_factor_short
    )
    capped_maintenance_short = (
        capped_slippage_short + volume_maintenance_short + orders_maintenance_short
    )
    uncapped_maintenance_short = (
        uncapped_slippage_short + volume_maintenance_short + orders_maintenance_short
    )
    maintenance_short = min([uncapped_maintenance_short, capped_maintenance_short])
    logging.debug(
        f"short: capped_maintenance={capped_maintenance_short} ({capped_slippage_short} + {volume_maintenance_short} + {orders_maintenance_short})"
    )
    logging.debug(
        f"short: uncapped_maintenance={uncapped_maintenance_short} ({uncapped_slippage_short} + {volume_maintenance_short} + {orders_maintenance_short})"
    )

    return max([maintenance_short, maintenance_long])


def calc_capped_slippage(
    riskiest_position,
    mark_price,
    linear_slippage_factor,
    quadratic_slippage_factor,
):
    return mark_price * (
        float(linear_slippage_factor) * riskiest_position
        + float(quadratic_slippage_factor) ** 2 * riskiest_position
    )


def calc_uncapped_slippage(riskiest_position, mark_price, slippage_per_unit):
    return mark_price * riskiest_position * slippage_per_unit


def calc_volume_maintenance(open_volume, mark_price, risk_factor):
    return open_volume * mark_price * risk_factor


def calculate_orders_maintenance(open_orders, mark_price, risk_factor):
    return open_orders * mark_price * risk_factor


def calculate_spu(riskiest_position, order_book, side, mark_price):
    if riskiest_position == 0:
        return 0
    if side == "short":
        order_book = order_book.sells
    else:
        order_book = reversed(order_book.buys)

    remaining = riskiest_position
    total_slippage = 0
    book_volume = 0
    for price_level in order_book:
        required = min(remaining, price_level.volume)
        total_slippage += required * abs(price_level.price - mark_price)
        remaining += -required
        book_volume += price_level.volume
    if remaining > 0:
        logging.warning(
            f"Not enough volume on the book ({book_volume}) to close a {side} position of size {riskiest_position}. Slippage capping should be applied."
        )
    return total_slippage / riskiest_position


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    with VegaServiceNetwork(
        network=Network.MAINNET1, run_with_wallet=True, run_with_console=False
    ) as vega:
        # Get market data
        risk_factors = vega.get_risk_factors(market_id=MARKET_ID)
        market_data = vega.get_latest_market_data(market_id=MARKET_ID)
        market_info = data_raw.market_info(
            data_client=vega.trading_data_client_v2, market_id=MARKET_ID
        )
        order_book = vega.market_depth(market_id=MARKET_ID, num_levels=1000)

        # Get party data
        logging.debug(
            f"timestamp={vega.trading_data_client_v2.GetVegaTime(GetVegaTimeRequest()).timestamp}"
        )
        mm_open_volume = data.positions_by_market(
            data_client=vega.trading_data_client_v2,
            pub_key=PARTY_ID,
            market_id=MARKET_ID,
        ).open_volume
        logging.debug(
            f"timestamp={vega.trading_data_client_v2.GetVegaTime(GetVegaTimeRequest()).timestamp}"
        )
        mm_margin_levels = data.margin_levels(
            data_client=vega.trading_data_client_v2,
            party_id=PARTY_ID,
            market_id=MARKET_ID,
        )
        logging.debug(
            f"timestamp={vega.trading_data_client_v2.GetVegaTime(GetVegaTimeRequest()).timestamp}"
        )
        mm_orders = data.list_orders(
            data_client=vega.trading_data_client_v2,
            market_id=MARKET_ID,
            party_id=PARTY_ID,
            live_only=True,
        )
        logging.debug(
            f"timestamp={vega.trading_data_client_v2.GetVegaTime(GetVegaTimeRequest()).timestamp}"
        )

        # Extract the open orders
        open_orders_long = sum([order.size for order in mm_orders if order.side == 1])
        open_orders_short = abs(
            sum([order.size for order in mm_orders if order.side == 2])
        )

        # Calculate the expected maintenance
        expected_maintenance = calc_maintenance(
            open_volume=mm_open_volume,
            open_orders_long=open_orders_short,
            open_orders_short=open_orders_short,
            mark_price=market_data.mark_price,
            risk_factor_long=risk_factors.long,
            risk_factor_short=risk_factors.short,
            linear_slippage_factor=market_info.linear_slippage_factor,
            quadratic_slippage_factor=market_info.quadratic_slippage_factor,
            order_book=order_book,
        )

        logging.info(
            f"expected maintenance_margin={expected_maintenance} | actual maintenance_margin={mm_margin_levels[0].maintenance_margin}"
        )
