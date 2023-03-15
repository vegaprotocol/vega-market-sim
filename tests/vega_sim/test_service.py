import json
from typing import Optional
import pytest
import requests_mock

from vega_sim.service import VegaService
from vega_sim.wallet.vega_wallet import (
    WALLET_CREATION_URL,
    WALLET_KEY_URL,
    WALLET_LOGIN_URL,
    VegaWallet,
)


class StubService(VegaService):
    def __init__(self, wallet_url: str):
        super().__init__()
        self._wallet = VegaWallet(
            wallet_url=wallet_url,
            wallet_path="",
            vega_home_dir="",
            passphrase_file_path="",
        )

    @property
    def wallet(self):
        return self._wallet

    def start_order_monitoring(
        self, market_id: Optional[str] = None, party_id: Optional[str] = None
    ):
        pass


@pytest.fixture
def stub_service():
    return StubService("localhost:TEST_WALLET")


## Tests largely meaningless/hard to test now we call CLI directly

# def test_base_service_wallet_creation(stub_service: StubService):
#     with requests_mock.Mocker() as req_mocker:
#         req_mocker.post(
#             WALLET_CREATION_URL.format(wallet_server_url="localhost:TEST_WALLET"),
#             json=lambda req, _: {
#                 "token": req.json()["wallet"] + req.json()["passphrase"]
#             },
#         )
#         req_mocker.post(
#             WALLET_KEY_URL.format(wallet_server_url="localhost:TEST_WALLET"),
#             json=lambda req, _: {
#                 "key": {
#                     "pub": req.json()["passphrase"] + json.dumps(req.json()["meta"])
#                 }
#             },
#         )
#         req_mocker.get(
#             WALLET_KEY_URL.format(wallet_server_url="localhost:TEST_WALLET"),
#             json={"keys": [{"name": "TEST_KEYNAME", "pub": "TEST_PUBLICKEY"}]},
#         )
#         stub_service.create_wallet("TEST_NAME", "TEST_PHRASE")
#         assert stub_service.wallet.login_tokens["TEST_NAME"] == "TEST_NAMETEST_PHRASE"
#         assert (
#             stub_service.wallet.pub_keys["TEST_NAME"]["TEST_KEYNAME"]
#             == "TEST_PUBLICKEY"
#         )


# def test_base_service_wallet_login(stub_service: StubService):
#     with requests_mock.Mocker() as req_mocker:
#         req_mocker.post(
#             WALLET_LOGIN_URL.format(wallet_server_url="localhost:TEST_WALLET"),
#             json=lambda req, _: {
#                 "token": req.json()["wallet"] + req.json()["passphrase"]
#             },
#         )
#         req_mocker.post(
#             WALLET_KEY_URL.format(wallet_server_url="localhost:TEST_WALLET"),
#             json=lambda req, _: {
#                 "key": {
#                     "pub": req.json()["passphrase"] + json.dumps(req.json()["meta"])
#                 }
#             },
#         )
#         req_mocker.get(
#             WALLET_KEY_URL.format(wallet_server_url="localhost:TEST_WALLET"),
#             json={"keys": [{"name": "TEST_KEYNAME", "pub": "TEST_PUBLICKEY"}]},
#         )
#         stub_service.login("TEST_NAME", "TEST_PHRASE")
#         assert stub_service.wallet.login_tokens["TEST_NAME"] == "TEST_NAMETEST_PHRASE"
#         assert (
#             stub_service.wallet.pub_keys["TEST_NAME"]["TEST_KEYNAME"]
#             == "TEST_PUBLICKEY"
#         )
