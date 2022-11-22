import logging

from vega_sim.null_service import VegaServiceNull

logger = logging.getLogger(__name__)


class VegaServiceNullPool:
    def __init__(self, *args, num_instances: int = 1, **kwargs):
        self.start_order_feed = kwargs.pop("start_order_feed", True)

        self.args = args
        self.kwargs = kwargs
        self.num_instances = num_instances

        self.instances = [
            VegaServiceNull(*self.args, **self.kwargs, start_order_feed=False)
            for _ in range(self.num_instances)
        ]
        self.next_instance_idx = 0

    def __enter__(self):
        for instance in self.instances:
            instance.start(block_on_startup=False)
        return self

    def __exit__(self, type, value, traceback):
        for instance in self.instances:
            instance.stop()

    def get_instance(self):
        to_ret = self.instances[self.next_instance_idx]
        to_ret.wait_for_ready()
        if self.start_order_feed:
            to_ret.start_order_monitoring()

        self.next_instance_idx += 1

        self.instances.append(
            VegaServiceNull(*self.args, **self.kwargs, start_order_feed=False)
        )
        self.instances[-1].start(block_on_startup=False)

        return to_ret


if __name__ == "__main__":
    with VegaServiceNullPool(
        num_instances=5,
        run_with_console=False,
        launch_graphql=False,
        retain_log_files=True,
        use_full_vega_wallet=False,
        store_transactions=True,
    ) as vsp:
        for i in range(50):
            inst = vsp.get_instance()
            print(i)
            inst.stop()
        print("hello")
