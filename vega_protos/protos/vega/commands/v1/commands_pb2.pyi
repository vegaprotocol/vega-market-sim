from vega.commands.v1 import validator_commands_pb2 as _validator_commands_pb2
from vega import governance_pb2 as _governance_pb2
from vega import vega_pb2 as _vega_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
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

class BatchMarketInstructions(_message.Message):
    __slots__ = (
        "cancellations",
        "amendments",
        "submissions",
        "stop_orders_cancellation",
        "stop_orders_submission",
        "update_margin_mode",
    )
    CANCELLATIONS_FIELD_NUMBER: _ClassVar[int]
    AMENDMENTS_FIELD_NUMBER: _ClassVar[int]
    SUBMISSIONS_FIELD_NUMBER: _ClassVar[int]
    STOP_ORDERS_CANCELLATION_FIELD_NUMBER: _ClassVar[int]
    STOP_ORDERS_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    UPDATE_MARGIN_MODE_FIELD_NUMBER: _ClassVar[int]
    cancellations: _containers.RepeatedCompositeFieldContainer[OrderCancellation]
    amendments: _containers.RepeatedCompositeFieldContainer[OrderAmendment]
    submissions: _containers.RepeatedCompositeFieldContainer[OrderSubmission]
    stop_orders_cancellation: _containers.RepeatedCompositeFieldContainer[
        StopOrdersCancellation
    ]
    stop_orders_submission: _containers.RepeatedCompositeFieldContainer[
        StopOrdersSubmission
    ]
    update_margin_mode: _containers.RepeatedCompositeFieldContainer[UpdateMarginMode]
    def __init__(
        self,
        cancellations: _Optional[_Iterable[_Union[OrderCancellation, _Mapping]]] = ...,
        amendments: _Optional[_Iterable[_Union[OrderAmendment, _Mapping]]] = ...,
        submissions: _Optional[_Iterable[_Union[OrderSubmission, _Mapping]]] = ...,
        stop_orders_cancellation: _Optional[
            _Iterable[_Union[StopOrdersCancellation, _Mapping]]
        ] = ...,
        stop_orders_submission: _Optional[
            _Iterable[_Union[StopOrdersSubmission, _Mapping]]
        ] = ...,
        update_margin_mode: _Optional[
            _Iterable[_Union[UpdateMarginMode, _Mapping]]
        ] = ...,
    ) -> None: ...

class StopOrdersSubmission(_message.Message):
    __slots__ = ("rises_above", "falls_below")
    RISES_ABOVE_FIELD_NUMBER: _ClassVar[int]
    FALLS_BELOW_FIELD_NUMBER: _ClassVar[int]
    rises_above: StopOrderSetup
    falls_below: StopOrderSetup
    def __init__(
        self,
        rises_above: _Optional[_Union[StopOrderSetup, _Mapping]] = ...,
        falls_below: _Optional[_Union[StopOrderSetup, _Mapping]] = ...,
    ) -> None: ...

class StopOrderSetup(_message.Message):
    __slots__ = (
        "order_submission",
        "expires_at",
        "expiry_strategy",
        "size_override_setting",
        "size_override_value",
        "price",
        "trailing_percent_offset",
    )
    ORDER_SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    SIZE_OVERRIDE_SETTING_FIELD_NUMBER: _ClassVar[int]
    SIZE_OVERRIDE_VALUE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    TRAILING_PERCENT_OFFSET_FIELD_NUMBER: _ClassVar[int]
    order_submission: OrderSubmission
    expires_at: int
    expiry_strategy: _vega_pb2.StopOrder.ExpiryStrategy
    size_override_setting: _vega_pb2.StopOrder.SizeOverrideSetting
    size_override_value: _vega_pb2.StopOrder.SizeOverrideValue
    price: str
    trailing_percent_offset: str
    def __init__(
        self,
        order_submission: _Optional[_Union[OrderSubmission, _Mapping]] = ...,
        expires_at: _Optional[int] = ...,
        expiry_strategy: _Optional[
            _Union[_vega_pb2.StopOrder.ExpiryStrategy, str]
        ] = ...,
        size_override_setting: _Optional[
            _Union[_vega_pb2.StopOrder.SizeOverrideSetting, str]
        ] = ...,
        size_override_value: _Optional[
            _Union[_vega_pb2.StopOrder.SizeOverrideValue, _Mapping]
        ] = ...,
        price: _Optional[str] = ...,
        trailing_percent_offset: _Optional[str] = ...,
    ) -> None: ...

