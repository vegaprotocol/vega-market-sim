import time

from vega_sim.null_service import VegaServiceNull
from vega_sim.replay import replay


if __name__ == "__main__":
    log_dir="/var/folders/67/mjxp58z56yj83_1x0372gkwr0000gn/T/vega-sim-gvsbyhf7/"
    with replay.replay_run_context(retain_log_files=True,replay_path=log_dir) as vega:
        time.sleep(1)
        vega.wait_for_core_catchup()    
    
    print("All done.")