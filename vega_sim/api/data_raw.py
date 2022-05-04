from __future__ import annotations

from collections import namedtuple
from typing import Dict, List, Optional

import vegaapiclient as vac
import vegaapiclient.generated.data_node.api.v1 as data_node_protos
import vegaapiclient.generated.vega as vega_protos

MarketAccount = namedtuple("MarketAccount", ["insurance", "liquidity_fee"])


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


def asset_info(
    asset_id: str,
    data_client: vac.VegaTradingDataClient,
) -> vac.vega.assets.Asset:
    """Returns information on a given asset selected by its ID

    Args:
        asset_id:
            str, The ID of the asset requested
        data_client:
            VegaTradingDataClient, an instantiated gRPC data client

    Returns:
        vega.assets.Asset, Object containing data about the requested asset
    """
    return data_client.AssetByID(
        data_node_protos.trading_data.AssetByIDRequest(id=asset_id)
    ).asset


def all_market_accounts(
    asset_id: str,
    market_id: str,
    data_client: vac.VegaTradingDataClient,
) -> Dict[vega_protos.vega.AccountType, MarketAccount]:
    """
    Output liquidity fee account/ insurance pool in the market
    """
    accounts = data_client.MarketAccounts(
        data_node_protos.trading_data.MarketAccountsRequest(
            asset=asset_id, market_id=market_id
        )
    ).accounts

    return {account.type: account for account in accounts}


def market_accounts(
    asset_id: str,
    market_id: str,
    data_client: vac.VegaTradingDataClient,
) -> MarketAccount:
    """
    Output liquidity fee account/ insurance pool in the market
    """
    account_type_map = all_market_accounts(
        asset_id=asset_id, market_id=market_id, data_client=data_client
    )
    return MarketAccount(
        account_type_map[vega_protos.vega.ACCOUNT_TYPE_FEES_LIQUIDITY],
        account_type_map[vega_protos.vega.ACCOUNT_TYPE_INSURANCE],
    )


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


def order_status(
    order_id: str, data_client: vac.VegaTradingDataClient, version: int = 0
) -> Optional[vega_protos.vega.Order]:
    """Loads information about a specific order identified by the ID.
    Optionally return historic order versions.

    Args:
        order_id:
            str, the order identifier as specified by Vega when originally placed
        data_client:
            VegaTradingDataClient, an instantiated gRPC trading data client
        version:
            int, Optional, Version of the order:
                - Set `version` to 0 for most recent version of the order
                - Set `1` for original version of the order
                - Set `2` for first amendment, `3` for second amendment, etc
    Returns:
        Optional[vega.Order], the requested Order object or None if nothing found
    """
    return data_client.OrderByID(
        data_node_protos.trading_data.OrderByIDRequest(
            order_id=order_id, version=version
        )
    ).order
