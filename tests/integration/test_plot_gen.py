from vega_sim.scenario.curve_market_maker.scenario import CurveMarketMaker
from vega_sim.null_service import VegaServiceNull
from vega_sim.tools.scenario_plots import plot_run_outputs


# Not included in pytest runs at all as this 'test' is generating a plot for
# later visual inspection rather than asserting anything and should only run
# when someone specifically wants it.
def generate_trading_plot():
    scen = CurveMarketMaker(
        market_name="ETH",
        asset_name="USD",
        num_steps=290,
        market_decimal=2,
        asset_decimal=4,
        market_position_decimal=4,
        initial_price=1000,
        lp_commitamount=250_000,
        initial_asset_mint=10_000_000,
        step_length_seconds=60,
        # step_length_seconds=Granularity.HOUR.value,
        block_length_seconds=1,
        q_upper=30,
        q_lower=-30,
        market_maker_curve_kappa=0.2,
        market_maker_assumed_market_kappa=0.2,
        buy_intensity=100,
        sell_intensity=100,
        sensitive_price_taker_half_life=10,
        opening_auction_trade_amount=0.0001,
        market_order_trader_base_order_size=0.01,
    )
    with VegaServiceNull(
        warn_on_raw_data_access=False,
        retain_log_files=True,
    ) as vega:
        scen.run_iteration(vega=vega, output_data=True)
        figs = plot_run_outputs()
        for key, value in figs.items():
            value.savefig(f"{key}.jpg")


if __name__ == "__main__":
    generate_trading_plot()
