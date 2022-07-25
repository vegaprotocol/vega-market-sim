from vega_sim.null_service import VegaServiceNull


# Simply testing that multiple Vegas start
# in the same process ok
def test_multiple_instantiation():
    with VegaServiceNull(
        run_with_console=False,
        start_order_feed=False,
    ) as _:
        pass
    with VegaServiceNull(
        run_with_console=False,
        start_order_feed=False,
    ) as _:
        pass
    with VegaServiceNull(
        run_with_console=False,
        start_order_feed=False,
    ) as _:
        pass
    with VegaServiceNull(
        run_with_console=False,
        start_order_feed=False,
    ) as _:
        with VegaServiceNull(
            run_with_console=False,
            start_order_feed=False,
        ) as _:
            pass
