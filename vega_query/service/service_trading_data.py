import time
import toml
import grpc
import logging
import datetime

from pathlib import Path
from dataclasses import dataclass
from typing import TypeVar, Optional, Callable, List, Any

from vega_protos.protos.data_node.api.v2 import trading_data
from vega_protos.protos.data_node.api.v2.trading_data_pb2_grpc import (
    TradingDataServiceStub,
)
import vega_protos.protos as protos
from vega_query.service.networks.constants import Network


logger = logging.getLogger(__name__)

T = TypeVar("T")
S = TypeVar("S")
U = TypeVar("U")

from functools import wraps


def log_client_method(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Client method '{func.__name__}' called with kwargs: {kwargs}")
        res = func(*args, **kwargs)
        if hasattr(res, "__iter__"):
            logger.debug(f"Returning {len(res)} results.")
        else:
            logger.debug(f"Returning single result.")
        return res

    return wrapper


def unroll_v2_pagination(
    base_request: S,
    request_func: Callable[[S], T],
    extraction_func: Callable[[S], List[U]],
    max_pages: int,
) -> List[T]:
    base_request.pagination.CopyFrom(
        protos.data_node.api.v2.trading_data.Pagination(first=1000)
    )
    response = request_func(base_request)

    full_list = extraction_func(response)
    page = 1
    while response.page_info.has_next_page:
        if max_pages is not None and page >= max_pages:
            break
        base_request.pagination.after = response.page_info.end_cursor
        response = request_func(base_request)
        curr_list = extraction_func(response)
        full_list.extend(curr_list)
        logger.debug(f"Extended results wih {len(curr_list)} entries from page {page}.")
        page += 1

    return full_list


class TradingDataService:
    def __init__(
        self,
        network: Network,
        network_config: Optional[Path] = None,
        port_data_node: Optional[int] = None,
    ):

        self.__node = None

        match network:

            case Network.NETWORK_UNSPECIFIED:
                if network_config is None:
                    raise ValueError(
                        "A network config file must be provided for an unspecified network"
                    )
                self.__grpc_nodes = self.__nodes_from_config(network_config)

            case Network.NETWORK_LOCAL:
                if port_data_node is None:
                    raise ValueError(
                        "A data node port must be specified for a local network."
                    )
                self.__grpc_nodes = dict.fromkeys([f"localhost:{port_data_node}"])

            case (
                Network.NETWORK_MAINNET
                | Network.NETWORK_TESTNET
                | Network.NETWORK_STAGNET
            ):
                self.__grpc_nodes = self.__nodes_from_config(network.config)

        self.score_nodes()
        self.switch_node()

    def stop(self):
        self.__channel.close()

    def score_nodes(self):
        # Response time
        for key in self.__grpc_nodes:
            try:
                # Try create a channel if fail, skip
                self.__create_channel(key)
                self.__stub = TradingDataServiceStub(self.__channel)
                t = time.time()
                self.__stub.Ping(trading_data.PingRequest())
                self.__grpc_nodes[key] = abs(time.time() - t)
                logger.debug(
                    f"Opened insecure channel with {key} -"
                    f" {self.__grpc_nodes[key]:.2f}s"
                )
                self.__channel.close()

            except grpc.FutureTimeoutError:
                logger.debug(f"Unable to open insecure channel with {key}")
                self.__grpc_nodes[key] = float("inf")

    def switch_node(self):
        for _ in range(100):
            try:
                # If the current node has failed, reset the node
                if self.__node is not None:
                    self.__grpc_nodes[self.__node] = float("inf")
                self.__node = min(self.__grpc_nodes, key=self.__grpc_nodes.get)
                self.__create_channel(self.__node)
                self.__stub = TradingDataServiceStub(self.__channel)
                logger.debug(f"Opened insecure channel with {self.__node}")
                break
            except grpc.FutureTimeoutError:
                logger.debug(f"Unable to open insecure channel with {self.__node}")
                continue

    def __create_channel(self, node):
        try:
            self.__channel = grpc.insecure_channel(
                node,
                options=[
                    ("grpc.max_send_message_length", 1024 * 1024 * 20),
                    ("grpc.max_receive_message_length", 1024 * 1024 * 20),
                ],
            )
            grpc.channel_ready_future(self.__channel).result(timeout=1)
        except grpc.FutureTimeoutError as e:
            self.__channel.close()
            raise e

    def __nodes_from_config(self, network_config: Path) -> dict:
        if not network_config.exists():
            raise ValueError(f"Config for {network_config.absolute()} does not exist.")
        config = toml.load(network_config.absolute())
        return dict.fromkeys(config["API"]["GRPC"]["Hosts"], 0)

    @log_client_method
    def ping(self):
        self.__stub.Ping(trading_data.PingRequest())

    @log_client_method
    def list_accounts(
        self,
        asset_id: Optional[str] = None,
        party_ids: Optional[List[str]] = None,
        market_ids: Optional[List[str]] = None,
        account_types: Optional[List[protos.vega.vega.AccountType.Value]] = None,
        max_pages: Optional[int] = None,
    ) -> List[protos.vega.vega.Account]:
        account_filter = trading_data.AccountFilter(
            asset_id=asset_id,
            party_ids=party_ids,
            market_ids=market_ids,
            account_types=account_types,
        )
        return unroll_v2_pagination(
            base_request=trading_data.ListAccountsRequest(filter=account_filter),
            request_func=lambda x: self.__stub.ListAccounts(x).accounts,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )

    # def observe_accounts(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def info(self) -> protos.data_node.api.v2.trading_data.InfoResponse:
    #     # TODO: Implement method
    #     pass

    # def get_order(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    @log_client_method
    def list_orders(
        self,
        statuses: Optional[List[protos.vega.vega.Order.Status.Value]] = None,
        types: Optional[List[protos.vega.vega.Order.Type.Value]] = None,
        time_in_forces: Optional[List[protos.vega.vega.Order.TimeInForce.Value]] = None,
        exclude_liquidity: Optional[bool] = None,
        party_ids: Optional[List[str]] = None,
        market_ids: Optional[List[str]] = None,
        reference: Optional[str] = None,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        live_only: Optional[bool] = None,
        max_pages: Optional[int] = None,
    ) -> List[protos.vega.vega.Order]:
        order_filter = protos.data_node.api.v2.trading_data.OrderFilter(
            statuses=statuses,
            types=types,
            time_in_forces=time_in_forces,
            exclude_liquidity=exclude_liquidity,
            party_ids=party_ids,
            market_ids=market_ids,
            reference=reference,
            date_range=protos.data_node.api.v2.trading_data.DateRange(
                start_timestamp=start_timestamp, end_timestamp=end_timestamp
            ),
            live_only=live_only,
        )
        return unroll_v2_pagination(
            base_request=trading_data.ListOrdersRequest(filter=order_filter),
            request_func=lambda x: self.__stub.ListOrders(x).orders,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )

    # def list_order_versions(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def observe_orders(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_stop_order(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_stop_orders(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    @log_client_method
    def list_positions(
        self,
        party_id: Optional[str] = None,
        market_id: Optional[str] = None,
        max_pages: Optional[int] = None,
    ) -> List[protos.vega.vega.Position]:
        return unroll_v2_pagination(
            base_request=trading_data.ListPositionsRequest(
                party_id=party_id,
                market_id=market_id,
            ),
            request_func=lambda x: self.__stub.ListPositions(x).positions,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )

    @log_client_method
    def list_all_positions(
        self,
        party_ids: Optional[List[str]] = None,
        market_ids: Optional[List[str]] = None,
        max_pages: Optional[int] = None,
    ) -> List[protos.vega.vega.Position]:
        filter = trading_data.PositionsFilter(
            party_ids=party_ids, market_ids=market_ids
        )
        return unroll_v2_pagination(
            base_request=trading_data.ListAllPositionsRequest(
                filter=filter,
            ),
            request_func=lambda x: self.__stub.ListAllPositions(x).positions,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )

    # def observe_positions(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    @log_client_method
    def list_ledger_entries(
        self,
        close_on_account_filters: Optional[bool] = None,
        from_asset_id: Optional[str] = None,
        from_party_ids: Optional[List[str]] = None,
        from_market_ids: Optional[List[str]] = None,
        from_account_types: Optional[List[protos.vega.vega.AccountType.Value]] = None,
        to_asset_id: Optional[str] = None,
        to_party_ids: Optional[List[str]] = None,
        to_market_ids: Optional[List[str]] = None,
        to_account_types: Optional[List[protos.vega.vega.AccountType.Value]] = None,
        transfer_types: Optional[List[protos.vega.vega.TransferType.Value]] = None,
        date_range_start_timestamp: Optional[int] = None,
        date_range_end_timestamp: Optional[int] = None,
        max_pages: Optional[int] = None,
    ) -> List[protos.data_node.api.v2.trading_data.AggregatedLedgerEntry]:
        if (from_party_ids is None) and (to_party_ids is None):
            raise ValueError(
                "Either 'from_party_ids' or 'to_party_ids' must be specified."
            )
        return unroll_v2_pagination(
            base_request=trading_data.ListLedgerEntriesRequest(
                filter=trading_data.LedgerEntryFilter(
                    close_on_account_filters=close_on_account_filters,
                    from_account_filter=trading_data.AccountFilter(
                        asset_id=from_asset_id,
                        party_ids=from_party_ids,
                        market_ids=from_market_ids,
                        account_types=from_account_types,
                    ),
                    to_account_filter=trading_data.AccountFilter(
                        asset_id=to_asset_id,
                        party_ids=to_party_ids,
                        market_ids=to_market_ids,
                        account_types=to_account_types,
                    ),
                    transfer_types=transfer_types,
                ),
                date_range=trading_data.DateRange(
                    start_timestamp=date_range_start_timestamp,
                    end_timestamp=date_range_end_timestamp,
                ),
            ),
            request_func=lambda x: self.__stub.ListLedgerEntries(x).ledger_entries,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )

    # def export_ledger_entries(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    @log_client_method
    def list_balance_changes(
        self,
        asset_id: Optional[str] = None,
        party_ids: Optional[List[str]] = None,
        market_ids: Optional[List[str]] = None,
        account_types: Optional[List[protos.vega.vega.AccountType.Value]] = None,
        date_range_start_timestamp: Optional[int] = None,
        date_range_end_timestamp: Optional[int] = None,
        max_pages: Optional[int] = None,
    ) -> List[trading_data.AggregatedBalance]:
        return unroll_v2_pagination(
            base_request=trading_data.ListBalanceChangesRequest(
                filter=trading_data.AccountFilter(
                    asset_id=asset_id,
                    party_ids=party_ids,
                    market_ids=market_ids,
                    account_types=account_types,
                ),
                date_range=trading_data.DateRange(
                    start_timestamp=date_range_start_timestamp,
                    end_timestamp=date_range_end_timestamp,
                ),
            ),
            request_func=lambda x: self.__stub.ListBalanceChanges(x).balances,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )

    @log_client_method
    def get_latest_market_data(
        self, market_id: str, max_pages: Optional[int] = None
    ) -> protos.vega.vega.MarketData:
        response = self.__stub.GetLatestMarketData(
            trading_data.GetLatestMarketDataRequest(market_id=market_id)
        )
        self.__channel
        return response.market_data

    @log_client_method
    def list_latest_market_data(
        self,
    ) -> List[protos.vega.vega.MarketData]:
        return list(
            self.__stub.ListLatestMarketData(
                trading_data.ListLatestMarketDataRequest()
            ).markets_data
        )

    @log_client_method
    def get_latest_market_depth(self, market_id: str) -> protos.vega.vega.MarketDepth:
        return self.__stub.GetLatestMarketDepth(
            trading_data.GetLatestMarketDataRequest(market_id=market_id)
        )

    # def observe_markets_depth(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def observe_markets_depth_updates(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def observe_markets_data(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    @log_client_method
    def get_market_data_history_by_id(
        self,
        market_id: str,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        max_pages: Optional[int] = None,
    ) -> List[protos.vega.vega.MarketData]:
        return unroll_v2_pagination(
            base_request=trading_data.GetMarketDataHistoryByIDRequest(
                market_id=market_id,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
            ),
            request_func=lambda x: self.__stub.GetMarketDataHistoryByID(x).market_data,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )

    # def list_transfers(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_transfer(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_network_limits(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    @log_client_method
    def list_candle_data(
        self,
        candle_id: str,
        from_timestamp: Optional[int] = None,
        to_timestamp: Optional[int] = None,
        max_pages: Optional[int] = None,
    ) -> List[trading_data.Candle]:
        return unroll_v2_pagination(
            base_request=trading_data.ListCandleDataRequest(
                candle_id=candle_id,
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp,
            ),
            request_func=lambda x: self.__stub.ListCandleData(x).candles,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )

    # def observe_candle_data(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    @log_client_method
    def list_candle_intervals(
        self, market_id: str
    ) -> List[trading_data.IntervalToCandleId]:
        return self.__stub.ListCandleIntervals(
            trading_data.ListCandleIntervalsRequest(market_id=market_id)
        ).interval_to_candle_id

    # def list_votes(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def observe_votes(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_e_r_c20_multi_sig_signer_added_bundles(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_e_r_c20_multi_sig_signer_removed_bundles(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_e_r_c20_list_asset_bundle(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_e_r_c20_set_asset_limits_bundle(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_e_r_c20_withdrawal_approval(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_last_trade(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    @log_client_method
    def list_trades(
        self,
        market_ids: Optional[List[str]] = None,
        order_ids: Optional[List[str]] = None,
        party_ids: Optional[List[str]] = None,
        date_range_start_timestamp: Optional[int] = None,
        date_range_end_timestamp: Optional[int] = None,
        max_pages: Optional[int] = None,
    ) -> List[protos.vega.vega.Trade]:
        return unroll_v2_pagination(
            base_request=trading_data.ListTradesRequest(
                market_ids=market_ids,
                order_ids=order_ids,
                party_ids=party_ids,
                date_range=trading_data.DateRange(
                    start_timestamp=date_range_start_timestamp,
                    end_timestamp=date_range_end_timestamp,
                ),
            ),
            request_func=lambda x: self.__stub.ListTrades(x).trades,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )

    # def observe_trades(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_oracle_spec(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_oracle_specs(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_oracle_data(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    @log_client_method
    def get_market(self, market_id: str) -> protos.vega.markets.Market:
        return self.__stub.GetMarket(
            trading_data.GetMarketRequest(market_id=market_id)
        ).market

    @log_client_method
    def list_markets(
        self,
        include_settled: Optional[bool] = None,
        max_pages: Optional[int] = None,
    ) -> List[protos.vega.markets.Market]:
        return unroll_v2_pagination(
            base_request=trading_data.ListMarketsRequest(
                include_settled=include_settled
            ),
            request_func=lambda x: self.__stub.ListMarkets(x).markets,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )

    # def list_successor_markets(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_party(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    @log_client_method
    def list_parties(
        self, party_id: Optional[str] = None, max_pages: Optional[int] = None
    ) -> List[protos.vega.vega.Party]:
        return unroll_v2_pagination(
            base_request=trading_data.ListPartiesRequest(party_id=party_id),
            request_func=lambda x: self.__stub.ListParties(x).parties,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )

    # def list_margin_levels(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def observe_margin_levels(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    @log_client_method
    def list_rewards(
        self,
        party_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        from_epoch: Optional[int] = None,
        to_epoch: Optional[int] = None,
        team_id: Optional[str] = None,
        game_id: Optional[str] = None,
        max_pages: Optional[int] = None,
    ) -> List[protos.vega.vega.Reward]:
        return unroll_v2_pagination(
            base_request=trading_data.ListRewardsRequest(
                party_id=party_id,
                asset_id=asset_id,
                from_epoch=from_epoch,
                to_epoch=to_epoch,
                team_id=team_id,
                game_id=game_id,
            ),
            request_func=lambda x: self.__stub.ListRewards(x).rewards,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )

    # def list_reward_summaries(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    @log_client_method
    def list_epoch_reward_summaries(
        self,
        asset_ids: List[str] = None,
        market_ids: List[str] = None,
        from_epoch: Optional[int] = None,
        to_epoch: Optional[int] = None,
        max_pages: Optional[int] = None,
    ) -> List[protos.vega.vega.EpochRewardSummary]:
        return unroll_v2_pagination(
            base_request=trading_data.ListEpochRewardSummariesRequest(
                filter=trading_data.RewardSummaryFilter(
                    asset_ids=asset_ids,
                    market_ids=market_ids,
                    from_epoch=from_epoch,
                    to_epoch=to_epoch,
                )
            ),
            request_func=lambda x: self.__stub.ListEpochRewardSummaries(x).summaries,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )

    # def get_deposit(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_deposits(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_withdrawal(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_withdrawals(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    def get_asset(self, asset_id: str) -> protos.vega.assets.Asset:
        return self.__stub.GetAsset(
            trading_data.GetAssetRequest(asset_id=asset_id)
        ).asset

    def list_assets(
        self, asset_id: Optional[str] = None, max_pages: Optional[int] = None
    ) -> List[protos.vega.assets.Asset]:
        return unroll_v2_pagination(
            base_request=trading_data.ListAssetsRequest(asset_id=asset_id),
            request_func=lambda x: self.__stub.ListAssets(x).assets,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )

    # def list_liquidity_provisions(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_all_liquidity_provisions(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def observe_liquidity_provisions(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_liquidity_providers(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_paid_liquidity_fees(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_governance_data(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    @log_client_method
    def list_governance_data(
        self,
        proposal_state: Optional[protos.vega.governance.Proposal.State.Value] = None,
        proposal_type: Optional[
            protos.data_node.api.v2.trading_data.ListGovernanceDataRequest.Type.Value
        ] = None,
        proposer_party_id: Optional[str] = None,
        proposal_reference: Optional[str] = None,
        max_pages: Optional[int] = None,
    ) -> List[protos.vega.governance.GovernanceData]:
        return unroll_v2_pagination(
            base_request=trading_data.ListGovernanceDataRequest(
                proposal_state=proposal_state,
                proposal_type=proposal_type,
                proposer_party_id=proposer_party_id,
                proposal_reference=proposal_reference,
            ),
            request_func=lambda x: self.__stub.ListGovernanceData(x).connection,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )

    # def observe_governance(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_delegations(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_network_data(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_node(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_nodes(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_node_signatures(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_epoch(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def estimate_fee(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def estimate_margin(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def estimate_position(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    @log_client_method
    def list_network_parameters(
        self, max_pages: Optional[int] = None
    ) -> List[protos.vega.vega.NetworkParameter]:
        return unroll_v2_pagination(
            base_request=trading_data.ListNetworkParametersRequest(),
            request_func=lambda x: self.__stub.ListNetworkParameters(
                x
            ).network_parameters,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )

    @log_client_method
    def get_network_parameter(self, key: str) -> protos.vega.vega.NetworkParameter:
        return self.__stub.GetNetworkParameter(
            trading_data.GetNetworkParameterRequest(key=key)
        ).network_parameter

    # def list_checkpoints(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_stake(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_risk_factors(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def observe_event_bus(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def observe_ledger_movements(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_key_rotations(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_ethereum_key_rotations(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    def get_vega_time(self) -> int:
        return self.__stub.GetVegaTime(trading_data.GetVegaTimeRequest()).timestamp

    # def get_protocol_upgrade_status(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_protocol_upgrade_proposals(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_core_snapshots(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_most_recent_network_history_segment(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_all_network_history_segments(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_active_network_history_peer_addresses(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_network_history_status(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_network_history_bootstrap_peers(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_entities(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    @log_client_method
    def list_funding_periods(
        self,
        market_id: str,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        max_pages: Optional[int] = None,
    ) -> List[protos.vega.events.v1.events.FundingPeriod]:
        return unroll_v2_pagination(
            base_request=trading_data.ListFundingPeriodsRequest(
                market_id=market_id,
                date_range=protos.data_node.api.v2.trading_data.DateRange(
                    start_timestamp=start_timestamp,
                    end_timestamp=end_timestamp,
                ),
            ),
            request_func=lambda x: self.__stub.ListFundingPeriods(x).funding_periods,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )

    @log_client_method
    def list_funding_period_data_points(
        self,
        market_id: str,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        source: Optional[
            protos.vega.events.v1.events.FundingPeriodDataPoint.Source.Value
        ] = None,
        seq: Optional[int] = None,
        max_pages: Optional[int] = None,
    ) -> List[protos.vega.events.v1.events.FundingPeriodDataPoint]:
        return unroll_v2_pagination(
            base_request=trading_data.ListFundingPeriodDataPointsRequest(
                market_id=market_id,
                date_range=protos.data_node.api.v2.trading_data.DateRange(
                    start_timestamp=start_timestamp,
                    end_timestamp=end_timestamp,
                ),
                source=source,
                seq=seq,
            ),
            request_func=lambda x: self.__stub.ListFundingPeriodDataPoints(
                x
            ).funding_period_data_points,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )

    @log_client_method
    def list_funding_payments(
        self,
        party_id: str,
        market_id: Optional[str] = None,
        max_pages: Optional[int] = None,
    ) -> List[protos.data_node.api.v2.trading_data.FundingPayment]:
        return unroll_v2_pagination(
            base_request=trading_data.ListFundingPaymentsRequest(
                party_id=party_id,
                market_id=market_id,
            ),
            request_func=lambda x: self.__stub.ListFundingPayments(x).funding_payments,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )

    # def list_game_party_store(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_game_team_scores(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_games(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_party_activity_streak(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_current_referral_program(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_referral_sets(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_referral_set_referees(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_referral_set_stats(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_teams(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_team_referees(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def list_team_referee_history(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_fees_stats(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_fees_stats_for_party(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_current_volume_discount_program(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_volume_discount_stats(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_vesting_balances_summary(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_party_vesting_stats(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def observe_transaction_results(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    # def estimate_transfer_fee(self, max_pages: Optional[int] = None) -> Any:
    #     # TODO: Implement method
    #     pass

    # def get_total_transfer_fee_discount(
    #     self, max_pages: Optional[int] = None
    # ) -> Any:
    #     # TODO: Implement method
    #     pass

    @log_client_method
    def list_amms(
        self,
        market_id: Optional[str] = None,
        party_id: Optional[str] = None,
        amm_party_id: Optional[str] = None,
        status: Optional[protos.vega.events.v1.events.AMM.Status.Value] = None,
        max_pages: Optional[int] = None,
    ) -> List[protos.vega.events.v1.events.AMM]:
        return unroll_v2_pagination(
            base_request=trading_data.ListAMMsRequest(
                party_id=party_id,
                market_id=market_id,
                amm_party_id=amm_party_id,
                status=status,
            ),
            request_func=lambda x: self.__stub.ListAMMs(x).amms,
            extraction_func=lambda res: [i.node for i in res.edges],
            max_pages=max_pages,
        )
