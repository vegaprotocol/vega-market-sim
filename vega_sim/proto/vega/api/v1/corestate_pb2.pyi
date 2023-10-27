from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2
from vega import assets_pb2 as _assets_pb2
from vega.events.v1 import events_pb2 as _events_pb2
from vega import governance_pb2 as _governance_pb2
from vega import markets_pb2 as _markets_pb2
from vega import vega_pb2 as _vega_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class Account(_message.Message):
    __slots__ = ["party", "market", "balance", "asset", "type"]
    PARTY_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    party: str
    market: str
    balance: str
    asset: str
    type: str
    def __init__(
        self,
        party: _Optional[str] = ...,
        market: _Optional[str] = ...,
        balance: _Optional[str] = ...,
        asset: _Optional[str] = ...,
        type: _Optional[str] = ...,
    ) -> None: ...

class ListAccountsRequest(_message.Message):
    __slots__ = ["party", "market"]
    PARTY_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    party: str
    market: str
    def __init__(
        self, party: _Optional[str] = ..., market: _Optional[str] = ...
    ) -> None: ...

class ListAccountsResponse(_message.Message):
    __slots__ = ["accounts"]
    ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    accounts: _containers.RepeatedCompositeFieldContainer[Account]
    def __init__(
        self, accounts: _Optional[_Iterable[_Union[Account, _Mapping]]] = ...
    ) -> None: ...

class ListAssetsRequest(_message.Message):
    __slots__ = ["asset"]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    asset: str
    def __init__(self, asset: _Optional[str] = ...) -> None: ...

class ListAssetsResponse(_message.Message):
    __slots__ = ["assets"]
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    assets: _containers.RepeatedCompositeFieldContainer[_assets_pb2.Asset]
    def __init__(
        self, assets: _Optional[_Iterable[_Union[_assets_pb2.Asset, _Mapping]]] = ...
    ) -> None: ...

class ListNetworkParametersRequest(_message.Message):
    __slots__ = ["network_parameter_key"]
    NETWORK_PARAMETER_KEY_FIELD_NUMBER: _ClassVar[int]
    network_parameter_key: str
    def __init__(self, network_parameter_key: _Optional[str] = ...) -> None: ...

class ListNetworkParametersResponse(_message.Message):
    __slots__ = ["network_parameters"]
    NETWORK_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    network_parameters: _containers.RepeatedCompositeFieldContainer[
        _vega_pb2.NetworkParameter
    ]
    def __init__(
        self,
        network_parameters: _Optional[
            _Iterable[_Union[_vega_pb2.NetworkParameter, _Mapping]]
        ] = ...,
    ) -> None: ...

class ListNetworkLimitsRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ListNetworkLimitsResponse(_message.Message):
    __slots__ = ["network_limits"]
    NETWORK_LIMITS_FIELD_NUMBER: _ClassVar[int]
    network_limits: _vega_pb2.NetworkLimits
    def __init__(
        self, network_limits: _Optional[_Union[_vega_pb2.NetworkLimits, _Mapping]] = ...
    ) -> None: ...

class ListPartiesRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ListPartiesResponse(_message.Message):
    __slots__ = ["parties"]
    PARTIES_FIELD_NUMBER: _ClassVar[int]
    parties: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Party]
    def __init__(
        self, parties: _Optional[_Iterable[_Union[_vega_pb2.Party, _Mapping]]] = ...
    ) -> None: ...

class ListValidatorsRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ListValidatorsResponse(_message.Message):
    __slots__ = ["validators"]
    VALIDATORS_FIELD_NUMBER: _ClassVar[int]
    validators: _containers.RepeatedCompositeFieldContainer[_events_pb2.ValidatorUpdate]
    def __init__(
        self,
        validators: _Optional[
            _Iterable[_Union[_events_pb2.ValidatorUpdate, _Mapping]]
        ] = ...,
    ) -> None: ...

class ListMarketsRequest(_message.Message):
    __slots__ = ["market"]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    market: str
    def __init__(self, market: _Optional[str] = ...) -> None: ...

class ListMarketsResponse(_message.Message):
    __slots__ = ["markets"]
    MARKETS_FIELD_NUMBER: _ClassVar[int]
    markets: _containers.RepeatedCompositeFieldContainer[_markets_pb2.Market]
    def __init__(
        self, markets: _Optional[_Iterable[_Union[_markets_pb2.Market, _Mapping]]] = ...
    ) -> None: ...

