"""
"""

import logging

from decimal import Decimal
from collections import defaultdict
from typing import List, Dict, Optional

from vega_query.service.service import Service, Network

import vega_protos as protos


logger = logging.getLogger(__name__)


def ceil(value: Decimal) -> Decimal:
    return Decimal(value.__ceil__())


def floor(value: Decimal) -> Decimal:
    return Decimal(value.__floor__())


class Checker:

    KEYS = (
        "market.fee.factors.makerFee",
        "market.fee.factors.buybackFee",
        "market.fee.factors.treasuryFee",
        "market.fee.factors.infrastructureFee",
    )

    def __init__(self, service: Service, acceptable_error=Decimal("100")) -> None:

        self.acceptable_error = acceptable_error

        self.__service = service
        self.__trades: List[protos.vega.vega.Trade] = None
        self.__assets: Dict[str, protos.vega.assets.Asset] = None
        self.__markets: Dict[str, protos.vega.markets.Market] = None

        self.__epochs: List[protos.vega.vega.Epoch] = []

        self.__fee_factors: Dict[int, List[Dict[str, str]]] = defaultdict(list)

        self.__referral_reward_factors: Dict[
            int, Dict[str, protos.vega.vega.RewardFactors]
        ] = defaultdict(dict)
        self.__referral_discount_factors: Dict[
            int, Dict[str, protos.vega.vega.DiscountFactors]
        ] = defaultdict(dict)
        self.__volume_discount_factors: Dict[
            int, Dict[str, protos.vega.vega.DiscountFactors]
        ] = defaultdict(dict)
        self.__volume_rebate_factors: Dict[int, Dict[str, str]] = defaultdict(dict)

        self.__initialise_epochs()
        self.__initialise_trades()
        self.__initialise_network_parameters()

    @property
    def trades(self) -> List[protos.vega.vega.Trade]:
        if self.__trades is None:
            return None
        return self.__trades

    @property
    def markets(self) -> Dict[str, protos.vega.markets.Market]:
        if self.__markets is None:
            self.__markets = {
                market.id: market for market in self.__service.api.data.list_markets()
            }
        return self.__markets

    @property
    def assets(self) -> Dict[str, protos.vega.assets.Asset]:
        if self.__assets is None:
            self.__assets = {
                market.id: self.__service.utils.market.find_asset(
                    market.tradable_instrument.instrument.code
                )
                for market in self.markets.values()
            }
        return self.__assets

    @property
    def fee_factors(self):
        return self.__fee_factors

    def __initialise_network_parameters(self):
        ts = self.__service.api.data.get_vega_time()
        for key in self.KEYS:
            self.__fee_factors[key].append(
                {
                    "ts": ts,
                    "value": self.__service.api.data.get_network_parameter(
                        key=key
                    ).value,
                }
            )
        for governance_data in self.__service.api.data.list_governance_data(
            proposal_state=protos.vega.governance.Proposal.STATE_ENACTED,
            proposal_type=protos.data_node.api.v2.trading_data.ListGovernanceDataRequest.TYPE_NETWORK_PARAMETERS,
        ):
            if governance_data.proposal is not None:
                ts = governance_data.proposal.timestamp
                key = (
                    governance_data.proposal.terms.update_network_parameter.changes.key
                )
                value = (
                    governance_data.proposal.terms.update_network_parameter.changes.value
                )
                if key in self.KEYS:
                    self.__fee_factors[key].append(({"ts": ts, "value": value}))

    def get_epoch(self, ts: int) -> protos.vega.vega.Epoch:
        for epoch in self.__epochs:
            if epoch.timestamps.start_time <= ts:
                return epoch
        while not epoch.timestamps.start_time <= ts:
            epoch = self.__service.api.data.get_epoch(id=(epoch.seq - 1))
            if epoch is None:
                return None
            self.__epochs.append(epoch)
        return epoch

    def get_party_referral_reward_factors(
        self, epoch: int, party: str
    ) -> Optional[protos.vega.vega.RewardFactors]:
        if party in self.__referral_reward_factors[epoch]:
            return self.__referral_reward_factors[epoch][party]
        stats = self.__service.api.data.get_referral_set_stats(
            at_epoch=epoch, referee=party
        )
        if len(stats) > 0:
            assert int(stats[0].at_epoch) == epoch
            self.__referral_reward_factors[epoch][party] = stats[0].reward_factors
            return self.__referral_reward_factors[epoch][party]
        else:
            self.__referral_reward_factors[epoch][party] = None
        return self.__referral_reward_factors[epoch][party]

    def get_party_referral_discount_factors(
        self, epoch: int, party: str
    ) -> Optional[protos.vega.vega.DiscountFactors]:
        # if party == "network":
        #     return None
        if party in self.__referral_discount_factors[epoch]:
            return self.__referral_discount_factors[epoch][party]
        stats = self.__service.api.data.get_referral_set_stats(
            at_epoch=epoch, referee=party
        )
        if len(stats) > 0:
            assert int(stats[0].at_epoch) == epoch
            self.__referral_discount_factors[epoch][party] = stats[0].discount_factors
        else:
            self.__referral_discount_factors[epoch][party] = None
        return self.__referral_discount_factors[epoch][party]

    def get_party_volume_discount_factors(
        self, epoch: int, party: str
    ) -> Optional[protos.vega.vega.DiscountFactors]:
        # if party == "network":
        #     return None
        if party in self.__volume_discount_factors[epoch]:
            return self.__volume_discount_factors[epoch][party]
        stats = self.__service.api.data.get_volume_discount_stats(
            at_epoch=epoch, party_id=party
        )
        if len(stats) > 0:
            assert int(stats[0].at_epoch) == epoch
            self.__volume_discount_factors[epoch][party] = stats[0].discount_factors
        else:
            self.__volume_discount_factors[epoch][party] = None
        return self.__volume_discount_factors[epoch][party]

    def get_party_volume_rebate_factor(self, epoch: int, party: str) -> Decimal:
        if party == "network":
            return Decimal("0")
        if party in self.__volume_rebate_factors[epoch]:
            return self.__volume_rebate_factors[epoch][party]
        stats = self.__service.api.data.get_volume_rebate_stats(
            at_epoch=epoch, party_id=party
        )
        if len(stats) > 0:
            self.__volume_rebate_factors[epoch][party] = Decimal(
                stats[0].additional_maker_rebate
            )
        else:
            self.__volume_rebate_factors[epoch][party] = Decimal("0")
        return self.__volume_rebate_factors[epoch][party]

    def get_fee_factor(self, key: str, timestamp: int) -> Decimal:
        if key not in self.KEYS:
            raise ValueError(f"invalid key {key}")
        current = self.fee_factors[key][0]
        for param in self.fee_factors[key]:
            if timestamp > param["ts"]:
                break
            current = param
        return Decimal(current["value"])

    def __initialise_epochs(self):
        self.__epochs.append(self.__service.api.data.get_epoch())

    def __initialise_trades(self):
        self.__trades = self.__service.api.data.list_trades(
            date_range_start_timestamp=self.__epochs[0].timestamps.end_time,
            max_pages=5,
        )

    def check(self):
        checked = 0
        for trade in self.trades:
            self.__check_trade(trade)
            checked += 1
            if checked % 1 == 0:
                print(f"checked {checked} of {len(self.trades)} trades")
        print(f"finished and checked {checked} trades")

    def __check_trade(self, trade: protos.vega.vega.Trade):

        if trade.type == protos.vega.vega.Trade.TYPE_NETWORK_CLOSE_OUT_BAD:
            return True
        if trade.type == protos.vega.vega.Trade.TYPE_NETWORK_CLOSE_OUT_GOOD:
            return True
        if trade.aggressor:
            self.__handle_continuous(trade)
        else:
            self.__handle_auction(trade)

    def get_notional(self, trade: protos.vega.vega.Trade) -> Decimal:
        asset = self.assets[trade.market_id]
        market = self.markets[trade.market_id]
        exp = int(asset.details.decimals) - int(market.decimal_places)
        priceFactor = Decimal(10) ** Decimal(exp)
        positionFactor = Decimal(10) ** Decimal(market.position_decimal_places)
        price = int(Decimal(trade.price) * priceFactor)
        return Decimal(price * int(trade.size)) / positionFactor

    def apply_reward_factors(
        self,
        maker_fee: int,
        liquidity_fee: int,
        infrastructure_fee: int,
        reward_factors: Optional[protos.vega.vega.RewardFactors] = None,
    ):
        if reward_factors is None:
            return (
                maker_fee,
                liquidity_fee,
                infrastructure_fee,
                Decimal(0),
                Decimal(0),
                Decimal(0),
            )
        maker_reward = int(
            floor(Decimal(maker_fee) * Decimal(reward_factors.maker_reward_factor))
        )
        liquidity_reward = int(
            floor(
                Decimal(liquidity_fee) * Decimal(reward_factors.liquidity_reward_factor)
            )
        )
        infrastructure_reward = int(
            floor(
                Decimal(infrastructure_fee)
                * Decimal(reward_factors.infrastructure_reward_factor)
            )
        )
        return (
            maker_fee - maker_reward,
            liquidity_fee - liquidity_reward,
            infrastructure_fee - infrastructure_reward,
            maker_reward,
            liquidity_reward,
            infrastructure_reward,
        )

    def apply_discount_factors(
        self,
        maker_fee: int,
        liquidity_fee: int,
        infrastructure_fee: int,
        discount_factors: Optional[protos.vega.vega.DiscountFactors] = None,
    ):
        if discount_factors is None:
            return (
                maker_fee,
                liquidity_fee,
                infrastructure_fee,
                int(0),
                int(0),
                int(0),
            )
        maker_discount = int(
            floor(Decimal(maker_fee) * Decimal(discount_factors.maker_discount_factor))
        )
        liquidity_discount = int(
            floor(
                Decimal(liquidity_fee)
                * Decimal(discount_factors.liquidity_discount_factor)
            )
        )
        infrastructure_discount = int(
            floor(
                Decimal(infrastructure_fee)
                * Decimal(discount_factors.infrastructure_discount_factor)
            )
        )
        return (
            maker_fee - maker_discount,
            liquidity_fee - liquidity_discount,
            infrastructure_fee - infrastructure_discount,
            maker_discount,
            liquidity_discount,
            infrastructure_discount,
        )

    def apply_rebate_factor(
        self,
        notional: Decimal,
        buyback_fee: int,
        treasury_fee: int,
        effective_rebate_factor: Optional[Decimal] = None,
    ):
        if effective_rebate_factor is None:
            return buyback_fee, treasury_fee, int(0)

        high_volume_maker_fee = effective_rebate_factor * notional
        factor = Decimal(1) - (
            high_volume_maker_fee / (Decimal(buyback_fee + treasury_fee))
        )
        print(factor)
        return (
            int(floor(Decimal(buyback_fee) * factor)),
            int(floor(Decimal(treasury_fee) * factor)),
            int(floor(high_volume_maker_fee)),
        )

    def __handle_auction(self, trade):
        pass

    def __handle_continuous(self, trade: protos.vega.vega.Trade):

        fees = (
            trade.buyer_fee
            if trade.aggressor == protos.vega.vega.SIDE_BUY
            else trade.seller_fee
        )
        taker = (
            trade.buyer
            if trade.aggressor == protos.vega.vega.SIDE_BUY
            else trade.seller
        )
        maker = (
            trade.seller
            if trade.aggressor == protos.vega.vega.SIDE_BUY
            else trade.buyer
        )

        epoch = self.get_epoch(trade.timestamp)

        notional = self.get_notional(trade)

        referral_reward_factors = self.get_party_referral_reward_factors(
            epoch=epoch.seq - 1, party=taker
        )
        referral_discount_factors = self.get_party_referral_discount_factors(
            epoch=epoch.seq - 1, party=taker
        )
        volume_discount_factors = self.get_party_volume_discount_factors(
            epoch=epoch.seq - 1, party=taker
        )

        # Calculate full fees
        maker_fee_factor = self.get_fee_factor(
            "market.fee.factors.makerFee", trade.timestamp
        )
        liquidity_fee_factor = Decimal("0")
        infrastructure_fee_factor = self.get_fee_factor(
            "market.fee.factors.infrastructureFee", trade.timestamp
        )
        buyback_fee_factor = self.get_fee_factor(
            "market.fee.factors.buybackFee", trade.timestamp
        )
        treasury_fee_factor = self.get_fee_factor(
            "market.fee.factors.treasuryFee", trade.timestamp
        )
        maker_fee = int(ceil(notional * maker_fee_factor))
        liquidity_fee = int(ceil(notional * liquidity_fee_factor))
        infrastructure_fee = int(ceil(notional * infrastructure_fee_factor))
        buyback_fee = int(ceil(notional * buyback_fee_factor))
        treasury_fee = int(ceil(notional * treasury_fee_factor))

        # Apply discounts and rewards in the following order

        # 1. Volume rebates
        # 3. Referral discounts
        # 2. Volume discounts
        # 4. Referral rewards

        volume_rebate_factor = self.get_party_volume_rebate_factor(
            epoch=epoch.seq - 1, party=maker
        )
        effective_rebate_factor = min(
            volume_rebate_factor,
            buyback_fee_factor + treasury_fee_factor,
        )
        (
            buyback_fee,
            treasury_fee,
            high_volume_maker_fee,
        ) = self.apply_rebate_factor(
            notional, buyback_fee, treasury_fee, effective_rebate_factor
        )

        (
            maker_fee,
            liquidity_fee,
            infrastructure_fee,
            maker_fee_referral_discount,
            liquidity_fee_referral_discount,
            infrastructure_fee_referral_discount,
        ) = self.apply_discount_factors(
            maker_fee, liquidity_fee, infrastructure_fee, referral_discount_factors
        )

        (
            maker_fee,
            liquidity_fee,
            infrastructure_fee,
            maker_fee_volume_discount,
            liquidity_fee_volume_discount,
            infrastructure_fee_volume_discount,
        ) = self.apply_discount_factors(
            maker_fee, liquidity_fee, infrastructure_fee, volume_discount_factors
        )

        (
            maker_fee,
            liquidity_fee,
            infrastructure_fee,
            maker_fee_referral_reward,
            liquidity_fee_referral_reward,
            infrastructure_fee_referral_reward,
        ) = self.apply_reward_factors(
            maker_fee, liquidity_fee, infrastructure_fee, referral_reward_factors
        )

        try:
            self.__check_maker_fee(
                fees,
                maker_fee_referral_reward,
                maker_fee_referral_discount,
                maker_fee_volume_discount,
                maker_fee,
            )
        except AssertionError as e:
            logger.debug(trade)
            logger.debug(f"party: {taker}")
            logger.debug(f"epoch: {epoch.seq}")
            logger.debug(
                f"referral maker reward factor: {referral_reward_factors.maker_reward_factor if referral_reward_factors else 0}"
            )
            logger.debug(
                f"referral maker discount factor: {referral_discount_factors.maker_discount_factor if referral_discount_factors else 0}"
            )
            logger.debug(
                f"volume maker discount factor: {volume_discount_factors.maker_discount_factor if volume_discount_factors else 0}"
            )
            raise e
        try:
            self.__check_infrastructure_fee(
                fees,
                infrastructure_fee_referral_reward,
                infrastructure_fee_referral_discount,
                infrastructure_fee_volume_discount,
                infrastructure_fee,
            )
        except AssertionError as e:
            logger.debug(trade)
            logger.debug(f"party: {taker}")
            logger.debug(f"epoch: {epoch.seq}")
            logger.debug(
                f"referral infrastructure reward factor: {referral_reward_factors.infrastructure_reward_factor if referral_reward_factors else 0}"
            )
            logger.debug(
                f"referral infrastructure discount factor: {referral_discount_factors.infrastructure_discount_factor if referral_discount_factors else 0}"
            )
            logger.debug(
                f"volume infrastructure discount factor: {volume_discount_factors.infrastructure_discount_factor if volume_discount_factors else 0}"
            )
            raise e
        try:
            self.__check_high_volume_maker_fee(
                fees,
                buyback_fee,
                treasury_fee,
                high_volume_maker_fee,
            )
        except AssertionError as e:
            logger.debug(trade)
            logger.debug(f"party: {maker}")
            logger.debug(f"epoch: {epoch.seq}")
            logger.debug(f"buyback fee factor: {buyback_fee_factor}")
            logger.debug(f"treasury fee factor: {treasury_fee_factor}")
            logger.debug(f"additional maker rebate: {volume_rebate_factor}")
            raise e

    def __check_maker_fee(
        self,
        fee: protos.vega.vega.Fee,
        maker_fee_referral_reward: int,
        maker_fee_referral_discount: int,
        maker_fee_volume_discount: int,
        maker_fee: int,
    ):
        def __get_equality(err: int):
            if err == 0:
                return "=="
            elif err <= self.acceptable_error:
                return "~="
            elif err > self.acceptable_error:
                return "!="

        try:
            referral_discount_error = abs(
                int(fee.maker_fee_referrer_discount) - maker_fee_referral_discount
            )
            volume_discount_error = abs(
                int(fee.maker_fee_volume_discount) - maker_fee_volume_discount
            )
            final_fee_error = abs(int(fee.maker_fee) - maker_fee)
            assert referral_discount_error <= self.acceptable_error
            assert volume_discount_error <= self.acceptable_error
            assert final_fee_error <= self.acceptable_error

        except AssertionError as e:
            logger.warning(f"maker referral reward: {maker_fee_referral_reward}")
            logger.debug(
                f"maker referral discount: {fee.maker_fee_referrer_discount} {__get_equality(referral_discount_error)} {maker_fee_referral_discount}"
            )
            logger.debug(
                f"maker volume discount: {fee.maker_fee_volume_discount} {__get_equality(volume_discount_error)} {maker_fee_volume_discount}"
            )
            logger.debug(
                f"maker final fee: {fee.maker_fee} {__get_equality(final_fee_error)} {maker_fee}"
            )
            raise e

    def __check_high_volume_maker_fee(
        self,
        fee: protos.vega.vega.Fee,
        buyback_fee: int,
        treasury_fee: int,
        high_volume_maker_fee: int,
    ):
        def __get_equality(err: int):
            if err == 0:
                return "=="
            elif err <= self.acceptable_error:
                return "~="
            elif err > self.acceptable_error:
                return "!="

        try:
            buyback_fee_error = abs(int(fee.buy_back_fee) - buyback_fee)
            treasury_fee_error = abs(int(fee.treasury_fee) - treasury_fee)
            high_volume_maker_fee_error = abs(
                int(fee.high_volume_maker_fee) - high_volume_maker_fee
            )
            assert buyback_fee_error <= self.acceptable_error
            assert treasury_fee_error <= self.acceptable_error
            assert high_volume_maker_fee_error <= self.acceptable_error
        except AssertionError as e:
            logger.debug(
                f"buyback fee: {fee.buy_back_fee} {__get_equality(buyback_fee_error)} {buyback_fee}"
            )
            logger.debug(
                f"treasury fee: {fee.treasury_fee} {__get_equality(treasury_fee_error)} {treasury_fee}"
            )
            logger.debug(
                f"additional maker rebate: {fee.high_volume_maker_fee} {__get_equality(high_volume_maker_fee_error)} {high_volume_maker_fee}"
            )
            raise e

    def __check_infrastructure_fee(
        self,
        fee: protos.vega.vega.Fee,
        infrastructure_fee_referral_reward: int,
        infrastructure_fee_referral_discount: int,
        infrastructure_fee_volume_discount: int,
        infrastructure_fee: int,
    ):

        def __get_equality(err: int):
            if err == 0:
                return "=="
            elif err <= self.acceptable_error:
                return "~="
            elif err > self.acceptable_error:
                return "!="

        try:
            referral_discount_error = abs(
                int(fee.infrastructure_fee_referrer_discount)
                - infrastructure_fee_referral_discount
            )
            volume_discount_error = abs(
                int(fee.infrastructure_fee_volume_discount)
                - infrastructure_fee_volume_discount
            )
            final_fee_error = abs(int(fee.infrastructure_fee) - infrastructure_fee)
            assert referral_discount_error <= self.acceptable_error
            assert volume_discount_error <= self.acceptable_error
            assert final_fee_error <= self.acceptable_error

        except AssertionError as e:
            logger.warning(
                f"infrastructure referral reward: {infrastructure_fee_referral_reward}"
            )
            logger.warning(
                f"infrastructure referral discount: {fee.infrastructure_fee_referrer_discount} {__get_equality(referral_discount_error)} {infrastructure_fee_referral_discount}"
            )
            logger.warning(
                f"infrastructure volume discount: {fee.infrastructure_fee_volume_discount} {__get_equality(volume_discount_error)} {infrastructure_fee_volume_discount}"
            )
            logger.warning(
                f"infrastructure final fee: {fee.infrastructure_fee} {__get_equality(final_fee_error)} {infrastructure_fee}"
            )
            raise e


if __name__ == "__main__":

    import logging

    logging.basicConfig(level=logging.DEBUG)

    # s = Service(network=Network.NETWORK_TESTNET)
    s = Service(network=Network.NETWORK_LOCAL, port_data_node=55351)
    c = Checker(s)
    c.check()
