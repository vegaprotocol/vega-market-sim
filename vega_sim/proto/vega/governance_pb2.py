# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vega/governance.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import assets_pb2 as vega_dot_assets__pb2
from . import data_source_pb2 as vega_dot_data__source__pb2
from . import markets_pb2 as vega_dot_markets__pb2
from . import vega_pb2 as vega_dot_vega__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x15vega/governance.proto\x12\x04vega\x1a\x11vega/assets.proto\x1a\x16vega/data_source.proto\x1a\x12vega/markets.proto\x1a\x0fvega/vega.proto"a\n\x0bSpotProduct\x12\x1d\n\nbase_asset\x18\x01 \x01(\tR\tbaseAsset\x12\x1f\n\x0bquote_asset\x18\x02 \x01(\tR\nquoteAsset\x12\x12\n\x04name\x18\x03 \x01(\tR\x04name"\x95\x03\n\rFutureProduct\x12)\n\x10settlement_asset\x18\x01 \x01(\tR\x0fsettlementAsset\x12\x1d\n\nquote_name\x18\x02 \x01(\tR\tquoteName\x12i\n$data_source_spec_for_settlement_data\x18\x03 \x01(\x0b\x32\x1a.vega.DataSourceDefinitionR\x1f\x64\x61taSourceSpecForSettlementData\x12q\n(data_source_spec_for_trading_termination\x18\x04 \x01(\x0b\x32\x1a.vega.DataSourceDefinitionR#dataSourceSpecForTradingTermination\x12\\\n\x18\x64\x61ta_source_spec_binding\x18\x05 \x01(\x0b\x32#.vega.DataSourceSpecToFutureBindingR\x15\x64\x61taSourceSpecBinding"\xcc\x04\n\x10PerpetualProduct\x12)\n\x10settlement_asset\x18\x01 \x01(\tR\x0fsettlementAsset\x12\x1d\n\nquote_name\x18\x02 \x01(\tR\tquoteName\x12\x32\n\x15margin_funding_factor\x18\x03 \x01(\tR\x13marginFundingFactor\x12#\n\rinterest_rate\x18\x04 \x01(\tR\x0cinterestRate\x12*\n\x11\x63lamp_lower_bound\x18\x05 \x01(\tR\x0f\x63lampLowerBound\x12*\n\x11\x63lamp_upper_bound\x18\x06 \x01(\tR\x0f\x63lampUpperBound\x12q\n(data_source_spec_for_settlement_schedule\x18\x07 \x01(\x0b\x32\x1a.vega.DataSourceDefinitionR#dataSourceSpecForSettlementSchedule\x12i\n$data_source_spec_for_settlement_data\x18\x08 \x01(\x0b\x32\x1a.vega.DataSourceDefinitionR\x1f\x64\x61taSourceSpecForSettlementData\x12_\n\x18\x64\x61ta_source_spec_binding\x18\t \x01(\x0b\x32&.vega.DataSourceSpecToPerpetualBindingR\x15\x64\x61taSourceSpecBinding"\xdc\x01\n\x17InstrumentConfiguration\x12\x12\n\x04name\x18\x01 \x01(\tR\x04name\x12\x12\n\x04\x63ode\x18\x02 \x01(\tR\x04\x63ode\x12-\n\x06\x66uture\x18\x64 \x01(\x0b\x32\x13.vega.FutureProductH\x00R\x06\x66uture\x12\'\n\x04spot\x18\x65 \x01(\x0b\x32\x11.vega.SpotProductH\x00R\x04spot\x12\x36\n\tperpetual\x18\x66 \x01(\x0b\x32\x16.vega.PerpetualProductH\x00R\tperpetualB\t\n\x07product"\xca\x04\n\x1aNewSpotMarketConfiguration\x12=\n\ninstrument\x18\x01 \x01(\x0b\x32\x1d.vega.InstrumentConfigurationR\ninstrument\x12%\n\x0e\x64\x65\x63imal_places\x18\x02 \x01(\x04R\rdecimalPlaces\x12\x1a\n\x08metadata\x18\x03 \x03(\tR\x08metadata\x12_\n\x1bprice_monitoring_parameters\x18\x04 \x01(\x0b\x32\x1f.vega.PriceMonitoringParametersR\x19priceMonitoringParameters\x12S\n\x17target_stake_parameters\x18\x05 \x01(\x0b\x32\x1b.vega.TargetStakeParametersR\x15targetStakeParameters\x12\x31\n\x06simple\x18\x64 \x01(\x0b\x32\x17.vega.SimpleModelParamsH\x00R\x06simple\x12\x39\n\nlog_normal\x18\x65 \x01(\x0b\x32\x18.vega.LogNormalRiskModelH\x00R\tlogNormal\x12\x36\n\x17position_decimal_places\x18\x06 \x01(\x03R\x15positionDecimalPlaces\x12;\n\nsla_params\x18\x07 \x01(\x0b\x32\x1c.vega.LiquiditySLAParametersR\tslaParamsB\x11\n\x0frisk_parameters"\xf8\x06\n\x16NewMarketConfiguration\x12=\n\ninstrument\x18\x01 \x01(\x0b\x32\x1d.vega.InstrumentConfigurationR\ninstrument\x12%\n\x0e\x64\x65\x63imal_places\x18\x02 \x01(\x04R\rdecimalPlaces\x12\x1a\n\x08metadata\x18\x03 \x03(\tR\x08metadata\x12_\n\x1bprice_monitoring_parameters\x18\x04 \x01(\x0b\x32\x1f.vega.PriceMonitoringParametersR\x19priceMonitoringParameters\x12k\n\x1fliquidity_monitoring_parameters\x18\x05 \x01(\x0b\x32#.vega.LiquidityMonitoringParametersR\x1dliquidityMonitoringParameters\x12\x31\n\x06simple\x18\x64 \x01(\x0b\x32\x17.vega.SimpleModelParamsH\x00R\x06simple\x12\x39\n\nlog_normal\x18\x65 \x01(\x0b\x32\x18.vega.LogNormalRiskModelH\x00R\tlogNormal\x12\x36\n\x17position_decimal_places\x18\x06 \x01(\x03R\x15positionDecimalPlaces\x12)\n\x0elp_price_range\x18\x08 \x01(\tH\x01R\x0clpPriceRange\x88\x01\x01\x12\x34\n\x16linear_slippage_factor\x18\t \x01(\tR\x14linearSlippageFactor\x12:\n\x19quadratic_slippage_factor\x18\n \x01(\tR\x17quadraticSlippageFactor\x12?\n\tsuccessor\x18\x0b \x01(\x0b\x32\x1c.vega.SuccessorConfigurationH\x02R\tsuccessor\x88\x01\x01\x12V\n\x18liquidity_sla_parameters\x18\x0c \x01(\x0b\x32\x1c.vega.LiquiditySLAParametersR\x16liquiditySlaParametersB\x11\n\x0frisk_parametersB\x11\n\x0f_lp_price_rangeB\x0c\n\n_successor"K\n\rNewSpotMarket\x12:\n\x07\x63hanges\x18\x01 \x01(\x0b\x32 .vega.NewSpotMarketConfigurationR\x07\x63hanges"z\n\x16SuccessorConfiguration\x12(\n\x10parent_market_id\x18\x01 \x01(\tR\x0eparentMarketId\x12\x36\n\x17insurance_pool_fraction\x18\x02 \x01(\tR\x15insurancePoolFraction"C\n\tNewMarket\x12\x36\n\x07\x63hanges\x18\x01 \x01(\x0b\x32\x1c.vega.NewMarketConfigurationR\x07\x63hanges"f\n\x0cUpdateMarket\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12\x39\n\x07\x63hanges\x18\x02 \x01(\x0b\x32\x1f.vega.UpdateMarketConfigurationR\x07\x63hanges"n\n\x10UpdateSpotMarket\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12=\n\x07\x63hanges\x18\x02 \x01(\x0b\x32#.vega.UpdateSpotMarketConfigurationR\x07\x63hanges"\xd3\x05\n\x19UpdateMarketConfiguration\x12\x43\n\ninstrument\x18\x01 \x01(\x0b\x32#.vega.UpdateInstrumentConfigurationR\ninstrument\x12\x1a\n\x08metadata\x18\x02 \x03(\tR\x08metadata\x12_\n\x1bprice_monitoring_parameters\x18\x03 \x01(\x0b\x32\x1f.vega.PriceMonitoringParametersR\x19priceMonitoringParameters\x12k\n\x1fliquidity_monitoring_parameters\x18\x04 \x01(\x0b\x32#.vega.LiquidityMonitoringParametersR\x1dliquidityMonitoringParameters\x12\x31\n\x06simple\x18\x64 \x01(\x0b\x32\x17.vega.SimpleModelParamsH\x00R\x06simple\x12\x39\n\nlog_normal\x18\x65 \x01(\x0b\x32\x18.vega.LogNormalRiskModelH\x00R\tlogNormal\x12)\n\x0elp_price_range\x18\x05 \x01(\tH\x01R\x0clpPriceRange\x88\x01\x01\x12\x34\n\x16linear_slippage_factor\x18\x06 \x01(\tR\x14linearSlippageFactor\x12:\n\x19quadratic_slippage_factor\x18\x07 \x01(\tR\x17quadraticSlippageFactor\x12V\n\x18liquidity_sla_parameters\x18\x08 \x01(\x0b\x32\x1c.vega.LiquiditySLAParametersR\x16liquiditySlaParametersB\x11\n\x0frisk_parametersB\x11\n\x0f_lp_price_range"\xaf\x03\n\x1dUpdateSpotMarketConfiguration\x12\x1a\n\x08metadata\x18\x01 \x03(\tR\x08metadata\x12_\n\x1bprice_monitoring_parameters\x18\x02 \x01(\x0b\x32\x1f.vega.PriceMonitoringParametersR\x19priceMonitoringParameters\x12S\n\x17target_stake_parameters\x18\x03 \x01(\x0b\x32\x1b.vega.TargetStakeParametersR\x15targetStakeParameters\x12\x31\n\x06simple\x18\x64 \x01(\x0b\x32\x17.vega.SimpleModelParamsH\x00R\x06simple\x12\x39\n\nlog_normal\x18\x65 \x01(\x0b\x32\x18.vega.LogNormalRiskModelH\x00R\tlogNormal\x12;\n\nsla_params\x18\x04 \x01(\x0b\x32\x1c.vega.LiquiditySLAParametersR\tslaParamsB\x11\n\x0frisk_parameters"\xb1\x01\n\x1dUpdateInstrumentConfiguration\x12\x12\n\x04\x63ode\x18\x01 \x01(\tR\x04\x63ode\x12\x33\n\x06\x66uture\x18\x64 \x01(\x0b\x32\x19.vega.UpdateFutureProductH\x00R\x06\x66uture\x12<\n\tperpetual\x18\x65 \x01(\x0b\x32\x1c.vega.UpdatePerpetualProductH\x00R\tperpetualB\t\n\x07product"\xf0\x02\n\x13UpdateFutureProduct\x12\x1d\n\nquote_name\x18\x01 \x01(\tR\tquoteName\x12i\n$data_source_spec_for_settlement_data\x18\x02 \x01(\x0b\x32\x1a.vega.DataSourceDefinitionR\x1f\x64\x61taSourceSpecForSettlementData\x12q\n(data_source_spec_for_trading_termination\x18\x03 \x01(\x0b\x32\x1a.vega.DataSourceDefinitionR#dataSourceSpecForTradingTermination\x12\\\n\x18\x64\x61ta_source_spec_binding\x18\x04 \x01(\x0b\x32#.vega.DataSourceSpecToFutureBindingR\x15\x64\x61taSourceSpecBinding"\xa7\x04\n\x16UpdatePerpetualProduct\x12\x1d\n\nquote_name\x18\x01 \x01(\tR\tquoteName\x12\x32\n\x15margin_funding_factor\x18\x02 \x01(\tR\x13marginFundingFactor\x12#\n\rinterest_rate\x18\x03 \x01(\tR\x0cinterestRate\x12*\n\x11\x63lamp_lower_bound\x18\x04 \x01(\tR\x0f\x63lampLowerBound\x12*\n\x11\x63lamp_upper_bound\x18\x05 \x01(\tR\x0f\x63lampUpperBound\x12q\n(data_source_spec_for_settlement_schedule\x18\x06 \x01(\x0b\x32\x1a.vega.DataSourceDefinitionR#dataSourceSpecForSettlementSchedule\x12i\n$data_source_spec_for_settlement_data\x18\x07 \x01(\x0b\x32\x1a.vega.DataSourceDefinitionR\x1f\x64\x61taSourceSpecForSettlementData\x12_\n\x18\x64\x61ta_source_spec_binding\x18\x08 \x01(\x0b\x32&.vega.DataSourceSpecToPerpetualBindingR\x15\x64\x61taSourceSpecBinding"J\n\x16UpdateNetworkParameter\x12\x30\n\x07\x63hanges\x18\x01 \x01(\x0b\x32\x16.vega.NetworkParameterR\x07\x63hanges"8\n\x08NewAsset\x12,\n\x07\x63hanges\x18\x01 \x01(\x0b\x32\x12.vega.AssetDetailsR\x07\x63hanges"\\\n\x0bUpdateAsset\x12\x19\n\x08\x61sset_id\x18\x01 \x01(\tR\x07\x61ssetId\x12\x32\n\x07\x63hanges\x18\x02 \x01(\x0b\x32\x18.vega.AssetDetailsUpdateR\x07\x63hanges"\r\n\x0bNewFreeform"\x9c\x08\n\rProposalTerms\x12+\n\x11\x63losing_timestamp\x18\x01 \x01(\x03R\x10\x63losingTimestamp\x12/\n\x13\x65nactment_timestamp\x18\x02 \x01(\x03R\x12\x65nactmentTimestamp\x12\x31\n\x14validation_timestamp\x18\x03 \x01(\x03R\x13validationTimestamp\x12\x39\n\rupdate_market\x18\x65 \x01(\x0b\x32\x12.vega.UpdateMarketH\x00R\x0cupdateMarket\x12\x30\n\nnew_market\x18\x66 \x01(\x0b\x32\x0f.vega.NewMarketH\x00R\tnewMarket\x12X\n\x18update_network_parameter\x18g \x01(\x0b\x32\x1c.vega.UpdateNetworkParameterH\x00R\x16updateNetworkParameter\x12-\n\tnew_asset\x18h \x01(\x0b\x32\x0e.vega.NewAssetH\x00R\x08newAsset\x12\x36\n\x0cnew_freeform\x18i \x01(\x0b\x32\x11.vega.NewFreeformH\x00R\x0bnewFreeform\x12\x36\n\x0cupdate_asset\x18j \x01(\x0b\x32\x11.vega.UpdateAssetH\x00R\x0bupdateAsset\x12=\n\x0fnew_spot_market\x18k \x01(\x0b\x32\x13.vega.NewSpotMarketH\x00R\rnewSpotMarket\x12\x46\n\x12update_spot_market\x18l \x01(\x0b\x32\x16.vega.UpdateSpotMarketH\x00R\x10updateSpotMarket\x12\x36\n\x0cnew_transfer\x18m \x01(\x0b\x32\x11.vega.NewTransferH\x00R\x0bnewTransfer\x12?\n\x0f\x63\x61ncel_transfer\x18n \x01(\x0b\x32\x14.vega.CancelTransferH\x00R\x0e\x63\x61ncelTransfer\x12I\n\x13update_market_state\x18o \x01(\x0b\x32\x17.vega.UpdateMarketStateH\x00R\x11updateMarketState\x12U\n\x17update_referral_program\x18p \x01(\x0b\x32\x1b.vega.UpdateReferralProgramH\x00R\x15updateReferralProgram\x12h\n\x1eupdate_volume_discount_program\x18q \x01(\x0b\x32!.vega.UpdateVolumeDiscountProgramH\x00R\x1bupdateVolumeDiscountProgramB\x08\n\x06\x63hange"W\n\x11ProposalRationale\x12 \n\x0b\x64\x65scription\x18\x01 \x01(\tR\x0b\x64\x65scription\x12\x14\n\x05title\x18\x04 \x01(\tR\x05titleJ\x04\x08\x02\x10\x03J\x04\x08\x03\x10\x04"\x86\x03\n\x0eGovernanceData\x12*\n\x08proposal\x18\x01 \x01(\x0b\x32\x0e.vega.ProposalR\x08proposal\x12\x1c\n\x03yes\x18\x02 \x03(\x0b\x32\n.vega.VoteR\x03yes\x12\x1a\n\x02no\x18\x03 \x03(\x0b\x32\n.vega.VoteR\x02no\x12?\n\tyes_party\x18\x04 \x03(\x0b\x32".vega.GovernanceData.YesPartyEntryR\x08yesParty\x12<\n\x08no_party\x18\x05 \x03(\x0b\x32!.vega.GovernanceData.NoPartyEntryR\x07noParty\x1aG\n\rYesPartyEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12 \n\x05value\x18\x02 \x01(\x0b\x32\n.vega.VoteR\x05value:\x02\x38\x01\x1a\x46\n\x0cNoPartyEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12 \n\x05value\x18\x02 \x01(\x0b\x32\n.vega.VoteR\x05value:\x02\x38\x01"\x9a\x07\n\x08Proposal\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\x12\x1c\n\treference\x18\x02 \x01(\tR\treference\x12\x19\n\x08party_id\x18\x03 \x01(\tR\x07partyId\x12*\n\x05state\x18\x04 \x01(\x0e\x32\x14.vega.Proposal.StateR\x05state\x12\x1c\n\ttimestamp\x18\x05 \x01(\x03R\ttimestamp\x12)\n\x05terms\x18\x06 \x01(\x0b\x32\x13.vega.ProposalTermsR\x05terms\x12\x30\n\x06reason\x18\x07 \x01(\x0e\x32\x13.vega.ProposalErrorH\x00R\x06reason\x88\x01\x01\x12(\n\rerror_details\x18\x08 \x01(\tH\x01R\x0c\x65rrorDetails\x88\x01\x01\x12\x35\n\trationale\x18\t \x01(\x0b\x32\x17.vega.ProposalRationaleR\trationale\x12\x35\n\x16required_participation\x18\n \x01(\tR\x15requiredParticipation\x12+\n\x11required_majority\x18\x0b \x01(\tR\x10requiredMajority\x12^\n)required_liquidity_provider_participation\x18\x0c \x01(\tH\x02R&requiredLiquidityProviderParticipation\x88\x01\x01\x12T\n$required_liquidity_provider_majority\x18\r \x01(\tH\x03R!requiredLiquidityProviderMajority\x88\x01\x01"\xae\x01\n\x05State\x12\x15\n\x11STATE_UNSPECIFIED\x10\x00\x12\x10\n\x0cSTATE_FAILED\x10\x01\x12\x0e\n\nSTATE_OPEN\x10\x02\x12\x10\n\x0cSTATE_PASSED\x10\x03\x12\x12\n\x0eSTATE_REJECTED\x10\x04\x12\x12\n\x0eSTATE_DECLINED\x10\x05\x12\x11\n\rSTATE_ENACTED\x10\x06\x12\x1f\n\x1bSTATE_WAITING_FOR_NODE_VOTE\x10\x07\x42\t\n\x07_reasonB\x10\n\x0e_error_detailsB,\n*_required_liquidity_provider_participationB\'\n%_required_liquidity_provider_majority"\x91\x03\n\x04Vote\x12\x19\n\x08party_id\x18\x01 \x01(\tR\x07partyId\x12&\n\x05value\x18\x02 \x01(\x0e\x32\x10.vega.Vote.ValueR\x05value\x12\x1f\n\x0bproposal_id\x18\x03 \x01(\tR\nproposalId\x12\x1c\n\ttimestamp\x18\x04 \x01(\x03R\ttimestamp\x12\x43\n\x1etotal_governance_token_balance\x18\x05 \x01(\tR\x1btotalGovernanceTokenBalance\x12\x41\n\x1dtotal_governance_token_weight\x18\x06 \x01(\tR\x1atotalGovernanceTokenWeight\x12\x42\n\x1etotal_equity_like_share_weight\x18\x07 \x01(\tR\x1atotalEquityLikeShareWeight";\n\x05Value\x12\x15\n\x11VALUE_UNSPECIFIED\x10\x00\x12\x0c\n\x08VALUE_NO\x10\x01\x12\r\n\tVALUE_YES\x10\x02"T\n\x1bUpdateVolumeDiscountProgram\x12\x35\n\x07\x63hanges\x18\x01 \x01(\x0b\x32\x1b.vega.VolumeDiscountProgramR\x07\x63hanges"H\n\x15UpdateReferralProgram\x12/\n\x07\x63hanges\x18\x01 \x01(\x0b\x32\x15.vega.ReferralProgramR\x07\x63hanges"S\n\x11UpdateMarketState\x12>\n\x07\x63hanges\x18\x01 \x01(\x0b\x32$.vega.UpdateMarketStateConfigurationR\x07\x63hanges"\xa0\x01\n\x1eUpdateMarketStateConfiguration\x12\x1b\n\tmarket_id\x18\x01 \x01(\tR\x08marketId\x12<\n\x0bupdate_type\x18\x02 \x01(\x0e\x32\x1b.vega.MarketStateUpdateTypeR\nupdateType\x12\x19\n\x05price\x18\x03 \x01(\tH\x00R\x05price\x88\x01\x01\x42\x08\n\x06_price"M\n\x0e\x43\x61ncelTransfer\x12;\n\x07\x63hanges\x18\x01 \x01(\x0b\x32!.vega.CancelTransferConfigurationR\x07\x63hanges">\n\x1b\x43\x61ncelTransferConfiguration\x12\x1f\n\x0btransfer_id\x18\x01 \x01(\tR\ntransferId"G\n\x0bNewTransfer\x12\x38\n\x07\x63hanges\x18\x01 \x01(\x0b\x32\x1e.vega.NewTransferConfigurationR\x07\x63hanges"\xd9\x03\n\x18NewTransferConfiguration\x12\x32\n\x0bsource_type\x18\x01 \x01(\x0e\x32\x11.vega.AccountTypeR\nsourceType\x12\x16\n\x06source\x18\x02 \x01(\tR\x06source\x12\x41\n\rtransfer_type\x18\x03 \x01(\x0e\x32\x1c.vega.GovernanceTransferTypeR\x0ctransferType\x12\x16\n\x06\x61mount\x18\x04 \x01(\tR\x06\x61mount\x12\x14\n\x05\x61sset\x18\x05 \x01(\tR\x05\x61sset\x12.\n\x13\x66raction_of_balance\x18\x06 \x01(\tR\x11\x66ractionOfBalance\x12<\n\x10\x64\x65stination_type\x18\x07 \x01(\x0e\x32\x11.vega.AccountTypeR\x0f\x64\x65stinationType\x12 \n\x0b\x64\x65stination\x18\x08 \x01(\tR\x0b\x64\x65stination\x12/\n\x07one_off\x18\x65 \x01(\x0b\x32\x14.vega.OneOffTransferH\x00R\x06oneOff\x12\x37\n\trecurring\x18\x66 \x01(\x0b\x32\x17.vega.RecurringTransferH\x00R\trecurringB\x06\n\x04kind"/\n\x0eOneOffTransfer\x12\x1d\n\ndeliver_on\x18\x01 \x01(\x03R\tdeliverOn"\xc4\x01\n\x11RecurringTransfer\x12\x1f\n\x0bstart_epoch\x18\x01 \x01(\x04R\nstartEpoch\x12 \n\tend_epoch\x18\x02 \x01(\x04H\x00R\x08\x65ndEpoch\x88\x01\x01\x12H\n\x11\x64ispatch_strategy\x18\x03 \x01(\x0b\x32\x16.vega.DispatchStrategyH\x01R\x10\x64ispatchStrategy\x88\x01\x01\x42\x0c\n\n_end_epochB\x14\n\x12_dispatch_strategy*\xd6\x12\n\rProposalError\x12\x1e\n\x1aPROPOSAL_ERROR_UNSPECIFIED\x10\x00\x12&\n"PROPOSAL_ERROR_CLOSE_TIME_TOO_SOON\x10\x01\x12&\n"PROPOSAL_ERROR_CLOSE_TIME_TOO_LATE\x10\x02\x12&\n"PROPOSAL_ERROR_ENACT_TIME_TOO_SOON\x10\x03\x12&\n"PROPOSAL_ERROR_ENACT_TIME_TOO_LATE\x10\x04\x12&\n"PROPOSAL_ERROR_INSUFFICIENT_TOKENS\x10\x05\x12.\n*PROPOSAL_ERROR_INVALID_INSTRUMENT_SECURITY\x10\x06\x12\x1d\n\x19PROPOSAL_ERROR_NO_PRODUCT\x10\x07\x12&\n"PROPOSAL_ERROR_UNSUPPORTED_PRODUCT\x10\x08\x12"\n\x1ePROPOSAL_ERROR_NO_TRADING_MODE\x10\x0b\x12+\n\'PROPOSAL_ERROR_UNSUPPORTED_TRADING_MODE\x10\x0c\x12)\n%PROPOSAL_ERROR_NODE_VALIDATION_FAILED\x10\r\x12.\n*PROPOSAL_ERROR_MISSING_BUILTIN_ASSET_FIELD\x10\x0e\x12\x31\n-PROPOSAL_ERROR_MISSING_ERC20_CONTRACT_ADDRESS\x10\x0f\x12 \n\x1cPROPOSAL_ERROR_INVALID_ASSET\x10\x10\x12*\n&PROPOSAL_ERROR_INCOMPATIBLE_TIMESTAMPS\x10\x11\x12%\n!PROPOSAL_ERROR_NO_RISK_PARAMETERS\x10\x12\x12\x30\n,PROPOSAL_ERROR_NETWORK_PARAMETER_INVALID_KEY\x10\x13\x12\x32\n.PROPOSAL_ERROR_NETWORK_PARAMETER_INVALID_VALUE\x10\x14\x12\x36\n2PROPOSAL_ERROR_NETWORK_PARAMETER_VALIDATION_FAILED\x10\x15\x12\x35\n1PROPOSAL_ERROR_OPENING_AUCTION_DURATION_TOO_SMALL\x10\x16\x12\x35\n1PROPOSAL_ERROR_OPENING_AUCTION_DURATION_TOO_LARGE\x10\x17\x12/\n+PROPOSAL_ERROR_COULD_NOT_INSTANTIATE_MARKET\x10\x19\x12)\n%PROPOSAL_ERROR_INVALID_FUTURE_PRODUCT\x10\x1a\x12)\n%PROPOSAL_ERROR_INVALID_RISK_PARAMETER\x10\x1e\x12\x31\n-PROPOSAL_ERROR_MAJORITY_THRESHOLD_NOT_REACHED\x10\x1f\x12\x36\n2PROPOSAL_ERROR_PARTICIPATION_THRESHOLD_NOT_REACHED\x10 \x12(\n$PROPOSAL_ERROR_INVALID_ASSET_DETAILS\x10!\x12\x1f\n\x1bPROPOSAL_ERROR_UNKNOWN_TYPE\x10"\x12.\n*PROPOSAL_ERROR_UNKNOWN_RISK_PARAMETER_TYPE\x10#\x12#\n\x1fPROPOSAL_ERROR_INVALID_FREEFORM\x10$\x12\x31\n-PROPOSAL_ERROR_INSUFFICIENT_EQUITY_LIKE_SHARE\x10%\x12!\n\x1dPROPOSAL_ERROR_INVALID_MARKET\x10&\x12\x31\n-PROPOSAL_ERROR_TOO_MANY_MARKET_DECIMAL_PLACES\x10\'\x12\x35\n1PROPOSAL_ERROR_TOO_MANY_PRICE_MONITORING_TRIGGERS\x10(\x12/\n+PROPOSAL_ERROR_ERC20_ADDRESS_ALREADY_IN_USE\x10)\x12-\n)PROPOSAL_ERROR_LP_PRICE_RANGE_NONPOSITIVE\x10*\x12+\n\'PROPOSAL_ERROR_LP_PRICE_RANGE_TOO_LARGE\x10+\x12\x36\n2PROPOSAL_ERROR_LINEAR_SLIPPAGE_FACTOR_OUT_OF_RANGE\x10,\x12\x39\n5PROPOSAL_ERROR_QUADRATIC_SLIPPAGE_FACTOR_OUT_OF_RANGE\x10-\x12\x1f\n\x1bPROPOSAL_ERROR_INVALID_SPOT\x10.\x12(\n$PROPOSAL_ERROR_SPOT_PRODUCT_DISABLED\x10/\x12+\n\'PROPOSAL_ERROR_INVALID_SUCCESSOR_MARKET\x10\x30\x12\x36\n2PROPOSAL_ERROR_GOVERNANCE_TRANSFER_PROPOSAL_FAILED\x10\x31\x12\x37\n3PROPOSAL_ERROR_GOVERNANCE_TRANSFER_PROPOSAL_INVALID\x10\x32\x12>\n:PROPOSAL_ERROR_GOVERNANCE_CANCEL_TRANSFER_PROPOSAL_INVALID\x10\x33\x12.\n*PROPOSAL_ERROR_INVALID_MARKET_STATE_UPDATE\x10\x34\x12%\n!PROPOSAL_ERROR_INVALID_SLA_PARAMS\x10\x35\x12%\n!PROPOSAL_ERROR_MISSING_SLA_PARAMS\x10\x36\x12,\n(PROPOSAL_ERROR_INVALID_PERPETUAL_PRODUCT\x10\x37\x12+\n\'PROPOSAL_ERROR_INVALID_REFERRAL_PROGRAM\x10\x38\x12\x32\n.PROPOSAL_ERROR_INVALID_VOLUME_DISCOUNT_PROGRAM\x10\x39*\xb4\x01\n\x15MarketStateUpdateType\x12(\n$MARKET_STATE_UPDATE_TYPE_UNSPECIFIED\x10\x00\x12&\n"MARKET_STATE_UPDATE_TYPE_TERMINATE\x10\x01\x12$\n MARKET_STATE_UPDATE_TYPE_SUSPEND\x10\x02\x12#\n\x1fMARKET_STATE_UPDATE_TYPE_RESUME\x10\x03*\x99\x01\n\x16GovernanceTransferType\x12(\n$GOVERNANCE_TRANSFER_TYPE_UNSPECIFIED\x10\x00\x12+\n\'GOVERNANCE_TRANSFER_TYPE_ALL_OR_NOTHING\x10\x01\x12(\n$GOVERNANCE_TRANSFER_TYPE_BEST_EFFORT\x10\x02\x42\'Z%code.vegaprotocol.io/vega/protos/vegab\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "vega.governance_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals["DESCRIPTOR"]._options = None
    _globals[
        "DESCRIPTOR"
    ]._serialized_options = b"Z%code.vegaprotocol.io/vega/protos/vega"
    _globals["_GOVERNANCEDATA_YESPARTYENTRY"]._options = None
    _globals["_GOVERNANCEDATA_YESPARTYENTRY"]._serialized_options = b"8\001"
    _globals["_GOVERNANCEDATA_NOPARTYENTRY"]._options = None
    _globals["_GOVERNANCEDATA_NOPARTYENTRY"]._serialized_options = b"8\001"
    _globals["_PROPOSALERROR"]._serialized_start = 10121
    _globals["_PROPOSALERROR"]._serialized_end = 12511
    _globals["_MARKETSTATEUPDATETYPE"]._serialized_start = 12514
    _globals["_MARKETSTATEUPDATETYPE"]._serialized_end = 12694
    _globals["_GOVERNANCETRANSFERTYPE"]._serialized_start = 12697
    _globals["_GOVERNANCETRANSFERTYPE"]._serialized_end = 12850
    _globals["_SPOTPRODUCT"]._serialized_start = 111
    _globals["_SPOTPRODUCT"]._serialized_end = 208
    _globals["_FUTUREPRODUCT"]._serialized_start = 211
    _globals["_FUTUREPRODUCT"]._serialized_end = 616
    _globals["_PERPETUALPRODUCT"]._serialized_start = 619
    _globals["_PERPETUALPRODUCT"]._serialized_end = 1207
    _globals["_INSTRUMENTCONFIGURATION"]._serialized_start = 1210
    _globals["_INSTRUMENTCONFIGURATION"]._serialized_end = 1430
    _globals["_NEWSPOTMARKETCONFIGURATION"]._serialized_start = 1433
    _globals["_NEWSPOTMARKETCONFIGURATION"]._serialized_end = 2019
    _globals["_NEWMARKETCONFIGURATION"]._serialized_start = 2022
    _globals["_NEWMARKETCONFIGURATION"]._serialized_end = 2910
    _globals["_NEWSPOTMARKET"]._serialized_start = 2912
    _globals["_NEWSPOTMARKET"]._serialized_end = 2987
    _globals["_SUCCESSORCONFIGURATION"]._serialized_start = 2989
    _globals["_SUCCESSORCONFIGURATION"]._serialized_end = 3111
    _globals["_NEWMARKET"]._serialized_start = 3113
    _globals["_NEWMARKET"]._serialized_end = 3180
    _globals["_UPDATEMARKET"]._serialized_start = 3182
    _globals["_UPDATEMARKET"]._serialized_end = 3284
    _globals["_UPDATESPOTMARKET"]._serialized_start = 3286
    _globals["_UPDATESPOTMARKET"]._serialized_end = 3396
    _globals["_UPDATEMARKETCONFIGURATION"]._serialized_start = 3399
    _globals["_UPDATEMARKETCONFIGURATION"]._serialized_end = 4122
    _globals["_UPDATESPOTMARKETCONFIGURATION"]._serialized_start = 4125
    _globals["_UPDATESPOTMARKETCONFIGURATION"]._serialized_end = 4556
    _globals["_UPDATEINSTRUMENTCONFIGURATION"]._serialized_start = 4559
    _globals["_UPDATEINSTRUMENTCONFIGURATION"]._serialized_end = 4736
    _globals["_UPDATEFUTUREPRODUCT"]._serialized_start = 4739
    _globals["_UPDATEFUTUREPRODUCT"]._serialized_end = 5107
    _globals["_UPDATEPERPETUALPRODUCT"]._serialized_start = 5110
    _globals["_UPDATEPERPETUALPRODUCT"]._serialized_end = 5661
    _globals["_UPDATENETWORKPARAMETER"]._serialized_start = 5663
    _globals["_UPDATENETWORKPARAMETER"]._serialized_end = 5737
    _globals["_NEWASSET"]._serialized_start = 5739
    _globals["_NEWASSET"]._serialized_end = 5795
    _globals["_UPDATEASSET"]._serialized_start = 5797
    _globals["_UPDATEASSET"]._serialized_end = 5889
    _globals["_NEWFREEFORM"]._serialized_start = 5891
    _globals["_NEWFREEFORM"]._serialized_end = 5904
    _globals["_PROPOSALTERMS"]._serialized_start = 5907
    _globals["_PROPOSALTERMS"]._serialized_end = 6959
    _globals["_PROPOSALRATIONALE"]._serialized_start = 6961
    _globals["_PROPOSALRATIONALE"]._serialized_end = 7048
    _globals["_GOVERNANCEDATA"]._serialized_start = 7051
    _globals["_GOVERNANCEDATA"]._serialized_end = 7441
    _globals["_GOVERNANCEDATA_YESPARTYENTRY"]._serialized_start = 7298
    _globals["_GOVERNANCEDATA_YESPARTYENTRY"]._serialized_end = 7369
    _globals["_GOVERNANCEDATA_NOPARTYENTRY"]._serialized_start = 7371
    _globals["_GOVERNANCEDATA_NOPARTYENTRY"]._serialized_end = 7441
    _globals["_PROPOSAL"]._serialized_start = 7444
    _globals["_PROPOSAL"]._serialized_end = 8366
    _globals["_PROPOSAL_STATE"]._serialized_start = 8076
    _globals["_PROPOSAL_STATE"]._serialized_end = 8250
    _globals["_VOTE"]._serialized_start = 8369
    _globals["_VOTE"]._serialized_end = 8770
    _globals["_VOTE_VALUE"]._serialized_start = 8711
    _globals["_VOTE_VALUE"]._serialized_end = 8770
    _globals["_UPDATEVOLUMEDISCOUNTPROGRAM"]._serialized_start = 8772
    _globals["_UPDATEVOLUMEDISCOUNTPROGRAM"]._serialized_end = 8856
    _globals["_UPDATEREFERRALPROGRAM"]._serialized_start = 8858
    _globals["_UPDATEREFERRALPROGRAM"]._serialized_end = 8930
    _globals["_UPDATEMARKETSTATE"]._serialized_start = 8932
    _globals["_UPDATEMARKETSTATE"]._serialized_end = 9015
    _globals["_UPDATEMARKETSTATECONFIGURATION"]._serialized_start = 9018
    _globals["_UPDATEMARKETSTATECONFIGURATION"]._serialized_end = 9178
    _globals["_CANCELTRANSFER"]._serialized_start = 9180
    _globals["_CANCELTRANSFER"]._serialized_end = 9257
    _globals["_CANCELTRANSFERCONFIGURATION"]._serialized_start = 9259
    _globals["_CANCELTRANSFERCONFIGURATION"]._serialized_end = 9321
    _globals["_NEWTRANSFER"]._serialized_start = 9323
    _globals["_NEWTRANSFER"]._serialized_end = 9394
    _globals["_NEWTRANSFERCONFIGURATION"]._serialized_start = 9397
    _globals["_NEWTRANSFERCONFIGURATION"]._serialized_end = 9870
    _globals["_ONEOFFTRANSFER"]._serialized_start = 9872
    _globals["_ONEOFFTRANSFER"]._serialized_end = 9919
    _globals["_RECURRINGTRANSFER"]._serialized_start = 9922
    _globals["_RECURRINGTRANSFER"]._serialized_end = 10118
# @@protoc_insertion_point(module_scope)