class StopOrdersCancellation(_message.Message):
    __slots__ = ("market_id", "stop_order_id")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    STOP_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    stop_order_id: str
    def __init__(
        self, market_id: _Optional[str] = ..., stop_order_id: _Optional[str] = ...
    ) -> None: ...

class OrderSubmission(_message.Message):
    __slots__ = (
        "market_id",
        "price",
        "size",
        "side",
        "time_in_force",
        "expires_at",
        "type",
        "reference",
        "pegged_order",
        "post_only",
        "reduce_only",
        "iceberg_opts",
    )
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    TIME_IN_FORCE_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    PEGGED_ORDER_FIELD_NUMBER: _ClassVar[int]
    POST_ONLY_FIELD_NUMBER: _ClassVar[int]
    REDUCE_ONLY_FIELD_NUMBER: _ClassVar[int]
    ICEBERG_OPTS_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    price: str
    size: int
    side: _vega_pb2.Side
    time_in_force: _vega_pb2.Order.TimeInForce
    expires_at: int
    type: _vega_pb2.Order.Type
    reference: str
    pegged_order: _vega_pb2.PeggedOrder
    post_only: bool
    reduce_only: bool
    iceberg_opts: IcebergOpts
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        price: _Optional[str] = ...,
        size: _Optional[int] = ...,
        side: _Optional[_Union[_vega_pb2.Side, str]] = ...,
        time_in_force: _Optional[_Union[_vega_pb2.Order.TimeInForce, str]] = ...,
        expires_at: _Optional[int] = ...,
        type: _Optional[_Union[_vega_pb2.Order.Type, str]] = ...,
        reference: _Optional[str] = ...,
        pegged_order: _Optional[_Union[_vega_pb2.PeggedOrder, _Mapping]] = ...,
        post_only: bool = ...,
        reduce_only: bool = ...,
        iceberg_opts: _Optional[_Union[IcebergOpts, _Mapping]] = ...,
    ) -> None: ...

class IcebergOpts(_message.Message):
    __slots__ = ("peak_size", "minimum_visible_size")
    PEAK_SIZE_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_VISIBLE_SIZE_FIELD_NUMBER: _ClassVar[int]
    peak_size: int
    minimum_visible_size: int
    def __init__(
        self,
        peak_size: _Optional[int] = ...,
        minimum_visible_size: _Optional[int] = ...,
    ) -> None: ...

class UpdateMarginMode(_message.Message):
    __slots__ = ("market_id", "mode", "margin_factor")

    class Mode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MODE_UNSPECIFIED: _ClassVar[UpdateMarginMode.Mode]
        MODE_CROSS_MARGIN: _ClassVar[UpdateMarginMode.Mode]
        MODE_ISOLATED_MARGIN: _ClassVar[UpdateMarginMode.Mode]

    MODE_UNSPECIFIED: UpdateMarginMode.Mode
    MODE_CROSS_MARGIN: UpdateMarginMode.Mode
    MODE_ISOLATED_MARGIN: UpdateMarginMode.Mode
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    MARGIN_FACTOR_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    mode: UpdateMarginMode.Mode
    margin_factor: str
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        mode: _Optional[_Union[UpdateMarginMode.Mode, str]] = ...,
        margin_factor: _Optional[str] = ...,
    ) -> None: ...

class OrderCancellation(_message.Message):
    __slots__ = ("order_id", "market_id")
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    market_id: str
    def __init__(
        self, order_id: _Optional[str] = ..., market_id: _Optional[str] = ...
    ) -> None: ...

class OrderAmendment(_message.Message):
    __slots__ = (
        "order_id",
        "market_id",
        "price",
        "size_delta",
        "expires_at",
        "time_in_force",
        "pegged_offset",
        "pegged_reference",
        "size",
    )
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    SIZE_DELTA_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    TIME_IN_FORCE_FIELD_NUMBER: _ClassVar[int]
    PEGGED_OFFSET_FIELD_NUMBER: _ClassVar[int]
    PEGGED_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    market_id: str
    price: str
    size_delta: int
    expires_at: int
    time_in_force: _vega_pb2.Order.TimeInForce
    pegged_offset: str
    pegged_reference: _vega_pb2.PeggedReference
    size: int
    def __init__(
        self,
        order_id: _Optional[str] = ...,
        market_id: _Optional[str] = ...,
        price: _Optional[str] = ...,
        size_delta: _Optional[int] = ...,
        expires_at: _Optional[int] = ...,
        time_in_force: _Optional[_Union[_vega_pb2.Order.TimeInForce, str]] = ...,
        pegged_offset: _Optional[str] = ...,
        pegged_reference: _Optional[_Union[_vega_pb2.PeggedReference, str]] = ...,
        size: _Optional[int] = ...,
    ) -> None: ...

