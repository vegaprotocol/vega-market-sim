from vega_sim.scenario.common.agents import MarketRegime, MultiRegimeBackgroundMarket


def test_market_regime_sparse_to_dense():
    market_regimes = [
        MarketRegime(
            spread=1,
            tick_spacing=1.4,
            num_levels_per_side=5,
            base_volume_size=1,
            order_distribution_kappa=1.4,
            from_timepoint=0,
            thru_timepoint=500,
        )
    ]
    dense_regime = MultiRegimeBackgroundMarket._market_regime_sparse_to_dense(
        market_regimes=market_regimes, num_steps=500
    )

    for regime in dense_regime:
        assert regime == market_regimes[0]


def test_market_regime_sparse_to_dense_multi():
    market_regimes = [
        MarketRegime(
            spread=1,
            tick_spacing=1.4,
            num_levels_per_side=5,
            base_volume_size=1,
            order_distribution_kappa=1.4,
            from_timepoint=0,
            thru_timepoint=100,
        ),
        MarketRegime(
            spread=3,
            tick_spacing=1.4,
            num_levels_per_side=5,
            base_volume_size=1,
            order_distribution_kappa=1.4,
            from_timepoint=101,
            thru_timepoint=240,
        ),
        MarketRegime(
            spread=5,
            tick_spacing=1.4,
            num_levels_per_side=5,
            base_volume_size=1,
            order_distribution_kappa=1.4,
            from_timepoint=241,
            thru_timepoint=500,
        ),
    ]
    dense_regime = MultiRegimeBackgroundMarket._market_regime_sparse_to_dense(
        market_regimes=market_regimes, num_steps=500
    )

    for i, regime in enumerate(dense_regime):
        if i < 101:
            assert regime == market_regimes[0]
        elif i >= 101 and i < 241:
            assert regime == market_regimes[1]
        else:
            assert regime == market_regimes[2]


def test_market_regime_sparse_to_dense_multi_gaps():
    market_regimes = [
        MarketRegime(
            spread=1,
            tick_spacing=1.4,
            num_levels_per_side=5,
            base_volume_size=1,
            order_distribution_kappa=1.4,
            from_timepoint=0,
            thru_timepoint=100,
        ),
        MarketRegime(
            spread=3,
            tick_spacing=1.4,
            num_levels_per_side=5,
            base_volume_size=1,
            order_distribution_kappa=1.4,
            from_timepoint=110,
            thru_timepoint=240,
        ),
        MarketRegime(
            spread=5,
            tick_spacing=1.4,
            num_levels_per_side=5,
            base_volume_size=1,
            order_distribution_kappa=1.4,
            from_timepoint=241,
            thru_timepoint=500,
        ),
    ]
    dense_regime = MultiRegimeBackgroundMarket._market_regime_sparse_to_dense(
        market_regimes=market_regimes, num_steps=500
    )

    for i, regime in enumerate(dense_regime):
        if i < 101:
            assert regime == market_regimes[0]
        elif i >= 101 and i < 110:
            assert regime is None
        elif i >= 110 and i < 241:
            assert regime == market_regimes[1]
        else:
            assert regime == market_regimes[2]
