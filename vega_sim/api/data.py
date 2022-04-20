import numpy as np
from collections import namedtuple
from typing import Dict, List, Tuple

import vegaapiclient as vac
import vegaapiclient.generated.data_node.api.v1 as data_node_protos
import vegaapiclient.generated.vega as vega_protos

AccountData = namedtuple("AccountData", ["general", "margin", "bond"])
MarketAccount = namedtuple("MarketAccount", ["insurance", "liquidity_fee"])
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
        market_id=market_id,
    )
    accounts = data_client.PartyAccounts(account_req).accounts
    general, margin, bond = np.nan, np.nan, np.nan
    for account in accounts:
        if account.type == vega_protos.vega.ACCOUNT_TYPE_GENERAL:
            general = float(account.balance)
        if account.type == vega_protos.vega.ACCOUNT_TYPE_MARGIN:
            margin = float(account.balance)
        if account.type == vega_protos.vega.ACCOUNT_TYPE_BOND:
            bond = float(account.balance)

    return AccountData(general, margin, bond)


def positions_by_market(
    pub_key: str,
    market_id: str,
    data_client: vac.VegaTradingDataClient,
) -> List[vega_protos.vega.Position]:
    """Output positions of a party."""
    positions_req = data_node_protos.trading_data.PositionsByPartyRequest(
        party_id=pub_key,
        market_id=market_id,
    )
    return data_client.PositionsByParty(positions_req).positions


def all_markets(
    data_client: vac.VegaTradingDataClient,
) -> List[vega_protos.markets.Market]:
    """
    Output market info.
    """
    market_req = data_node_protos.trading_data.MarketsRequest()
    return data_client.Markets(market_req).markets


def market_info(
    market_id: str,
    data_client: vac.VegaTradingDataClient,
) -> vega_protos.markets.Market:
    """
    Output market info.
    """
    market_req = data_node_protos.trading_data.MarketByIDRequest(market_id=market_id)
    return data_client.MarketByID(market_req).market


def market_data(
    market_id: str,
    data_client: vac.VegaTradingDataClient,
) -> vega_protos.vega.MarketData:
    """
    Output market info.
    """
    market_req = data_node_protos.trading_data.MarketDataByIDRequest(
        market_id=market_id
    )
    return data_client.MarketDataByID(market_req).market_data


def infrastructure_fee_accounts(
    asset_id: str,
    data_client: vac.VegaTradingDataClient,
) -> List[vega_protos.vega.Account]:
    """
    Output infrastructure fee accounts
    """
    return data_client.FeeInfrastructureAccounts(
        data_node_protos.trading_data.FeeInfrastructureAccountsRequest(asset=asset_id)
    ).accounts


def market_accounts(
    asset_id: str,
    market_id: str,
    data_client: vac.VegaTradingDataClient,
) -> MarketAccount:
    """
    Output liquidity fee account/ insurance pool in the market
    """
    accounts = data_client.MarketAccounts(
        data_node_protos.trading_data.MarketAccountsRequest(
            asset=asset_id, market_id=market_id
        )
    ).accounts

    account_type_map = {account.type: account for account in accounts}
    return MarketAccount(
        account_type_map[vega_protos.vega.ACCOUNT_TYPE_FEES_LIQUIDITY],
        account_type_map[vega_protos.vega.ACCOUNT_TYPE_INSURANCE],
    )


def best_prices(
    market_id: str,
    data_client: vac.VegaTradingDataClient,
) -> Tuple[int, int]:
    """
    Output the best static bid price and best static ask price in current market.
    """
    mkt_data = market_data(market_id=market_id, data_client=data_client)
    return int(mkt_data.best_static_bid_price), int(mkt_data.best_static_offer_price)


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

    bids = {}
    offers = {}
    for order in orders:
        if order.status == vega_protos.vega.Order.Status.STATUS_ACTIVE:
            if order.side == vega_protos.vega.Order.Side.SIDE_BUY:
                price = int(order["price"])
                volume = int(order["remaining"])
                bids[price] = bids.get(price, 0) + volume
            else:
                price = int(order["price"])
                volume = int(order["remaining"])
                offers[price] = bids.get(price, 0) + volume

    return OrderBook(bids, offers)