class LiquidityProvisionSubmission(_message.Message):
    __slots__ = ("market_id", "commitment_amount", "fee", "reference")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    COMMITMENT_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    FEE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    commitment_amount: str
    fee: str
    reference: str
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        commitment_amount: _Optional[str] = ...,
        fee: _Optional[str] = ...,
        reference: _Optional[str] = ...,
    ) -> None: ...

class LiquidityProvisionCancellation(_message.Message):
    __slots__ = ("market_id",)
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    def __init__(self, market_id: _Optional[str] = ...) -> None: ...

class LiquidityProvisionAmendment(_message.Message):
    __slots__ = ("market_id", "commitment_amount", "fee", "reference")
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    COMMITMENT_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    FEE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    commitment_amount: str
    fee: str
    reference: str
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        commitment_amount: _Optional[str] = ...,
        fee: _Optional[str] = ...,
        reference: _Optional[str] = ...,
    ) -> None: ...

class WithdrawSubmission(_message.Message):
    __slots__ = ("amount", "asset", "ext")
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    amount: str
    asset: str
    ext: _vega_pb2.WithdrawExt
    def __init__(
        self,
        amount: _Optional[str] = ...,
        asset: _Optional[str] = ...,
        ext: _Optional[_Union[_vega_pb2.WithdrawExt, _Mapping]] = ...,
    ) -> None: ...

class ProposalSubmission(_message.Message):
    __slots__ = ("reference", "terms", "rationale")
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    TERMS_FIELD_NUMBER: _ClassVar[int]
    RATIONALE_FIELD_NUMBER: _ClassVar[int]
    reference: str
    terms: _governance_pb2.ProposalTerms
    rationale: _governance_pb2.ProposalRationale
    def __init__(
        self,
        reference: _Optional[str] = ...,
        terms: _Optional[_Union[_governance_pb2.ProposalTerms, _Mapping]] = ...,
        rationale: _Optional[_Union[_governance_pb2.ProposalRationale, _Mapping]] = ...,
    ) -> None: ...

class BatchProposalSubmissionTerms(_message.Message):
    __slots__ = ("closing_timestamp", "changes")
    CLOSING_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    closing_timestamp: int
    changes: _containers.RepeatedCompositeFieldContainer[
        _governance_pb2.BatchProposalTermsChange
    ]
    def __init__(
        self,
        closing_timestamp: _Optional[int] = ...,
        changes: _Optional[
            _Iterable[_Union[_governance_pb2.BatchProposalTermsChange, _Mapping]]
        ] = ...,
    ) -> None: ...

class BatchProposalSubmission(_message.Message):
    __slots__ = ("reference", "terms", "rationale")
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    TERMS_FIELD_NUMBER: _ClassVar[int]
    RATIONALE_FIELD_NUMBER: _ClassVar[int]
    reference: str
    terms: BatchProposalSubmissionTerms
    rationale: _governance_pb2.ProposalRationale
    def __init__(
        self,
        reference: _Optional[str] = ...,
        terms: _Optional[_Union[BatchProposalSubmissionTerms, _Mapping]] = ...,
        rationale: _Optional[_Union[_governance_pb2.ProposalRationale, _Mapping]] = ...,
    ) -> None: ...

class VoteSubmission(_message.Message):
    __slots__ = ("proposal_id", "value")
    PROPOSAL_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    proposal_id: str
    value: _governance_pb2.Vote.Value
    def __init__(
        self,
        proposal_id: _Optional[str] = ...,
        value: _Optional[_Union[_governance_pb2.Vote.Value, str]] = ...,
    ) -> None: ...

class DelegateSubmission(_message.Message):
    __slots__ = ("node_id", "amount")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    amount: str
    def __init__(
        self, node_id: _Optional[str] = ..., amount: _Optional[str] = ...
    ) -> None: ...

