from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.registry import  IdealMarketMakerV2
from vega_sim.parameter_test.parameter.loggers import (
    ideal_market_maker_single_data_extraction,
    target_stake_additional_data,
    v1_ideal_mm_additional_data,
    tau_scaling_additional_data,
    limit_order_book,
)



if __name__ == '__main__':
    with VegaServiceNull(
        run_with_console=False, 
        use_full_vega_wallet=False, 
        warn_on_raw_data_access=False) as vega:

    
        scenario = IdealMarketMakerV2(
            market_decimal=3,
            asset_decimal=5,
            market_position_decimal=2,
            initial_price=1123.11,
            spread=0.002,
            lp_commitamount=20000,
            step_length_seconds=60,
            block_length_seconds=1,
            buy_intensity=10,
            sell_intensity=10,
            q_upper=50,
            q_lower=-50,
            kappa=50,
            sigma=0.5,
            num_steps=72,
            state_extraction_fn=ideal_market_maker_single_data_extraction(
                additional_data_fns=[
                    tau_scaling_additional_data,
                    target_stake_additional_data,
                ]
            ),
        )
        
        
        print("Starting a run...")
        # res = scenario[0].run_iteration(vega=vega, pause_at_completion=False, run_with_console=False)
        env = scenario.set_up_background_market(
                vega=vega, tag=str(0),
            )
        result = env.run(pause_at_completion=False)
        
        # env.agents.append
        # scenario[0].age
        print("Wrapping up...")
        # vega.stop()