class ListProposalsRequest(_message.Message):
    __slots__ = ["proposal", "proposer"]
    PROPOSAL_FIELD_NUMBER: _ClassVar[int]
    PROPOSER_FIELD_NUMBER: _ClassVar[int]
    proposal: str
    proposer: str
    def __init__(
        self, proposal: _Optional[str] = ..., proposer: _Optional[str] = ...
    ) -> None: ...

class ListProposalsResponse(_message.Message):
    __slots__ = ["proposals"]
    PROPOSALS_FIELD_NUMBER: _ClassVar[int]
    proposals: _containers.RepeatedCompositeFieldContainer[_governance_pb2.Proposal]
    def __init__(
        self,
        proposals: _Optional[
            _Iterable[_Union[_governance_pb2.Proposal, _Mapping]]
        ] = ...,
    ) -> None: ...

class ListMarketsDataRequest(_message.Message):
    __slots__ = ["market"]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    market: str
    def __init__(self, market: _Optional[str] = ...) -> None: ...

class ListMarketsDataResponse(_message.Message):
    __slots__ = ["markets_data"]
    MARKETS_DATA_FIELD_NUMBER: _ClassVar[int]
    markets_data: _containers.RepeatedCompositeFieldContainer[_vega_pb2.MarketData]
    def __init__(
        self,
        markets_data: _Optional[
            _Iterable[_Union[_vega_pb2.MarketData, _Mapping]]
        ] = ...,
    ) -> None: ...

class ListVotesRequest(_message.Message):
    __slots__ = ["proposal", "party"]
    PROPOSAL_FIELD_NUMBER: _ClassVar[int]
    PARTY_FIELD_NUMBER: _ClassVar[int]
    proposal: str
    party: str
    def __init__(
        self, proposal: _Optional[str] = ..., party: _Optional[str] = ...
    ) -> None: ...

class ListVotesResponse(_message.Message):
    __slots__ = ["votes"]
    VOTES_FIELD_NUMBER: _ClassVar[int]
    votes: _containers.RepeatedCompositeFieldContainer[_governance_pb2.Vote]
    def __init__(
        self, votes: _Optional[_Iterable[_Union[_governance_pb2.Vote, _Mapping]]] = ...
    ) -> None: ...

class PartyStake(_message.Message):
    __slots__ = ["party", "current_stake_available", "stake_linkings"]
    PARTY_FIELD_NUMBER: _ClassVar[int]
    CURRENT_STAKE_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    STAKE_LINKINGS_FIELD_NUMBER: _ClassVar[int]
    party: str
    current_stake_available: str
    stake_linkings: _containers.RepeatedCompositeFieldContainer[
        _events_pb2.StakeLinking
    ]
    def __init__(
        self,
        party: _Optional[str] = ...,
        current_stake_available: _Optional[str] = ...,
        stake_linkings: _Optional[
            _Iterable[_Union[_events_pb2.StakeLinking, _Mapping]]
        ] = ...,
    ) -> None: ...

class ListPartiesStakeRequest(_message.Message):
    __slots__ = ["party"]
    PARTY_FIELD_NUMBER: _ClassVar[int]
    party: str
    def __init__(self, party: _Optional[str] = ...) -> None: ...

class ListPartiesStakeResponse(_message.Message):
    __slots__ = ["parties_stake"]
    PARTIES_STAKE_FIELD_NUMBER: _ClassVar[int]
    parties_stake: _containers.RepeatedCompositeFieldContainer[PartyStake]
    def __init__(
        self, parties_stake: _Optional[_Iterable[_Union[PartyStake, _Mapping]]] = ...
    ) -> None: ...

class ListDelegationsRequest(_message.Message):
    __slots__ = ["party", "node", "epoch_seq"]
    PARTY_FIELD_NUMBER: _ClassVar[int]
    NODE_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SEQ_FIELD_NUMBER: _ClassVar[int]
    party: str
    node: str
    epoch_seq: str
    def __init__(
        self,
        party: _Optional[str] = ...,
        node: _Optional[str] = ...,
        epoch_seq: _Optional[str] = ...,
    ) -> None: ...

class ListDelegationsResponse(_message.Message):
    __slots__ = ["delegations"]
    DELEGATIONS_FIELD_NUMBER: _ClassVar[int]
    delegations: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Delegation]
    def __init__(
        self,
        delegations: _Optional[_Iterable[_Union[_vega_pb2.Delegation, _Mapping]]] = ...,
    ) -> None: ...