class UndelegateSubmission(_message.Message):
    __slots__ = ("node_id", "amount", "method")

    class Method(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        METHOD_UNSPECIFIED: _ClassVar[UndelegateSubmission.Method]
        METHOD_NOW: _ClassVar[UndelegateSubmission.Method]
        METHOD_AT_END_OF_EPOCH: _ClassVar[UndelegateSubmission.Method]

    METHOD_UNSPECIFIED: UndelegateSubmission.Method
    METHOD_NOW: UndelegateSubmission.Method
    METHOD_AT_END_OF_EPOCH: UndelegateSubmission.Method
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    amount: str
    method: UndelegateSubmission.Method
    def __init__(
        self,
        node_id: _Optional[str] = ...,
        amount: _Optional[str] = ...,
        method: _Optional[_Union[UndelegateSubmission.Method, str]] = ...,
    ) -> None: ...

class Transfer(_message.Message):
    __slots__ = (
        "from_account_type",
        "to",
        "to_account_type",
        "asset",
        "amount",
        "reference",
        "one_off",
        "recurring",
    )
    FROM_ACCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    TO_ACCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    ASSET_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    ONE_OFF_FIELD_NUMBER: _ClassVar[int]
    RECURRING_FIELD_NUMBER: _ClassVar[int]
    from_account_type: _vega_pb2.AccountType
    to: str
    to_account_type: _vega_pb2.AccountType
    asset: str
    amount: str
    reference: str
    one_off: OneOffTransfer
    recurring: RecurringTransfer
    def __init__(
        self,
        from_account_type: _Optional[_Union[_vega_pb2.AccountType, str]] = ...,
        to: _Optional[str] = ...,
        to_account_type: _Optional[_Union[_vega_pb2.AccountType, str]] = ...,
        asset: _Optional[str] = ...,
        amount: _Optional[str] = ...,
        reference: _Optional[str] = ...,
        one_off: _Optional[_Union[OneOffTransfer, _Mapping]] = ...,
        recurring: _Optional[_Union[RecurringTransfer, _Mapping]] = ...,
        **kwargs
    ) -> None: ...

class OneOffTransfer(_message.Message):
    __slots__ = ("deliver_on",)
    DELIVER_ON_FIELD_NUMBER: _ClassVar[int]
    deliver_on: int
    def __init__(self, deliver_on: _Optional[int] = ...) -> None: ...

class RecurringTransfer(_message.Message):
    __slots__ = ("start_epoch", "end_epoch", "factor", "dispatch_strategy")
    START_EPOCH_FIELD_NUMBER: _ClassVar[int]
    END_EPOCH_FIELD_NUMBER: _ClassVar[int]
    FACTOR_FIELD_NUMBER: _ClassVar[int]
    DISPATCH_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    start_epoch: int
    end_epoch: int
    factor: str
    dispatch_strategy: _vega_pb2.DispatchStrategy
    def __init__(
        self,
        start_epoch: _Optional[int] = ...,
        end_epoch: _Optional[int] = ...,
        factor: _Optional[str] = ...,
        dispatch_strategy: _Optional[
            _Union[_vega_pb2.DispatchStrategy, _Mapping]
        ] = ...,
    ) -> None: ...

class CancelTransfer(_message.Message):
    __slots__ = ("transfer_id",)
    TRANSFER_ID_FIELD_NUMBER: _ClassVar[int]
    transfer_id: str
    def __init__(self, transfer_id: _Optional[str] = ...) -> None: ...

class IssueSignatures(_message.Message):
    __slots__ = ("submitter", "kind", "validator_node_id", "chain_id")
    SUBMITTER_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_NODE_ID_FIELD_NUMBER: _ClassVar[int]
    CHAIN_ID_FIELD_NUMBER: _ClassVar[int]
    submitter: str
    kind: _validator_commands_pb2.NodeSignatureKind
    validator_node_id: str
    chain_id: str
    def __init__(
        self,
        submitter: _Optional[str] = ...,
        kind: _Optional[_Union[_validator_commands_pb2.NodeSignatureKind, str]] = ...,
        validator_node_id: _Optional[str] = ...,
        chain_id: _Optional[str] = ...,
    ) -> None: ...

class CreateReferralSet(_message.Message):
    __slots__ = ("is_team", "team", "do_not_create_referral_set")

    class Team(_message.Message):
        __slots__ = ("name", "team_url", "avatar_url", "closed", "allow_list")
        NAME_FIELD_NUMBER: _ClassVar[int]
        TEAM_URL_FIELD_NUMBER: _ClassVar[int]
        AVATAR_URL_FIELD_NUMBER: _ClassVar[int]
        CLOSED_FIELD_NUMBER: _ClassVar[int]
        ALLOW_LIST_FIELD_NUMBER: _ClassVar[int]
        name: str
        team_url: str
        avatar_url: str
        closed: bool
        allow_list: _containers.RepeatedScalarFieldContainer[str]
        def __init__(
            self,
            name: _Optional[str] = ...,
            team_url: _Optional[str] = ...,
            avatar_url: _Optional[str] = ...,
            closed: bool = ...,
            allow_list: _Optional[_Iterable[str]] = ...,
        ) -> None: ...

    IS_TEAM_FIELD_NUMBER: _ClassVar[int]
    TEAM_FIELD_NUMBER: _ClassVar[int]
    DO_NOT_CREATE_REFERRAL_SET_FIELD_NUMBER: _ClassVar[int]
    is_team: bool
    team: CreateReferralSet.Team
    do_not_create_referral_set: bool
    def __init__(
        self,
        is_team: bool = ...,
        team: _Optional[_Union[CreateReferralSet.Team, _Mapping]] = ...,
        do_not_create_referral_set: bool = ...,
    ) -> None: ...

class UpdateReferralSet(_message.Message):
    __slots__ = ("id", "is_team", "team")

    class Team(_message.Message):
        __slots__ = ("name", "team_url", "avatar_url", "closed", "allow_list")
        NAME_FIELD_NUMBER: _ClassVar[int]
        TEAM_URL_FIELD_NUMBER: _ClassVar[int]
        AVATAR_URL_FIELD_NUMBER: _ClassVar[int]
        CLOSED_FIELD_NUMBER: _ClassVar[int]
        ALLOW_LIST_FIELD_NUMBER: _ClassVar[int]
        name: str
        team_url: str
        avatar_url: str
        closed: bool
        allow_list: _containers.RepeatedScalarFieldContainer[str]
        def __init__(
            self,
            name: _Optional[str] = ...,
            team_url: _Optional[str] = ...,
            avatar_url: _Optional[str] = ...,
            closed: bool = ...,
            allow_list: _Optional[_Iterable[str]] = ...,
        ) -> None: ...

    ID_FIELD_NUMBER: _ClassVar[int]
    IS_TEAM_FIELD_NUMBER: _ClassVar[int]
    TEAM_FIELD_NUMBER: _ClassVar[int]
    id: str
    is_team: bool
    team: UpdateReferralSet.Team
    def __init__(
        self,
        id: _Optional[str] = ...,
        is_team: bool = ...,
        team: _Optional[_Union[UpdateReferralSet.Team, _Mapping]] = ...,
    ) -> None: ...

class ApplyReferralCode(_message.Message):
    __slots__ = ("id", "do_not_join_team")
    ID_FIELD_NUMBER: _ClassVar[int]
    DO_NOT_JOIN_TEAM_FIELD_NUMBER: _ClassVar[int]
    id: str
    do_not_join_team: bool
    def __init__(
        self, id: _Optional[str] = ..., do_not_join_team: bool = ...
    ) -> None: ...

class JoinTeam(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class UpdatePartyProfile(_message.Message):
    __slots__ = ("alias", "metadata")
    ALIAS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    alias: str
    metadata: _containers.RepeatedCompositeFieldContainer[_vega_pb2.Metadata]
    def __init__(
        self,
        alias: _Optional[str] = ...,
        metadata: _Optional[_Iterable[_Union[_vega_pb2.Metadata, _Mapping]]] = ...,
    ) -> None: ...

class SubmitAMM(_message.Message):
    __slots__ = (
        "market_id",
        "commitment_amount",
        "slippage_tolerance",
        "concentrated_liquidity_parameters",
        "proposed_fee",
    )

    class ConcentratedLiquidityParameters(_message.Message):
        __slots__ = (
            "upper_bound",
            "lower_bound",
            "base",
            "leverage_at_upper_bound",
            "leverage_at_lower_bound",
        )
        UPPER_BOUND_FIELD_NUMBER: _ClassVar[int]
        LOWER_BOUND_FIELD_NUMBER: _ClassVar[int]
        BASE_FIELD_NUMBER: _ClassVar[int]
        LEVERAGE_AT_UPPER_BOUND_FIELD_NUMBER: _ClassVar[int]
        LEVERAGE_AT_LOWER_BOUND_FIELD_NUMBER: _ClassVar[int]
        upper_bound: str
        lower_bound: str
        base: str
        leverage_at_upper_bound: str
        leverage_at_lower_bound: str
        def __init__(
            self,
            upper_bound: _Optional[str] = ...,
            lower_bound: _Optional[str] = ...,
            base: _Optional[str] = ...,
            leverage_at_upper_bound: _Optional[str] = ...,
            leverage_at_lower_bound: _Optional[str] = ...,
        ) -> None: ...

    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    COMMITMENT_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    SLIPPAGE_TOLERANCE_FIELD_NUMBER: _ClassVar[int]
    CONCENTRATED_LIQUIDITY_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    PROPOSED_FEE_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    commitment_amount: str
    slippage_tolerance: str
    concentrated_liquidity_parameters: SubmitAMM.ConcentratedLiquidityParameters
    proposed_fee: str
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        commitment_amount: _Optional[str] = ...,
        slippage_tolerance: _Optional[str] = ...,
        concentrated_liquidity_parameters: _Optional[
            _Union[SubmitAMM.ConcentratedLiquidityParameters, _Mapping]
        ] = ...,
        proposed_fee: _Optional[str] = ...,
    ) -> None: ...

class AmendAMM(_message.Message):
    __slots__ = (
        "market_id",
        "commitment_amount",
        "slippage_tolerance",
        "concentrated_liquidity_parameters",
        "proposed_fee",
    )

    class ConcentratedLiquidityParameters(_message.Message):
        __slots__ = (
            "upper_bound",
            "lower_bound",
            "base",
            "leverage_at_upper_bound",
            "leverage_at_lower_bound",
        )
        UPPER_BOUND_FIELD_NUMBER: _ClassVar[int]
        LOWER_BOUND_FIELD_NUMBER: _ClassVar[int]
        BASE_FIELD_NUMBER: _ClassVar[int]
        LEVERAGE_AT_UPPER_BOUND_FIELD_NUMBER: _ClassVar[int]
        LEVERAGE_AT_LOWER_BOUND_FIELD_NUMBER: _ClassVar[int]
        upper_bound: str
        lower_bound: str
        base: str
        leverage_at_upper_bound: str
        leverage_at_lower_bound: str
        def __init__(
            self,
            upper_bound: _Optional[str] = ...,
            lower_bound: _Optional[str] = ...,
            base: _Optional[str] = ...,
            leverage_at_upper_bound: _Optional[str] = ...,
            leverage_at_lower_bound: _Optional[str] = ...,
        ) -> None: ...

    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    COMMITMENT_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    SLIPPAGE_TOLERANCE_FIELD_NUMBER: _ClassVar[int]
    CONCENTRATED_LIQUIDITY_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    PROPOSED_FEE_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    commitment_amount: str
    slippage_tolerance: str
    concentrated_liquidity_parameters: AmendAMM.ConcentratedLiquidityParameters
    proposed_fee: str
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        commitment_amount: _Optional[str] = ...,
        slippage_tolerance: _Optional[str] = ...,
        concentrated_liquidity_parameters: _Optional[
            _Union[AmendAMM.ConcentratedLiquidityParameters, _Mapping]
        ] = ...,
        proposed_fee: _Optional[str] = ...,
    ) -> None: ...

class CancelAMM(_message.Message):
    __slots__ = ("market_id", "method")

    class Method(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        METHOD_UNSPECIFIED: _ClassVar[CancelAMM.Method]
        METHOD_IMMEDIATE: _ClassVar[CancelAMM.Method]
        METHOD_REDUCE_ONLY: _ClassVar[CancelAMM.Method]

    METHOD_UNSPECIFIED: CancelAMM.Method
    METHOD_IMMEDIATE: CancelAMM.Method
    METHOD_REDUCE_ONLY: CancelAMM.Method
    MARKET_ID_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    market_id: str
    method: CancelAMM.Method
    def __init__(
        self,
        market_id: _Optional[str] = ...,
        method: _Optional[_Union[CancelAMM.Method, str]] = ...,
    ) -> None: ...

class DelayedTransactionsWrapper(_message.Message):
    __slots__ = ("transactions", "height")
    TRANSACTIONS_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    transactions: _containers.RepeatedScalarFieldContainer[bytes]
    height: int
    def __init__(
        self,
        transactions: _Optional[_Iterable[bytes]] = ...,
        height: _Optional[int] = ...,
    ) -> None: ...
