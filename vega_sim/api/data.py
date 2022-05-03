import numpy as np
from collections import namedtuple
from typing import Tuple

import vegaapiclient as vac
import vegaapiclient.generated.data_node.api.v1 as data_node_protos
import vegaapiclient.generated.vega as vega_protos
import vega_sim.api.data_raw as data_raw
from vega_sim.api.helpers import num_from_padded_int


class MissingAssetError(Exception):
    pass


AccountData = namedtuple("AccountData", ["general", "margin", "bond"])
OrderBook = namedtuple("OrderBook", ["bids", "offers"])


def party_account(
    pub_key: str,
    asset_id: str,
    market_id: str,
    data_client: vac.VegaTradingDataClient,
) -> AccountData:
    """Output money in general accounts/margin accounts/bond accounts (if exists)
    of a party."""
    account_req = data_node_protos.trading_data.PartyAccountsRequest(
        party_id=pub_key,
        asset=asset_id,
    )
    accounts = data_client.PartyAccounts(account_req).accounts

    asset_dp = asset_decimals(asset_id, data_client)

    general, margin, bond = np.nan, np.nan, np.nan
    for account in accounts:
        if account.market_id and account.market_id != market_id:
            # The 'general' account type has no market ID, so we have to pull
            # all markets then filter down here
            continue
        if account.type == vega_protos.vega.ACCOUNT_TYPE_GENERAL:
            general = num_from_padded_int(float(account.balance), asset_dp)
        if account.type == vega_protos.vega.ACCOUNT_TYPE_MARGIN:
            margin = num_from_padded_int(float(account.balance), asset_dp)
        if account.type == vega_protos.vega.ACCOUNT_TYPE_BOND:
            bond = num_from_padded_int(float(account.balance), asset_dp)

    return AccountData(general, margin, bond)


def find_asset_id(
    symbol: str, data_client: vac.VegaTradingDataClient, raise_on_missing: bool = False
) -> str:
    """Looks up the Asset ID of a given asset name

    Args:
        symbol:
            str, The symbol of the asset to look up
        data_client:
            VegaTradingDataClient, the gRPC data client
        raise_on_missing:
            bool, whether to raise an Error or silently return
                if the asset does not exist

    Returns:
        str, the ID of the asset
    """
    asset_request = data_node_protos.trading_data.AssetsRequest()
    assets = data_client.Assets(asset_request).assets
    # Find settlement asset
    for asset in assets:
        if asset.details.symbol == symbol:
            return asset.id
    if raise_on_missing:
        raise MissingAssetError(
            f"{symbol} asset not found on specified Vega network, "
            + "please propose and create this asset first"
        )


def market_price_decimals(
    market_id: str,
    data_client: vac.VegaTradingDataClient,
) -> int:
    """Returns the number of decimal places a specified market uses for price units.

    Args:
        market_id:
            str, The ID of the market requested
        data_client:
            VegaTradingDataClient, an instantiated gRPC data client

    Returns:
        int, The number of decimal places the market uses
    """
    return data_raw.market_info(
        market_id=market_id, data_client=data_client
    ).decimal_places


def market_position_decimals(
    market_id: str,
    data_client: vac.VegaTradingDataClient,
) -> int:
    """Returns the number of decimal places a specified market uses for position units.

    Args:
        market_id:
            str, The ID of the market requested
        data_client:
            VegaTradingDataClient, an instantiated gRPC data client

    Returns:
        int, The number of decimal places the market uses for positions
    """
    return data_raw.market_info(
        market_id=market_id, data_client=data_client
    ).position_decimal_places


def asset_decimals(
    asset_id: str,
    data_client: vac.VegaTradingDataClient,
) -> int:
    """Returns the number of decimal places a specified asset uses for price.

    Args:
        asset_id:
            str, The ID of the asset requested
        data_client:
            VegaTradingDataClient, an instantiated gRPC data client

    Returns:
        int, The number of decimal places the asset uses
    """
    return data_raw.asset_info(
        asset_id=asset_id, data_client=data_client
    ).details.decimals


def best_prices(
    market_id: str,
    data_client: vac.VegaTradingDataClient,
) -> Tuple[float, float]:
    """
    Output the best static bid price and best static ask price in current market.
    """
    mkt_data = data_raw.market_data(market_id=market_id, data_client=data_client)
    mkt_price_dp = market_price_decimals(market_id=market_id, data_client=data_client)

    return num_from_padded_int(
        mkt_data.best_static_bid_price, mkt_price_dp
    ), num_from_padded_int(mkt_data.best_static_offer_price, mkt_price_dp)


def open_orders_by_market(
    market_id: str,
    data_client: vac.VegaTradingDataClient,
) -> OrderBook:
    """
    Output all active limit orders in current market.
    """
    orders = data_client.OrdersByMarket(
        data_node_protos.trading_data.OrdersByMarketRequest(market_id=market_id)
    ).orders

    mkt_price_dp = market_price_decimals(market_id=market_id, data_client=data_client)
    mkt_pos_dp = market_position_decimals(market_id=market_id, data_client=data_client)

    bids = {}
    offers = {}
    for order in orders:
        if order.status == vega_protos.vega.Order.Status.STATUS_ACTIVE:
            if order.side == vega_protos.vega.Side.SIDE_BUY:
                price = num_from_padded_int(order.price, mkt_price_dp)
                volume = num_from_padded_int(order.remaining, mkt_pos_dp)
                bids[price] = bids.get(price, 0) + volume
            else:
                price = num_from_padded_int(order.price, mkt_price_dp)
                volume = num_from_padded_int(order.remaining, mkt_pos_dp)
                offers[price] = bids.get(price, 0) + volume

    return OrderBook(bids, offers)
