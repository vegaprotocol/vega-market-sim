import logging
import subprocess
import multiprocessing

def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = multiprocessing.Process(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

class VegaWallet:
    logger = logging.getLogger("vegawallet")

    def __init__(self, bin_path: str, network_name: str, token_file_path: str) -> None:
        self.bin_path = bin_path
        self.token_file_path = token_file_path
        self.network_name = network_name
        self.process = None
        self.process_thread = None
    

    def run(self, check: bool = False) -> subprocess.CompletedProcess:
        """
        Starts the vegawallet binary for the given network
        """

        VegaWallet.logger.info("Starting the vegawallet process")
        if self.process != None:
            raise RuntimeError("Wallet is already running")
        
        wallet_args = (
            self.bin_path, 
            "service",
            "run",
            "--network",
            self.network_name,
            "--load-tokens",
            "--automatic-consent",
            "--tokens-passphrase-file",
            self.token_file_path,
        )

        self.process = subprocess.Popen(
            wallet_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        try:
            with self.process.stdout:
                for line in iter(self.process.stdout.readline, b''):
                    VegaWallet.logger.info(line.decode("utf-8").strip())
                
        except subprocess.CalledProcessError as e:
            VegaWallet.logger.error(f"{str(e)}")

        
    @threaded
    def background_run(self):
        VegaWallet.logger.info("Running the wallet in the background")
        self.run()
        

    def __del__(self):
        """
        Manage the resource reserved by this class
        """

        VegaWallet.logger.info("Stopping the vegawallet process")
        # if not self.process is None:
        #     self.process.kill()
            