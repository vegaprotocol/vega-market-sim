import json
import pytest
import requests_mock

from vega_sim.service import VegaService
from vega_sim.api.wallet import WALLET_CREATION_URL, WALLET_KEY_URL, WALLET_LOGIN_URL


class StubService(VegaService):
    def __init__(self, wallet_url: str, data_url: str, faucet_url: str):
        super().__init__()
        self.wallet_url_str = wallet_url
        self.data_url_str = data_url
        self.faucet_url_str = faucet_url

    def wallet_url(self) -> str:
        return self.wallet_url_str

    def data_node_rest_url(self) -> str:
        return self.data_url_str

    def faucet_url(self) -> str:
        return self.faucet_url_str


@pytest.fixture
def stub_service():
    return StubService(
        "localhost:TEST_WALLET", "localhost:TEST_DATA", "localhost:TEST_FAUCET"
    )


def test_base_service_wallet_creation(stub_service: StubService):
    with requests_mock.Mocker() as req_mocker:
        req_mocker.post(
            WALLET_CREATION_URL.format(wallet_server_url="localhost:TEST_WALLET"),
            json=lambda req, _: {
                "token": req.json()["wallet"] + req.json()["passphrase"]
            },
        )
        req_mocker.post(
            WALLET_KEY_URL.format(wallet_server_url="localhost:TEST_WALLET"),
            json=lambda req, _: {
                "key": {
                    "pub": req.json()["passphrase"] + json.dumps(req.json()["meta"])
                }
            },
        )
        stub_service.create_wallet("TEST_NAME", "TEST_PHRASE")
        assert stub_service.login_tokens["TEST_NAME"] == "TEST_NAMETEST_PHRASE"
        assert (
            stub_service.pub_keys["TEST_NAME"] == 'TEST_PHRASE[{"name": "default_key"}]'
        )


def test_base_service_wallet_login(stub_service: StubService):
    with requests_mock.Mocker() as req_mocker:
        req_mocker.post(
            WALLET_LOGIN_URL.format(wallet_server_url="localhost:TEST_WALLET"),
            json=lambda req, _: {
                "token": req.json()["wallet"] + req.json()["passphrase"]
            },
        )
        req_mocker.post(
            WALLET_KEY_URL.format(wallet_server_url="localhost:TEST_WALLET"),
            json=lambda req, _: {
                "key": {
                    "pub": req.json()["passphrase"] + json.dumps(req.json()["meta"])
                }
            },
        )
        stub_service.login("TEST_NAME", "TEST_PHRASE")
        assert stub_service.login_tokens["TEST_NAME"] == "TEST_NAMETEST_PHRASE"
        assert (
            stub_service.pub_keys["TEST_NAME"] == 'TEST_PHRASE[{"name": "default_key"}]'
        )
