# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/vega.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import markets_pb2 as vega_dot_markets__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0fvega/vega.proto\x12\x04vega\x1a\x12vega/markets.proto"\x17\n\x05Party\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id"N\n\nRiskFactor\x12\x16\n\x06market\x18\x01 \x01(\tR\x06market\x12\x14\n\x05short\x18\x02 \x01(\tR\x05short\x12\x12\n\x04long\x18\x03 \x01(\tR\x04long"Z\n\x0bPeggedOrder\x12\x33\n\treference\x18\x01 \x01(\x0e\x32\x15.vega.PeggedReferenceR\treference\x12\x16\n\x06offset\x18\x02 \x01(\tR\x06offset"\xb0\t\n\x05Order\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x1b\n\tmarket_id\x18\x02 \x01(\tR\x08marketId\x12\x19\n\x08party_id\x18\x03 \x01(\tR\x07partyId\x12\x1e\n\x04side\x18\x04 \x01(\x0e\x32\n.vega.SideR\x04side\x12\x14\n\x05price\x18\x05 \x01(\tR\x05price\x12\x12\n\x04size\x18\x06 \x01(\x04R\x04size\x12\x1c\n\tremaining\x18\x07 \x01(\x04R\tremaining\x12;\n\rtime_in_force\x18\x08 \x01(\x0e\x32\x17.vega.Order.TimeInForceR\x0btimeInForce\x12$\n\x04type\x18\t \x01(\x0e\x32\x10.vega.Order.TypeR\x04type\x12\x1d\n\ncreated_at\x18\n \x01(\x03R\tcreatedAt\x12*\n\x06status\x18\x0b \x01(\x0e\x32\x12.vega.Order.StatusR\x06status\x12\x1d\n\nexpires_at\x18\x0c \x01(\x03R\texpiresAt\x12\x1c\n\treference\x18\r \x01(\tR\treference\x12-\n\x06reason\x18\x0e \x01(\x0e\x32\x10.vega.OrderErrorH\x00R\x06reason\x88\x01\x01\x12\x1d\n\nupdated_at\x18\x0f \x01(\x03R\tupdatedAt\x12\x18\n\x07version\x18\x10 \x01(\x04R\x07version\x12\x19\n\x08\x62\x61tch_id\x18\x11 \x01(\x04R\x07\x62\x61tchId\x12\x34\n\x0cpegged_order\x18\x12 \x01(\x0b\x32\x11.vega.PeggedOrderR\x0bpeggedOrder\x12\x34\n\x16liquidity_provision_id\x18\x13 \x01(\tR\x14liquidityProvisionId\x12\x1b\n\tpost_only\x18\x14 \x01(\x08R\x08postOnly\x12\x1f\n\x0breduce_only\x18\x15 \x01(\x08R\nreduceOnly"\xb6\x01\n\x0bTimeInForce\x12\x1d\n\x19TIME_IN_FORCE_UNSPECIFIED\x10\x00\x12\x15\n\x11TIME_IN_FORCE_GTC\x10\x01\x12\x15\n\x11TIME_IN_FORCE_GTT\x10\x02\x12\x15\n\x11TIME_IN_FORCE_IOC\x10\x03\x12\x15\n\x11TIME_IN_FORCE_FOK\x10\x04\x12\x15\n\x11TIME_IN_FORCE_GFA\x10\x05\x12\x15\n\x11TIME_IN_FORCE_GFN\x10\x06"O\n\x04Type\x12\x14\n\x10TYPE_UNSPECIFIED\x10\x00\x12\x0e\n\nTYPE_LIMIT\x10\x01\x12\x0f\n\x0bTYPE_MARKET\x10\x02\x12\x10\n\x0cTYPE_NETWORK\x10\x03"\xc9\x01\n\x06Status\x12\x16\n\x12STATUS_UNSPECIFIED\x10\x00\x12\x11\n\rSTATUS_ACTIVE\x10\x01\x12\x12\n\x0eSTATUS_EXPIRED\x10\x02\x12\x14\n\x10STATUS_CANCELLED\x10\x03\x12\x12\n\x0eSTATUS_STOPPED\x10\x04\x12\x11\n\rSTATUS_FILLED\x10\x05\x12\x13\n\x0fSTATUS_REJECTED\x10\x06\x12\x1b\n\x17STATUS_PARTIALLY_FILLED\x10\x07\x12\x11\n\rSTATUS_PARKED\x10\x08\x42\t\n\x07_reason"B\n\x1dOrderCancellationConfirmation\x12!\n\x05order\x18\x01 \x01(\x0b\x32\x0b.vega.OrderR\x05order"\xa0\x01\n\x11OrderConfirmation\x12!\n\x05order\x18\x01 \x01(\x0b\x32\x0b.vega.OrderR\x05order\x12#\n\x06trades\x18\x02 \x03(\x0b\x32\x0b.vega.TradeR\x06trades\x12\x43\n\x17passive_orders_affected\x18\x03 \x03(\x0b\x32\x0b.vega.OrderR\x15passiveOrdersAffected"\xd3\x01\n\x16\x41uctionIndicativeState\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12)\n\x10indicative_price\x18\x02 \x01(\tR\x0findicativePrice\x12+\n\x11indicative_volume\x18\x03 \x01(\x04R\x10indicativeVolume\x12#\n\rauction_start\x18\x04 \x01(\x03R\x0c\x61uctionStart\x12\x1f\n\x0b\x61uction_end\x18\x05 \x01(\x03R\nauctionEnd"\xdb\x04\n\x05Trade\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x1b\n\tmarket_id\x18\x02 \x01(\tR\x08marketId\x12\x14\n\x05price\x18\x03 \x01(\tR\x05price\x12\x12\n\x04size\x18\x04 \x01(\x04R\x04size\x12\x14\n\x05\x62uyer\x18\x05 \x01(\tR\x05\x62uyer\x12\x16\n\x06seller\x18\x06 \x01(\tR\x06seller\x12(\n\taggressor\x18\x07 \x01(\x0e\x32\n.vega.SideR\taggressor\x12\x1b\n\tbuy_order\x18\x08 \x01(\tR\x08\x62uyOrder\x12\x1d\n\nsell_order\x18\t \x01(\tR\tsellOrder\x12\x1c\n\ttimestamp\x18\n \x01(\x03R\ttimestamp\x12$\n\x04type\x18\x0b \x01(\x0e\x32\x10.vega.Trade.TypeR\x04type\x12&\n\tbuyer_fee\x18\x0c \x01(\x0b\x32\t.vega.FeeR\x08\x62uyerFee\x12(\n\nseller_fee\x18\r \x01(\x0b\x32\t.vega.FeeR\tsellerFee\x12.\n\x13\x62uyer_auction_batch\x18\x0e \x01(\x04R\x11\x62uyerAuctionBatch\x12\x30\n\x14seller_auction_batch\x18\x0f \x01(\x04R\x12sellerAuctionBatch"o\n\x04Type\x12\x14\n\x10TYPE_UNSPECIFIED\x10\x00\x12\x10\n\x0cTYPE_DEFAULT\x10\x01\x12\x1f\n\x1bTYPE_NETWORK_CLOSE_OUT_GOOD\x10\x02\x12\x1e\n\x1aTYPE_NETWORK_CLOSE_OUT_BAD\x10\x03"v\n\x03\x46\x65\x65\x12\x1b\n\tmaker_fee\x18\x01 \x01(\tR\x08makerFee\x12-\n\x12infrastructure_fee\x18\x02 \x01(\tR\x11infrastructureFee\x12#\n\rliquidity_fee\x18\x03 \x01(\tR\x0cliquidityFee"/\n\x08TradeSet\x12#\n\x06trades\x18\x01 \x03(\x0b\x32\x0b.vega.TradeR\x06trades"\xd6\x01\n\x06\x43\x61ndle\x12\x1c\n\ttimestamp\x18\x01 \x01(\x03R\ttimestamp\x12\x1a\n\x08\x64\x61tetime\x18\x02 \x01(\tR\x08\x64\x61tetime\x12\x12\n\x04high\x18\x03 \x01(\tR\x04high\x12\x10\n\x03low\x18\x04 \x01(\tR\x03low\x12\x12\n\x04open\x18\x05 \x01(\tR\x04open\x12\x14\n\x05\x63lose\x18\x06 \x01(\tR\x05\x63lose\x12\x16\n\x06volume\x18\x07 \x01(\x04R\x06volume\x12*\n\x08interval\x18\x08 \x01(\x0e\x32\x0e.vega.IntervalR\x08interval"d\n\nPriceLevel\x12\x14\n\x05price\x18\x01 \x01(\tR\x05price\x12(\n\x10number_of_orders\x18\x02 \x01(\x04R\x0enumberOfOrders\x12\x16\n\x06volume\x18\x03 \x01(\x04R\x06volume"\x9d\x01\n\x0bMarketDepth\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12"\n\x03\x62uy\x18\x02 \x03(\x0b\x32\x10.vega.PriceLevelR\x03\x62uy\x12$\n\x04sell\x18\x03 \x03(\x0b\x32\x10.vega.PriceLevelR\x04sell\x12\'\n\x0fsequence_number\x18\x04 \x01(\x04R\x0esequenceNumber"\xdd\x01\n\x11MarketDepthUpdate\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12"\n\x03\x62uy\x18\x02 \x03(\x0b\x32\x10.vega.PriceLevelR\x03\x62uy\x12$\n\x04sell\x18\x03 \x03(\x0b\x32\x10.vega.PriceLevelR\x04sell\x12\'\n\x0fsequence_number\x18\x04 \x01(\x04R\x0esequenceNumber\x12\x38\n\x18previous_sequence_number\x18\x05 \x01(\x04R\x16previousSequenceNumber"\xf7\x02\n\x08Position\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12\x19\n\x08party_id\x18\x02 \x01(\tR\x07partyId\x12\x1f\n\x0bopen_volume\x18\x03 \x01(\x03R\nopenVolume\x12!\n\x0crealised_pnl\x18\x04 \x01(\tR\x0brealisedPnl\x12%\n\x0eunrealised_pnl\x18\x05 \x01(\tR\runrealisedPnl\x12.\n\x13\x61verage_entry_price\x18\x06 \x01(\tR\x11\x61verageEntryPrice\x12\x1d\n\nupdated_at\x18\x07 \x01(\x03R\tupdatedAt\x12:\n\x19loss_socialisation_amount\x18\x08 \x01(\tR\x17lossSocialisationAmount\x12=\n\x0fposition_status\x18\t \x01(\x0e\x32\x14.vega.PositionStatusR\x0epositionStatus"=\n\rPositionTrade\x12\x16\n\x06volume\x18\x01 \x01(\x03R\x06volume\x12\x14\n\x05price\x18\x02 \x01(\tR\x05price"\xe4\x02\n\x07\x44\x65posit\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12,\n\x06status\x18\x02 \x01(\x0e\x32\x14.vega.Deposit.StatusR\x06status\x12\x19\n\x08party_id\x18\x03 \x01(\tR\x07partyId\x12\x14\n\x05\x61sset\x18\x04 \x01(\tR\x05\x61sset\x12\x16\n\x06\x61mount\x18\x05 \x01(\tR\x06\x61mount\x12\x17\n\x07tx_hash\x18\x06 \x01(\tR\x06txHash\x12-\n\x12\x63redited_timestamp\x18\x07 \x01(\x03R\x11\x63reditedTimestamp\x12+\n\x11\x63reated_timestamp\x18\x08 \x01(\x03R\x10\x63reatedTimestamp"]\n\x06Status\x12\x16\n\x12STATUS_UNSPECIFIED\x10\x00\x12\x0f\n\x0bSTATUS_OPEN\x10\x01\x12\x14\n\x10STATUS_CANCELLED\x10\x02\x12\x14\n\x10STATUS_FINALIZED\x10\x03"\xa8\x03\n\nWithdrawal\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x19\n\x08party_id\x18\x02 \x01(\tR\x07partyId\x12\x16\n\x06\x61mount\x18\x03 \x01(\tR\x06\x61mount\x12\x14\n\x05\x61sset\x18\x04 \x01(\tR\x05\x61sset\x12/\n\x06status\x18\x05 \x01(\x0e\x32\x17.vega.Withdrawal.StatusR\x06status\x12\x10\n\x03ref\x18\x06 \x01(\tR\x03ref\x12\x17\n\x07tx_hash\x18\x08 \x01(\tR\x06txHash\x12+\n\x11\x63reated_timestamp\x18\t \x01(\x03R\x10\x63reatedTimestamp\x12/\n\x13withdrawn_timestamp\x18\n \x01(\x03R\x12withdrawnTimestamp\x12#\n\x03\x65xt\x18\x0b \x01(\x0b\x32\x11.vega.WithdrawExtR\x03\x65xt"\\\n\x06Status\x12\x16\n\x12STATUS_UNSPECIFIED\x10\x00\x12\x0f\n\x0bSTATUS_OPEN\x10\x01\x12\x13\n\x0fSTATUS_REJECTED\x10\x02\x12\x14\n\x10STATUS_FINALIZED\x10\x03J\x04\x08\x07\x10\x08"D\n\x0bWithdrawExt\x12.\n\x05\x65rc20\x18\x01 \x01(\x0b\x32\x16.vega.Erc20WithdrawExtH\x00R\x05\x65rc20B\x05\n\x03\x65xt"=\n\x10\x45rc20WithdrawExt\x12)\n\x10receiver_address\x18\x01 \x01(\tR\x0freceiverAddress"\xa3\x01\n\x07\x41\x63\x63ount\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x14\n\x05owner\x18\x02 \x01(\tR\x05owner\x12\x18\n\x07\x62\x61lance\x18\x03 \x01(\tR\x07\x62\x61lance\x12\x14\n\x05\x61sset\x18\x04 \x01(\tR\x05\x61sset\x12\x1b\n\tmarket_id\x18\x05 \x01(\tR\x08marketId\x12%\n\x04type\x18\x06 \x01(\x0e\x32\x11.vega.AccountTypeR\x04type"?\n\x0f\x46inancialAmount\x12\x16\n\x06\x61mount\x18\x01 \x01(\tR\x06\x61mount\x12\x14\n\x05\x61sset\x18\x02 \x01(\tR\x05\x61sset"\xb3\x01\n\x08Transfer\x12\x14\n\x05owner\x18\x01 \x01(\tR\x05owner\x12-\n\x06\x61mount\x18\x02 \x01(\x0b\x32\x15.vega.FinancialAmountR\x06\x61mount\x12&\n\x04type\x18\x03 \x01(\x0e\x32\x12.vega.TransferTypeR\x04type\x12\x1d\n\nmin_amount\x18\x04 \x01(\tR\tminAmount\x12\x1b\n\tmarket_id\x18\x05 \x01(\tR\x08marketId"\x84\x01\n\x10\x44ispatchStrategy\x12(\n\x10\x61sset_for_metric\x18\x01 \x01(\tR\x0e\x61ssetForMetric\x12,\n\x06metric\x18\x02 \x01(\x0e\x32\x14.vega.DispatchMetricR\x06metric\x12\x18\n\x07markets\x18\x03 \x03(\tR\x07markets"\xe6\x01\n\x0fTransferRequest\x12\x30\n\x0c\x66rom_account\x18\x01 \x03(\x0b\x32\r.vega.AccountR\x0b\x66romAccount\x12,\n\nto_account\x18\x02 \x03(\x0b\x32\r.vega.AccountR\ttoAccount\x12\x16\n\x06\x61mount\x18\x03 \x01(\tR\x06\x61mount\x12\x1d\n\nmin_amount\x18\x04 \x01(\tR\tminAmount\x12\x14\n\x05\x61sset\x18\x05 \x01(\tR\x05\x61sset\x12&\n\x04type\x18\x07 \x01(\x0e\x32\x12.vega.TransferTypeR\x04type"\xa7\x01\n\x0e\x41\x63\x63ountDetails\x12\x19\n\x08\x61sset_id\x18\x01 \x01(\tR\x07\x61ssetId\x12%\n\x04type\x18\x02 \x01(\x0e\x32\x11.vega.AccountTypeR\x04type\x12\x19\n\x05owner\x18\x03 \x01(\tH\x00R\x05owner\x88\x01\x01\x12 \n\tmarket_id\x18\x04 \x01(\tH\x01R\x08marketId\x88\x01\x01\x42\x08\n\x06_ownerB\x0c\n\n_market_id"\xb9\x02\n\x0bLedgerEntry\x12\x37\n\x0c\x66rom_account\x18\x01 \x01(\x0b\x32\x14.vega.AccountDetailsR\x0b\x66romAccount\x12\x33\n\nto_account\x18\x02 \x01(\x0b\x32\x14.vega.AccountDetailsR\ttoAccount\x12\x16\n\x06\x61mount\x18\x03 \x01(\tR\x06\x61mount\x12&\n\x04type\x18\x04 \x01(\x0e\x32\x12.vega.TransferTypeR\x04type\x12\x1c\n\ttimestamp\x18\x05 \x01(\x03R\ttimestamp\x12\x30\n\x14\x66rom_account_balance\x18\x06 \x01(\tR\x12\x66romAccountBalance\x12,\n\x12to_account_balance\x18\x07 \x01(\tR\x10toAccountBalance"_\n\x13PostTransferBalance\x12.\n\x07\x61\x63\x63ount\x18\x01 \x01(\x0b\x32\x14.vega.AccountDetailsR\x07\x61\x63\x63ount\x12\x18\n\x07\x62\x61lance\x18\x02 \x01(\tR\x07\x62\x61lance"t\n\x0eLedgerMovement\x12+\n\x07\x65ntries\x18\x01 \x03(\x0b\x32\x11.vega.LedgerEntryR\x07\x65ntries\x12\x35\n\x08\x62\x61lances\x18\x02 \x03(\x0b\x32\x19.vega.PostTransferBalanceR\x08\x62\x61lances"\xad\x02\n\x0cMarginLevels\x12-\n\x12maintenance_margin\x18\x01 \x01(\tR\x11maintenanceMargin\x12!\n\x0csearch_level\x18\x02 \x01(\tR\x0bsearchLevel\x12%\n\x0einitial_margin\x18\x03 \x01(\tR\rinitialMargin\x12\x38\n\x18\x63ollateral_release_level\x18\x04 \x01(\tR\x16\x63ollateralReleaseLevel\x12\x19\n\x08party_id\x18\x05 \x01(\tR\x07partyId\x12\x1b\n\tmarket_id\x18\x06 \x01(\tR\x08marketId\x12\x14\n\x05\x61sset\x18\x07 \x01(\tR\x05\x61sset\x12\x1c\n\ttimestamp\x18\x08 \x01(\x03R\ttimestamp"\xe5\n\n\nMarketData\x12\x1d\n\nmark_price\x18\x01 \x01(\tR\tmarkPrice\x12$\n\x0e\x62\x65st_bid_price\x18\x02 \x01(\tR\x0c\x62\x65stBidPrice\x12&\n\x0f\x62\x65st_bid_volume\x18\x03 \x01(\x04R\rbestBidVolume\x12(\n\x10\x62\x65st_offer_price\x18\x04 \x01(\tR\x0e\x62\x65stOfferPrice\x12*\n\x11\x62\x65st_offer_volume\x18\x05 \x01(\x04R\x0f\x62\x65stOfferVolume\x12\x31\n\x15\x62\x65st_static_bid_price\x18\x06 \x01(\tR\x12\x62\x65stStaticBidPrice\x12\x33\n\x16\x62\x65st_static_bid_volume\x18\x07 \x01(\x04R\x13\x62\x65stStaticBidVolume\x12\x35\n\x17\x62\x65st_static_offer_price\x18\x08 \x01(\tR\x14\x62\x65stStaticOfferPrice\x12\x37\n\x18\x62\x65st_static_offer_volume\x18\t \x01(\x04R\x15\x62\x65stStaticOfferVolume\x12\x1b\n\tmid_price\x18\n \x01(\tR\x08midPrice\x12(\n\x10static_mid_price\x18\x0b \x01(\tR\x0estaticMidPrice\x12\x16\n\x06market\x18\x0c \x01(\tR\x06market\x12\x1c\n\ttimestamp\x18\r \x01(\x03R\ttimestamp\x12#\n\ropen_interest\x18\x0e \x01(\x04R\x0copenInterest\x12\x1f\n\x0b\x61uction_end\x18\x0f \x01(\x03R\nauctionEnd\x12#\n\rauction_start\x18\x10 \x01(\x03R\x0c\x61uctionStart\x12)\n\x10indicative_price\x18\x11 \x01(\tR\x0findicativePrice\x12+\n\x11indicative_volume\x18\x12 \x01(\x04R\x10indicativeVolume\x12H\n\x13market_trading_mode\x18\x13 \x01(\x0e\x32\x18.vega.Market.TradingModeR\x11marketTradingMode\x12.\n\x07trigger\x18\x14 \x01(\x0e\x32\x14.vega.AuctionTriggerR\x07trigger\x12\x41\n\x11\x65xtension_trigger\x18\x15 \x01(\x0e\x32\x14.vega.AuctionTriggerR\x10\x65xtensionTrigger\x12!\n\x0ctarget_stake\x18\x16 \x01(\tR\x0btargetStake\x12%\n\x0esupplied_stake\x18\x17 \x01(\tR\rsuppliedStake\x12S\n\x17price_monitoring_bounds\x18\x18 \x03(\x0b\x32\x1b.vega.PriceMonitoringBoundsR\x15priceMonitoringBounds\x12,\n\x12market_value_proxy\x18\x19 \x01(\tR\x10marketValueProxy\x12`\n\x1cliquidity_provider_fee_share\x18\x1a \x03(\x0b\x32\x1f.vega.LiquidityProviderFeeShareR\x19liquidityProviderFeeShare\x12\x35\n\x0cmarket_state\x18\x1b \x01(\x0e\x32\x12.vega.Market.StateR\x0bmarketState\x12-\n\x13next_mark_to_market\x18\x1c \x01(\x03R\x10nextMarkToMarket\x12*\n\x11last_traded_price\x18\x1d \x01(\tR\x0flastTradedPrice"\xba\x01\n\x19LiquidityProviderFeeShare\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party\x12*\n\x11\x65quity_like_share\x18\x02 \x01(\tR\x0f\x65quityLikeShare\x12\x36\n\x17\x61verage_entry_valuation\x18\x03 \x01(\tR\x15\x61verageEntryValuation\x12#\n\raverage_score\x18\x04 \x01(\tR\x0c\x61verageScore"\xc8\x01\n\x15PriceMonitoringBounds\x12&\n\x0fmin_valid_price\x18\x01 \x01(\tR\rminValidPrice\x12&\n\x0fmax_valid_price\x18\x02 \x01(\tR\rmaxValidPrice\x12\x36\n\x07trigger\x18\x03 \x01(\x0b\x32\x1c.vega.PriceMonitoringTriggerR\x07trigger\x12\'\n\x0freference_price\x18\x04 \x01(\tR\x0ereferencePrice"Q\n\x0b\x45rrorDetail\x12\x12\n\x04\x63ode\x18\x01 \x01(\x05R\x04\x63ode\x12\x18\n\x07message\x18\x02 \x01(\tR\x07message\x12\x14\n\x05inner\x18\x03 \x01(\tR\x05inner":\n\x10NetworkParameter\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12\x14\n\x05value\x18\x02 \x01(\tR\x05value"\x82\x03\n\rNetworkLimits\x12,\n\x12\x63\x61n_propose_market\x18\x01 \x01(\x08R\x10\x63\x61nProposeMarket\x12*\n\x11\x63\x61n_propose_asset\x18\x02 \x01(\x08R\x0f\x63\x61nProposeAsset\x12\x34\n\x16propose_market_enabled\x18\x04 \x01(\x08R\x14proposeMarketEnabled\x12\x32\n\x15propose_asset_enabled\x18\x05 \x01(\x08R\x13proposeAssetEnabled\x12%\n\x0egenesis_loaded\x18\x07 \x01(\x08R\rgenesisLoaded\x12=\n\x1bpropose_market_enabled_from\x18\x08 \x01(\x03R\x18proposeMarketEnabledFrom\x12;\n\x1apropose_asset_enabled_from\x18\t \x01(\x03R\x17proposeAssetEnabledFromJ\x04\x08\x03\x10\x04J\x04\x08\x06\x10\x07"}\n\x0eLiquidityOrder\x12\x33\n\treference\x18\x01 \x01(\x0e\x32\x15.vega.PeggedReferenceR\treference\x12\x1e\n\nproportion\x18\x02 \x01(\rR\nproportion\x12\x16\n\x06offset\x18\x03 \x01(\tR\x06offset"s\n\x17LiquidityOrderReference\x12\x19\n\x08order_id\x18\x01 \x01(\tR\x07orderId\x12=\n\x0fliquidity_order\x18\x02 \x01(\x0b\x32\x14.vega.LiquidityOrderR\x0eliquidityOrder"\xd2\x04\n\x12LiquidityProvision\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x19\n\x08party_id\x18\x02 \x01(\tR\x07partyId\x12\x1d\n\ncreated_at\x18\x03 \x01(\x03R\tcreatedAt\x12\x1d\n\nupdated_at\x18\x04 \x01(\x03R\tupdatedAt\x12\x1b\n\tmarket_id\x18\x05 \x01(\tR\x08marketId\x12+\n\x11\x63ommitment_amount\x18\x06 \x01(\tR\x10\x63ommitmentAmount\x12\x10\n\x03\x66\x65\x65\x18\x07 \x01(\tR\x03\x66\x65\x65\x12\x33\n\x05sells\x18\x08 \x03(\x0b\x32\x1d.vega.LiquidityOrderReferenceR\x05sells\x12\x31\n\x04\x62uys\x18\t \x03(\x0b\x32\x1d.vega.LiquidityOrderReferenceR\x04\x62uys\x12\x18\n\x07version\x18\n \x01(\x04R\x07version\x12\x37\n\x06status\x18\x0b \x01(\x0e\x32\x1f.vega.LiquidityProvision.StatusR\x06status\x12\x1c\n\treference\x18\x0c \x01(\tR\treference"\x9d\x01\n\x06Status\x12\x16\n\x12STATUS_UNSPECIFIED\x10\x00\x12\x11\n\rSTATUS_ACTIVE\x10\x01\x12\x12\n\x0eSTATUS_STOPPED\x10\x02\x12\x14\n\x10STATUS_CANCELLED\x10\x03\x12\x13\n\x0fSTATUS_REJECTED\x10\x04\x12\x15\n\x11STATUS_UNDEPLOYED\x10\x05\x12\x12\n\x0eSTATUS_PENDING\x10\x06"\xd0\x03\n\x0e\x45thereumConfig\x12\x1d\n\nnetwork_id\x18\x01 \x01(\tR\tnetworkId\x12\x19\n\x08\x63hain_id\x18\x02 \x01(\tR\x07\x63hainId\x12Z\n\x1a\x63ollateral_bridge_contract\x18\x03 \x01(\x0b\x32\x1c.vega.EthereumContractConfigR\x18\x63ollateralBridgeContract\x12$\n\rconfirmations\x18\x04 \x01(\rR\rconfirmations\x12T\n\x17staking_bridge_contract\x18\x05 \x01(\x0b\x32\x1c.vega.EthereumContractConfigR\x15stakingBridgeContract\x12R\n\x16token_vesting_contract\x18\x06 \x01(\x0b\x32\x1c.vega.EthereumContractConfigR\x14tokenVestingContract\x12X\n\x19multisig_control_contract\x18\x07 \x01(\x0b\x32\x1c.vega.EthereumContractConfigR\x17multisigControlContract"j\n\x16\x45thereumContractConfig\x12\x18\n\x07\x61\x64\x64ress\x18\x01 \x01(\tR\x07\x61\x64\x64ress\x12\x36\n\x17\x64\x65ployment_block_height\x18\x06 \x01(\x04R\x15\x64\x65ploymentBlockHeight"\xac\x01\n\x0f\x45pochTimestamps\x12\x1d\n\nstart_time\x18\x01 \x01(\x03R\tstartTime\x12\x1f\n\x0b\x65xpiry_time\x18\x02 \x01(\x03R\nexpiryTime\x12\x19\n\x08\x65nd_time\x18\x03 \x01(\x03R\x07\x65ndTime\x12\x1f\n\x0b\x66irst_block\x18\x04 \x01(\x04R\nfirstBlock\x12\x1d\n\nlast_block\x18\x05 \x01(\x04R\tlastBlock"\xb0\x01\n\x05\x45poch\x12\x10\n\x03seq\x18\x01 \x01(\x04R\x03seq\x12\x35\n\ntimestamps\x18\x02 \x01(\x0b\x32\x15.vega.EpochTimestampsR\ntimestamps\x12*\n\nvalidators\x18\x03 \x03(\x0b\x32\n.vega.NodeR\nvalidators\x12\x32\n\x0b\x64\x65legations\x18\x04 \x03(\x0b\x32\x10.vega.DelegationR\x0b\x64\x65legations"\x8e\x01\n\x12\x45pochParticipation\x12!\n\x05\x65poch\x18\x01 \x01(\x0b\x32\x0b.vega.EpochR\x05\x65poch\x12\x18\n\x07offline\x18\x02 \x01(\x04R\x07offline\x12\x16\n\x06online\x18\x03 \x01(\x04R\x06online\x12#\n\rtotal_rewards\x18\x04 \x01(\x01R\x0ctotalRewards"S\n\tEpochData\x12\x14\n\x05total\x18\x01 \x01(\x05R\x05total\x12\x18\n\x07offline\x18\x02 \x01(\x05R\x07offline\x12\x16\n\x06online\x18\x03 \x01(\x05R\x06online"\x9b\x02\n\x0cRankingScore\x12\x1f\n\x0bstake_score\x18\x01 \x01(\tR\nstakeScore\x12+\n\x11performance_score\x18\x02 \x01(\tR\x10performanceScore\x12\x42\n\x0fprevious_status\x18\x03 \x01(\x0e\x32\x19.vega.ValidatorNodeStatusR\x0epreviousStatus\x12\x31\n\x06status\x18\x04 \x01(\x0e\x32\x19.vega.ValidatorNodeStatusR\x06status\x12!\n\x0cvoting_power\x18\x05 \x01(\rR\x0bvotingPower\x12#\n\rranking_score\x18\x06 \x01(\tR\x0crankingScore"\xab\x02\n\x0bRewardScore\x12.\n\x13raw_validator_score\x18\x01 \x01(\tR\x11rawValidatorScore\x12+\n\x11performance_score\x18\x02 \x01(\tR\x10performanceScore\x12%\n\x0emultisig_score\x18\x03 \x01(\tR\rmultisigScore\x12\'\n\x0fvalidator_score\x18\x04 \x01(\tR\x0evalidatorScore\x12)\n\x10normalised_score\x18\x05 \x01(\tR\x0fnormalisedScore\x12\x44\n\x10validator_status\x18\x06 \x01(\x0e\x32\x19.vega.ValidatorNodeStatusR\x0fvalidatorStatus"\xb3\x05\n\x04Node\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x17\n\x07pub_key\x18\x02 \x01(\tR\x06pubKey\x12\x1c\n\ntm_pub_key\x18\x03 \x01(\tR\x08tmPubKey\x12)\n\x10\x65thereum_address\x18\x04 \x01(\tR\x0f\x65thereumAddress\x12\x19\n\x08info_url\x18\x05 \x01(\tR\x07infoUrl\x12\x1a\n\x08location\x18\x06 \x01(\tR\x08location\x12,\n\x12staked_by_operator\x18\x07 \x01(\tR\x10stakedByOperator\x12.\n\x13staked_by_delegates\x18\x08 \x01(\tR\x11stakedByDelegates\x12!\n\x0cstaked_total\x18\t \x01(\tR\x0bstakedTotal\x12,\n\x12max_intended_stake\x18\n \x01(\tR\x10maxIntendedStake\x12#\n\rpending_stake\x18\x0b \x01(\tR\x0cpendingStake\x12.\n\nepoch_data\x18\x0c \x01(\x0b\x32\x0f.vega.EpochDataR\tepochData\x12(\n\x06status\x18\r \x01(\x0e\x32\x10.vega.NodeStatusR\x06status\x12\x32\n\x0b\x64\x65legations\x18\x0e \x03(\x0b\x32\x10.vega.DelegationR\x0b\x64\x65legations\x12\x34\n\x0creward_score\x18\x0f \x01(\x0b\x32\x11.vega.RewardScoreR\x0brewardScore\x12\x37\n\rranking_score\x18\x10 \x01(\x0b\x32\x12.vega.RankingScoreR\x0crankingScore\x12\x12\n\x04name\x18\x11 \x01(\tR\x04name\x12\x1d\n\navatar_url\x18\x12 \x01(\tR\tavatarUrl"\x9c\x01\n\x07NodeSet\x12\x14\n\x05total\x18\x01 \x01(\rR\x05total\x12\x1a\n\x08inactive\x18\x02 \x01(\rR\x08inactive\x12\x1a\n\x08promoted\x18\x03 \x03(\tR\x08promoted\x12\x18\n\x07\x64\x65moted\x18\x04 \x03(\tR\x07\x64\x65moted\x12\x1d\n\x07maximum\x18\x05 \x01(\rH\x00R\x07maximum\x88\x01\x01\x42\n\n\x08_maximum"\xad\x02\n\x08NodeData\x12!\n\x0cstaked_total\x18\x01 \x01(\tR\x0bstakedTotal\x12\x1f\n\x0btotal_nodes\x18\x02 \x01(\rR\ntotalNodes\x12%\n\x0einactive_nodes\x18\x03 \x01(\rR\rinactiveNodes\x12\x38\n\x10tendermint_nodes\x18\x04 \x01(\x0b\x32\r.vega.NodeSetR\x0ftendermintNodes\x12\x30\n\x0c\x65rsatz_nodes\x18\x05 \x01(\x0b\x32\r.vega.NodeSetR\x0b\x65rsatzNodes\x12\x32\n\rpending_nodes\x18\x06 \x01(\x0b\x32\r.vega.NodeSetR\x0cpendingNodes\x12\x16\n\x06uptime\x18\x07 \x01(\x02R\x06uptime"p\n\nDelegation\x12\x14\n\x05party\x18\x01 \x01(\tR\x05party\x12\x17\n\x07node_id\x18\x02 \x01(\tR\x06nodeId\x12\x16\n\x06\x61mount\x18\x03 \x01(\tR\x06\x61mount\x12\x1b\n\tepoch_seq\x18\x04 \x01(\tR\x08\x65pochSeq"\xfb\x01\n\x06Reward\x12\x19\n\x08\x61sset_id\x18\x01 \x01(\tR\x07\x61ssetId\x12\x19\n\x08party_id\x18\x02 \x01(\tR\x07partyId\x12\x14\n\x05\x65poch\x18\x03 \x01(\x04R\x05\x65poch\x12\x16\n\x06\x61mount\x18\x04 \x01(\tR\x06\x61mount\x12.\n\x13percentage_of_total\x18\x05 \x01(\tR\x11percentageOfTotal\x12\x1f\n\x0breceived_at\x18\x06 \x01(\x03R\nreceivedAt\x12\x1b\n\tmarket_id\x18\x07 \x01(\tR\x08marketId\x12\x1f\n\x0breward_type\x18\x08 \x01(\tR\nrewardType"]\n\rRewardSummary\x12\x19\n\x08\x61sset_id\x18\x01 \x01(\tR\x07\x61ssetId\x12\x19\n\x08party_id\x18\x02 \x01(\tR\x07partyId\x12\x16\n\x06\x61mount\x18\x03 \x01(\tR\x06\x61mount"\x9b\x01\n\x12\x45pochRewardSummary\x12\x14\n\x05\x65poch\x18\x01 \x01(\x04R\x05\x65poch\x12\x19\n\x08\x61sset_id\x18\x02 \x01(\tR\x07\x61ssetId\x12\x1b\n\tmarket_id\x18\x03 \x01(\tR\x08marketId\x12\x1f\n\x0breward_type\x18\x04 \x01(\tR\nrewardType\x12\x16\n\x06\x61mount\x18\x05 \x01(\tR\x06\x61mount"y\n\x12StateValueProposal\x12 \n\x0cstate_var_id\x18\x01 \x01(\tR\nstateVarId\x12\x19\n\x08\x65vent_id\x18\x02 \x01(\tR\x07\x65ventId\x12&\n\x03kvb\x18\x03 \x03(\x0b\x32\x14.vega.KeyValueBundleR\x03kvb"k\n\x0eKeyValueBundle\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12\x1c\n\ttolerance\x18\x02 \x01(\tR\ttolerance\x12)\n\x05value\x18\x03 \x01(\x0b\x32\x13.vega.StateVarValueR\x05value"\xb4\x01\n\rStateVarValue\x12\x32\n\nscalar_val\x18\x01 \x01(\x0b\x32\x11.vega.ScalarValueH\x00R\tscalarVal\x12\x32\n\nvector_val\x18\x02 \x01(\x0b\x32\x11.vega.VectorValueH\x00R\tvectorVal\x12\x32\n\nmatrix_val\x18\x03 \x01(\x0b\x32\x11.vega.MatrixValueH\x00R\tmatrixValB\x07\n\x05value"#\n\x0bScalarValue\x12\x14\n\x05value\x18\x01 \x01(\tR\x05value"#\n\x0bVectorValue\x12\x14\n\x05value\x18\x01 \x03(\tR\x05value"6\n\x0bMatrixValue\x12\'\n\x05value\x18\x01 \x03(\x0b\x32\x11.vega.VectorValueR\x05value*9\n\x04Side\x12\x14\n\x10SIDE_UNSPECIFIED\x10\x00\x12\x0c\n\x08SIDE_BUY\x10\x01\x12\r\n\tSIDE_SELL\x10\x02*\xb5\x01\n\x08Interval\x12\x18\n\x14INTERVAL_UNSPECIFIED\x10\x00\x12\x1b\n\x0eINTERVAL_BLOCK\x10\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\x12\x10\n\x0cINTERVAL_I1M\x10<\x12\x11\n\x0cINTERVAL_I5M\x10\xac\x02\x12\x12\n\rINTERVAL_I15M\x10\x84\x07\x12\x11\n\x0cINTERVAL_I1H\x10\x90\x1c\x12\x12\n\x0cINTERVAL_I6H\x10\xe0\xa8\x01\x12\x12\n\x0cINTERVAL_I1D\x10\x80\xa3\x05*\x94\x01\n\x0ePositionStatus\x12\x1f\n\x1bPOSITION_STATUS_UNSPECIFIED\x10\x00\x12!\n\x1dPOSITION_STATUS_ORDERS_CLOSED\x10\x01\x12\x1e\n\x1aPOSITION_STATUS_CLOSED_OUT\x10\x02\x12\x1e\n\x1aPOSITION_STATUS_DISTRESSED\x10\x04*\x81\x02\n\x0e\x41uctionTrigger\x12\x1f\n\x1b\x41UCTION_TRIGGER_UNSPECIFIED\x10\x00\x12\x19\n\x15\x41UCTION_TRIGGER_BATCH\x10\x01\x12\x1b\n\x17\x41UCTION_TRIGGER_OPENING\x10\x02\x12\x19\n\x15\x41UCTION_TRIGGER_PRICE\x10\x03\x12\x1d\n\x19\x41UCTION_TRIGGER_LIQUIDITY\x10\x04\x12,\n(AUCTION_TRIGGER_LIQUIDITY_TARGET_NOT_MET\x10\x05\x12.\n*AUCTION_TRIGGER_UNABLE_TO_DEPLOY_LP_ORDERS\x10\x06*\x8b\x01\n\x0fPeggedReference\x12 \n\x1cPEGGED_REFERENCE_UNSPECIFIED\x10\x00\x12\x18\n\x14PEGGED_REFERENCE_MID\x10\x01\x12\x1d\n\x19PEGGED_REFERENCE_BEST_BID\x10\x02\x12\x1d\n\x19PEGGED_REFERENCE_BEST_ASK\x10\x03*\xc9\x10\n\nOrderError\x12\x1b\n\x17ORDER_ERROR_UNSPECIFIED\x10\x00\x12!\n\x1dORDER_ERROR_INVALID_MARKET_ID\x10\x01\x12 \n\x1cORDER_ERROR_INVALID_ORDER_ID\x10\x02\x12\x1f\n\x1bORDER_ERROR_OUT_OF_SEQUENCE\x10\x03\x12&\n"ORDER_ERROR_INVALID_REMAINING_SIZE\x10\x04\x12\x1c\n\x18ORDER_ERROR_TIME_FAILURE\x10\x05\x12\x1f\n\x1bORDER_ERROR_REMOVAL_FAILURE\x10\x06\x12+\n\'ORDER_ERROR_INVALID_EXPIRATION_DATETIME\x10\x07\x12\'\n#ORDER_ERROR_INVALID_ORDER_REFERENCE\x10\x08\x12 \n\x1cORDER_ERROR_EDIT_NOT_ALLOWED\x10\t\x12\x1d\n\x19ORDER_ERROR_AMEND_FAILURE\x10\n\x12\x19\n\x15ORDER_ERROR_NOT_FOUND\x10\x0b\x12 \n\x1cORDER_ERROR_INVALID_PARTY_ID\x10\x0c\x12\x1d\n\x19ORDER_ERROR_MARKET_CLOSED\x10\r\x12#\n\x1fORDER_ERROR_MARGIN_CHECK_FAILED\x10\x0e\x12\'\n#ORDER_ERROR_MISSING_GENERAL_ACCOUNT\x10\x0f\x12\x1e\n\x1aORDER_ERROR_INTERNAL_ERROR\x10\x10\x12\x1c\n\x18ORDER_ERROR_INVALID_SIZE\x10\x11\x12#\n\x1fORDER_ERROR_INVALID_PERSISTENCE\x10\x12\x12\x1c\n\x18ORDER_ERROR_INVALID_TYPE\x10\x13\x12\x1c\n\x18ORDER_ERROR_SELF_TRADING\x10\x14\x12.\n*ORDER_ERROR_INSUFFICIENT_FUNDS_TO_PAY_FEES\x10\x15\x12%\n!ORDER_ERROR_INCORRECT_MARKET_TYPE\x10\x16\x12%\n!ORDER_ERROR_INVALID_TIME_IN_FORCE\x10\x17\x12\x37\n3ORDER_ERROR_CANNOT_SEND_GFN_ORDER_DURING_AN_AUCTION\x10\x18\x12?\n;ORDER_ERROR_CANNOT_SEND_GFA_ORDER_DURING_CONTINUOUS_TRADING\x10\x19\x12\x34\n0ORDER_ERROR_CANNOT_AMEND_TO_GTT_WITHOUT_EXPIRYAT\x10\x1a\x12)\n%ORDER_ERROR_EXPIRYAT_BEFORE_CREATEDAT\x10\x1b\x12,\n(ORDER_ERROR_CANNOT_HAVE_GTC_AND_EXPIRYAT\x10\x1c\x12*\n&ORDER_ERROR_CANNOT_AMEND_TO_FOK_OR_IOC\x10\x1d\x12*\n&ORDER_ERROR_CANNOT_AMEND_TO_GFA_OR_GFN\x10\x1e\x12,\n(ORDER_ERROR_CANNOT_AMEND_FROM_GFA_OR_GFN\x10\x1f\x12\x34\n0ORDER_ERROR_CANNOT_SEND_IOC_ORDER_DURING_AUCTION\x10 \x12\x34\n0ORDER_ERROR_CANNOT_SEND_FOK_ORDER_DURING_AUCTION\x10!\x12#\n\x1fORDER_ERROR_MUST_BE_LIMIT_ORDER\x10"\x12"\n\x1eORDER_ERROR_MUST_BE_GTT_OR_GTC\x10#\x12\'\n#ORDER_ERROR_WITHOUT_REFERENCE_PRICE\x10$\x12\x33\n/ORDER_ERROR_BUY_CANNOT_REFERENCE_BEST_ASK_PRICE\x10%\x12\x37\n3ORDER_ERROR_OFFSET_MUST_BE_GREATER_OR_EQUAL_TO_ZERO\x10(\x12\x34\n0ORDER_ERROR_SELL_CANNOT_REFERENCE_BEST_BID_PRICE\x10)\x12\x30\n,ORDER_ERROR_OFFSET_MUST_BE_GREATER_THAN_ZERO\x10*\x12*\n&ORDER_ERROR_INSUFFICIENT_ASSET_BALANCE\x10+\x12\x45\nAORDER_ERROR_CANNOT_AMEND_PEGGED_ORDER_DETAILS_ON_NON_PEGGED_ORDER\x10,\x12.\n*ORDER_ERROR_UNABLE_TO_REPRICE_PEGGED_ORDER\x10-\x12\x35\n1ORDER_ERROR_UNABLE_TO_AMEND_PRICE_ON_PEGGED_ORDER\x10.\x12\x38\n4ORDER_ERROR_NON_PERSISTENT_ORDER_OUT_OF_PRICE_BOUNDS\x10/\x12&\n"ORDER_ERROR_TOO_MANY_PEGGED_ORDERS\x10\x30\x12+\n\'ORDER_ERROR_POST_ONLY_ORDER_WOULD_TRADE\x10\x31\x12;\n7ORDER_ERROR_REDUCE_ONLY_ORDER_WOULD_NOT_REDUCE_POSITION\x10\x32"\x04\x08&\x10&"\x04\x08\'\x10\'*\x82\x01\n\x0b\x43hainStatus\x12\x1c\n\x18\x43HAIN_STATUS_UNSPECIFIED\x10\x00\x12\x1d\n\x19\x43HAIN_STATUS_DISCONNECTED\x10\x01\x12\x1a\n\x16\x43HAIN_STATUS_REPLAYING\x10\x02\x12\x1a\n\x16\x43HAIN_STATUS_CONNECTED\x10\x03*\xc4\x04\n\x0b\x41\x63\x63ountType\x12\x1c\n\x18\x41\x43\x43OUNT_TYPE_UNSPECIFIED\x10\x00\x12\x1a\n\x16\x41\x43\x43OUNT_TYPE_INSURANCE\x10\x01\x12\x1b\n\x17\x41\x43\x43OUNT_TYPE_SETTLEMENT\x10\x02\x12\x17\n\x13\x41\x43\x43OUNT_TYPE_MARGIN\x10\x03\x12\x18\n\x14\x41\x43\x43OUNT_TYPE_GENERAL\x10\x04\x12$\n ACCOUNT_TYPE_FEES_INFRASTRUCTURE\x10\x05\x12\x1f\n\x1b\x41\x43\x43OUNT_TYPE_FEES_LIQUIDITY\x10\x06\x12\x1b\n\x17\x41\x43\x43OUNT_TYPE_FEES_MAKER\x10\x07\x12\x15\n\x11\x41\x43\x43OUNT_TYPE_BOND\x10\t\x12\x19\n\x15\x41\x43\x43OUNT_TYPE_EXTERNAL\x10\n\x12!\n\x1d\x41\x43\x43OUNT_TYPE_GLOBAL_INSURANCE\x10\x0b\x12\x1e\n\x1a\x41\x43\x43OUNT_TYPE_GLOBAL_REWARD\x10\x0c\x12"\n\x1e\x41\x43\x43OUNT_TYPE_PENDING_TRANSFERS\x10\r\x12\'\n#ACCOUNT_TYPE_REWARD_MAKER_PAID_FEES\x10\x0e\x12+\n\'ACCOUNT_TYPE_REWARD_MAKER_RECEIVED_FEES\x10\x0f\x12(\n$ACCOUNT_TYPE_REWARD_LP_RECEIVED_FEES\x10\x10\x12(\n$ACCOUNT_TYPE_REWARD_MARKET_PROPOSERS\x10\x11"\x04\x08\x08\x10\x08*\xc9\x06\n\x0cTransferType\x12\x1d\n\x19TRANSFER_TYPE_UNSPECIFIED\x10\x00\x12\x16\n\x12TRANSFER_TYPE_LOSS\x10\x01\x12\x15\n\x11TRANSFER_TYPE_WIN\x10\x02\x12\x1a\n\x16TRANSFER_TYPE_MTM_LOSS\x10\x04\x12\x19\n\x15TRANSFER_TYPE_MTM_WIN\x10\x05\x12\x1c\n\x18TRANSFER_TYPE_MARGIN_LOW\x10\x06\x12\x1d\n\x19TRANSFER_TYPE_MARGIN_HIGH\x10\x07\x12$\n TRANSFER_TYPE_MARGIN_CONFISCATED\x10\x08\x12\x1f\n\x1bTRANSFER_TYPE_MAKER_FEE_PAY\x10\t\x12#\n\x1fTRANSFER_TYPE_MAKER_FEE_RECEIVE\x10\n\x12(\n$TRANSFER_TYPE_INFRASTRUCTURE_FEE_PAY\x10\x0b\x12/\n+TRANSFER_TYPE_INFRASTRUCTURE_FEE_DISTRIBUTE\x10\x0c\x12#\n\x1fTRANSFER_TYPE_LIQUIDITY_FEE_PAY\x10\r\x12*\n&TRANSFER_TYPE_LIQUIDITY_FEE_DISTRIBUTE\x10\x0e\x12\x1a\n\x16TRANSFER_TYPE_BOND_LOW\x10\x0f\x12\x1b\n\x17TRANSFER_TYPE_BOND_HIGH\x10\x10\x12\x1a\n\x16TRANSFER_TYPE_WITHDRAW\x10\x12\x12\x19\n\x15TRANSFER_TYPE_DEPOSIT\x10\x13\x12\x1f\n\x1bTRANSFER_TYPE_BOND_SLASHING\x10\x14\x12\x1f\n\x1bTRANSFER_TYPE_REWARD_PAYOUT\x10\x15\x12%\n!TRANSFER_TYPE_TRANSFER_FUNDS_SEND\x10\x16\x12+\n\'TRANSFER_TYPE_TRANSFER_FUNDS_DISTRIBUTE\x10\x17\x12\x1f\n\x1bTRANSFER_TYPE_CLEAR_ACCOUNT\x10\x18\x12,\n(TRANSFER_TYPE_CHECKPOINT_BALANCE_RESTORE\x10\x19"\x04\x08\x03\x10\x03"\x04\x08\x11\x10\x11*\xc7\x01\n\x0e\x44ispatchMetric\x12\x1f\n\x1b\x44ISPATCH_METRIC_UNSPECIFIED\x10\x00\x12#\n\x1f\x44ISPATCH_METRIC_MAKER_FEES_PAID\x10\x01\x12\'\n#DISPATCH_METRIC_MAKER_FEES_RECEIVED\x10\x02\x12$\n DISPATCH_METRIC_LP_FEES_RECEIVED\x10\x03\x12 \n\x1c\x44ISPATCH_METRIC_MARKET_VALUE\x10\x04*c\n\nNodeStatus\x12\x1b\n\x17NODE_STATUS_UNSPECIFIED\x10\x00\x12\x19\n\x15NODE_STATUS_VALIDATOR\x10\x01\x12\x1d\n\x19NODE_STATUS_NON_VALIDATOR\x10\x02*Y\n\x0b\x45pochAction\x12\x1c\n\x18\x45POCH_ACTION_UNSPECIFIED\x10\x00\x12\x16\n\x12\x45POCH_ACTION_START\x10\x01\x12\x14\n\x10\x45POCH_ACTION_END\x10\x02*\xa7\x01\n\x13ValidatorNodeStatus\x12%\n!VALIDATOR_NODE_STATUS_UNSPECIFIED\x10\x00\x12$\n VALIDATOR_NODE_STATUS_TENDERMINT\x10\x01\x12 \n\x1cVALIDATOR_NODE_STATUS_ERSATZ\x10\x02\x12!\n\x1dVALIDATOR_NODE_STATUS_PENDING\x10\x03\x42\'Z%code.vegaprotocol.io/vega/protos/vegab\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "vega.vega_pb2", globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b"Z%code.vegaprotocol.io/vega/protos/vega"
    _SIDE._serialized_start = 13733
    _SIDE._serialized_end = 13790
    _INTERVAL._serialized_start = 13793
    _INTERVAL._serialized_end = 13974
    _POSITIONSTATUS._serialized_start = 13977
    _POSITIONSTATUS._serialized_end = 14125
    _AUCTIONTRIGGER._serialized_start = 14128
    _AUCTIONTRIGGER._serialized_end = 14385
    _PEGGEDREFERENCE._serialized_start = 14388
    _PEGGEDREFERENCE._serialized_end = 14527
    _ORDERERROR._serialized_start = 14530
    _ORDERERROR._serialized_end = 16651
    _CHAINSTATUS._serialized_start = 16654
    _CHAINSTATUS._serialized_end = 16784
    _ACCOUNTTYPE._serialized_start = 16787
    _ACCOUNTTYPE._serialized_end = 17367
    _TRANSFERTYPE._serialized_start = 17370
    _TRANSFERTYPE._serialized_end = 18211
    _DISPATCHMETRIC._serialized_start = 18214
    _DISPATCHMETRIC._serialized_end = 18413
    _NODESTATUS._serialized_start = 18415
    _NODESTATUS._serialized_end = 18514
    _EPOCHACTION._serialized_start = 18516
    _EPOCHACTION._serialized_end = 18605
    _VALIDATORNODESTATUS._serialized_start = 18608
    _VALIDATORNODESTATUS._serialized_end = 18775
    _PARTY._serialized_start = 45
    _PARTY._serialized_end = 68
    _RISKFACTOR._serialized_start = 70
    _RISKFACTOR._serialized_end = 148
    _PEGGEDORDER._serialized_start = 150
    _PEGGEDORDER._serialized_end = 240
    _ORDER._serialized_start = 243
    _ORDER._serialized_end = 1443
    _ORDER_TIMEINFORCE._serialized_start = 965
    _ORDER_TIMEINFORCE._serialized_end = 1147
    _ORDER_TYPE._serialized_start = 1149
    _ORDER_TYPE._serialized_end = 1228
    _ORDER_STATUS._serialized_start = 1231
    _ORDER_STATUS._serialized_end = 1432
    _ORDERCANCELLATIONCONFIRMATION._serialized_start = 1445
    _ORDERCANCELLATIONCONFIRMATION._serialized_end = 1511
    _ORDERCONFIRMATION._serialized_start = 1514
    _ORDERCONFIRMATION._serialized_end = 1674
    _AUCTIONINDICATIVESTATE._serialized_start = 1677
    _AUCTIONINDICATIVESTATE._serialized_end = 1888
    _TRADE._serialized_start = 1891
    _TRADE._serialized_end = 2494
    _TRADE_TYPE._serialized_start = 2383
    _TRADE_TYPE._serialized_end = 2494
    _FEE._serialized_start = 2496
    _FEE._serialized_end = 2614
    _TRADESET._serialized_start = 2616
    _TRADESET._serialized_end = 2663
    _CANDLE._serialized_start = 2666
    _CANDLE._serialized_end = 2880
    _PRICELEVEL._serialized_start = 2882
    _PRICELEVEL._serialized_end = 2982
    _MARKETDEPTH._serialized_start = 2985
    _MARKETDEPTH._serialized_end = 3142
    _MARKETDEPTHUPDATE._serialized_start = 3145
    _MARKETDEPTHUPDATE._serialized_end = 3366
    _POSITION._serialized_start = 3369
    _POSITION._serialized_end = 3744
    _POSITIONTRADE._serialized_start = 3746
    _POSITIONTRADE._serialized_end = 3807
    _DEPOSIT._serialized_start = 3810
    _DEPOSIT._serialized_end = 4166
    _DEPOSIT_STATUS._serialized_start = 4073
    _DEPOSIT_STATUS._serialized_end = 4166
    _WITHDRAWAL._serialized_start = 4169
    _WITHDRAWAL._serialized_end = 4593
    _WITHDRAWAL_STATUS._serialized_start = 4495
    _WITHDRAWAL_STATUS._serialized_end = 4587
    _WITHDRAWEXT._serialized_start = 4595
    _WITHDRAWEXT._serialized_end = 4663
    _ERC20WITHDRAWEXT._serialized_start = 4665
    _ERC20WITHDRAWEXT._serialized_end = 4726
    _ACCOUNT._serialized_start = 4729
    _ACCOUNT._serialized_end = 4892
    _FINANCIALAMOUNT._serialized_start = 4894
    _FINANCIALAMOUNT._serialized_end = 4957
    _TRANSFER._serialized_start = 4960
    _TRANSFER._serialized_end = 5139
    _DISPATCHSTRATEGY._serialized_start = 5142
    _DISPATCHSTRATEGY._serialized_end = 5274
    _TRANSFERREQUEST._serialized_start = 5277
    _TRANSFERREQUEST._serialized_end = 5507
    _ACCOUNTDETAILS._serialized_start = 5510
    _ACCOUNTDETAILS._serialized_end = 5677
    _LEDGERENTRY._serialized_start = 5680
    _LEDGERENTRY._serialized_end = 5993
    _POSTTRANSFERBALANCE._serialized_start = 5995
    _POSTTRANSFERBALANCE._serialized_end = 6090
    _LEDGERMOVEMENT._serialized_start = 6092
    _LEDGERMOVEMENT._serialized_end = 6208
    _MARGINLEVELS._serialized_start = 6211
    _MARGINLEVELS._serialized_end = 6512
    _MARKETDATA._serialized_start = 6515
    _MARKETDATA._serialized_end = 7896
    _LIQUIDITYPROVIDERFEESHARE._serialized_start = 7899
    _LIQUIDITYPROVIDERFEESHARE._serialized_end = 8085
    _PRICEMONITORINGBOUNDS._serialized_start = 8088
    _PRICEMONITORINGBOUNDS._serialized_end = 8288
    _ERRORDETAIL._serialized_start = 8290
    _ERRORDETAIL._serialized_end = 8371
    _NETWORKPARAMETER._serialized_start = 8373
    _NETWORKPARAMETER._serialized_end = 8431
    _NETWORKLIMITS._serialized_start = 8434
    _NETWORKLIMITS._serialized_end = 8820
    _LIQUIDITYORDER._serialized_start = 8822
    _LIQUIDITYORDER._serialized_end = 8947
    _LIQUIDITYORDERREFERENCE._serialized_start = 8949
    _LIQUIDITYORDERREFERENCE._serialized_end = 9064
    _LIQUIDITYPROVISION._serialized_start = 9067
    _LIQUIDITYPROVISION._serialized_end = 9661
    _LIQUIDITYPROVISION_STATUS._serialized_start = 9504
    _LIQUIDITYPROVISION_STATUS._serialized_end = 9661
    _ETHEREUMCONFIG._serialized_start = 9664
    _ETHEREUMCONFIG._serialized_end = 10128
    _ETHEREUMCONTRACTCONFIG._serialized_start = 10130
    _ETHEREUMCONTRACTCONFIG._serialized_end = 10236
    _EPOCHTIMESTAMPS._serialized_start = 10239
    _EPOCHTIMESTAMPS._serialized_end = 10411
    _EPOCH._serialized_start = 10414
    _EPOCH._serialized_end = 10590
    _EPOCHPARTICIPATION._serialized_start = 10593
    _EPOCHPARTICIPATION._serialized_end = 10735
    _EPOCHDATA._serialized_start = 10737
    _EPOCHDATA._serialized_end = 10820
    _RANKINGSCORE._serialized_start = 10823
    _RANKINGSCORE._serialized_end = 11106
    _REWARDSCORE._serialized_start = 11109
    _REWARDSCORE._serialized_end = 11408
    _NODE._serialized_start = 11411
    _NODE._serialized_end = 12102
    _NODESET._serialized_start = 12105
    _NODESET._serialized_end = 12261
    _NODEDATA._serialized_start = 12264
    _NODEDATA._serialized_end = 12565
    _DELEGATION._serialized_start = 12567
    _DELEGATION._serialized_end = 12679
    _REWARD._serialized_start = 12682
    _REWARD._serialized_end = 12933
    _REWARDSUMMARY._serialized_start = 12935
    _REWARDSUMMARY._serialized_end = 13028
    _EPOCHREWARDSUMMARY._serialized_start = 13031
    _EPOCHREWARDSUMMARY._serialized_end = 13186
    _STATEVALUEPROPOSAL._serialized_start = 13188
    _STATEVALUEPROPOSAL._serialized_end = 13309
    _KEYVALUEBUNDLE._serialized_start = 13311
    _KEYVALUEBUNDLE._serialized_end = 13418
    _STATEVARVALUE._serialized_start = 13421
    _STATEVARVALUE._serialized_end = 13601
    _SCALARVALUE._serialized_start = 13603
    _SCALARVALUE._serialized_end = 13638
    _VECTORVALUE._serialized_start = 13640
    _VECTORVALUE._serialized_end = 13675
    _MATRIXVALUE._serialized_start = 13677
    _MATRIXVALUE._serialized_end = 13731
# @@protoc_insertion_point(module_scope)
