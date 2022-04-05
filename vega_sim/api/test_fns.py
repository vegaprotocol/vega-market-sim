import os
import sys
import requests
import time

from vega_sim.service import VegaService


def propose_market(
    wallet_name,
    wallet_passphrase,
    pubkey,
    term_pubkey,
    node_url_rest,
    wallet_server_url,
    vega_service: VegaService,
):

    """
    Propose a market by user {wallet_name} on the node {node_url_rest}.
    """

    # Login wallet
    req = {"wallet": wallet_name, "passphrase": wallet_passphrase}
    response = requests.post(f"{wallet_server_url}/api/v1/auth/token", json=req)
    token = response.json()["token"]

    assert token != ""
    print(f"Logged in to wallet {wallet_name} successfully.", "\n")
    headers = {"Authorization": f"Bearer {token}"}

    # Make sure Vega network has the settlement asset
    url = f"{node_url_rest}/assets"
    response = requests.get(url)
    # Find settlement asset with name tDAI
    tDAI_id = None
    assets = response.json()["assets"]
    for asset in assets:
        if asset["details"]["symbol"] == "tDAI":
            tDAI_id = asset["id"]
            break

    if tDAI_id is None:
        print(
            "tDAI asset not found on specified Vega network, please propose and "
            "create this asset first"
        )
        return

    # Make sure Vega network has governance asset
    vote_asset_id = next(
        (x["id"] for x in assets if x["details"]["symbol"] == "VOTE"), None
    )
    if vote_asset_id is None:
        print(
            "VEGA asset not found on specified Vega network, please symbol name check and try again"
        )
        return

    # Request accounts for party and check governance asset balance
    url = f"{node_url_rest}/parties/{pubkey}/accounts"
    response = requests.get(url)

    voting_balance = 0
    accounts = response.json()["accounts"]
    for account in accounts:
        if account["asset"] == vote_asset_id:
            voting_balance = account["balance"]
            break

    if voting_balance == 0:
        print(f"Please deposit VEGA asset to public key {pubkey} and try again")
        sys.exit(1)

    # Get blockchain time
    # Request the current blockchain time, and convert to time in seconds
    response = requests.get(f"{node_url_rest}/time")
    blockchain_time = int(response.json()["timestamp"])
    blockchain_time_seconds = int(blockchain_time / 1e9)

    assert blockchain_time > 0
    assert blockchain_time_seconds > 0
    print(
        f"Blockchain time: {blockchain_time} ({blockchain_time_seconds} seconds "
        "past epoch)",
        "\n",
    )
    # Propose market
    proposal_ref = f"{pubkey}-IM-A-Market"

    # Set closing/enactment and validation timestamps to valid time offsets
    # from the current Vega blockchain time
    closing_time = blockchain_time_seconds + 360
    enactment_time = blockchain_time_seconds + 480
    validation_time = blockchain_time_seconds + 1

    # The proposal command below contains the configuration for a new market
    proposal = {
        "proposalSubmission": {
            "reference": proposal_ref,
            "terms": {
                "closingTimestamp": closing_time,
                "enactmentTimestamp": enactment_time,
                "validationTimestamp": validation_time,
                "newMarket": {
                    "changes": {
                        "decimalPlaces": 5,
                        "instrument": {
                            "code": "CRYPTO:BTCDAI/DEC22",
                            "future": {
                                "oracleSpecForSettlementPrice": {
                                    "pubKeys": [term_pubkey],
                                    "filters": [
                                        {
                                            "key": {
                                                "name": "price.DAI.value",
                                                "type": "TYPE_INTEGER",
                                            },
                                            "conditions": [],
                                        },
                                    ],
                                },
                                "oracleSpecForTradingTermination": {
                                    "pubKeys": [term_pubkey],
                                    "filters": [
                                        {
                                            "key": {
                                                "name": "trading.terminated",
                                                "type": "TYPE_BOOLEAN",
                                            },
                                            "conditions": [],
                                        },
                                    ],
                                },
                                "oracleSpecBinding": {
                                    "settlementPriceProperty": "price.DAI.value",
                                    "tradingTerminationProperty": "trading.terminated",
                                },
                                "quoteName": "tDAI",
                                "settlementAsset": tDAI_id,
                            },
                            "name": "BTC/DAI (2022, tDAI)",
                        },
                        "metadata": [
                            "base:BTC",
                            "quote:DAI",
                        ],
                        "liquidityMonitoringParameters": {
                            "targetStakeParameters": {
                                "timeWindow": 3600,
                                "scalingFactor": 10,
                            },
                            "triggeringRatio": 0.7,
                            "auctionExtension": 0,
                        },
                        "logNormal": {
                            "riskAversionParameter": 0.01,
                            "tau": 1.90128526884173e-06,
                            "params": {"mu": 0, "r": 0.016, "sigma": 1.5},
                        },
                    },
                    "liquidityCommitment": {
                        "commitmentAmount": "10000",
                        "fee": "0.002",
                        "sells": [
                            {
                                "reference": "PEGGED_REFERENCE_MID",
                                "proportion": 1,
                                "offset": "50",
                            },
                        ],
                        "buys": [
                            {
                                "reference": "PEGGED_REFERENCE_MID",
                                "proportion": 1,
                                "offset": "50",
                            },
                        ],
                        "reference": "",
                    },
                },
            },
        },
        "pubKey": pubkey,
        "propagate": True,
    }
    print("Submit a market proposal: ", proposal)

    # Sign the new market proposal transaction
    url = f"{wallet_server_url}/api/v1/command/sync"
    response = requests.post(url, headers=headers, json=proposal)
    print("Signed market proposal and sent to Vega", "\n")

    response.raise_for_status()

    # Wait for proposal to be included in a block and to be accepted by Vega network
    proposal_id = ""
    done = False
    while not done:
        vega_service.forward("1s")

        time.sleep(0.5)
        print(".", end="", flush=True)
        my_proposals = requests.get(node_url_rest + "/parties/" + pubkey + "/proposals")
        if my_proposals.status_code != 200:
            continue

        for n in my_proposals.json()["data"]:
            if n["proposal"]["reference"] == proposal_ref:
                proposal_id = n["proposal"]["id"]
                print("Your proposal has been accepted by the network", "\n")
                done = True
                break

    assert proposal_id != ""

    # Vote on the market
    # Create a vote message, to vote on the proposal
    vote = {
        "voteSubmission": {
            "value": "VALUE_YES",
            "proposalId": proposal_id,
        },
        "pubKey": pubkey,
        "propagate": True,
    }

    # Sign the vote transaction
    url = f"{wallet_server_url}/api/v1/command/sync"
    response = requests.post(url, headers=headers, json=vote)
    print("Signed vote on proposal and sent to Vega", "\n")

    # Put timeforward by hand in Null blockchain.
    vega_service.forward("480s")

    print("The market has been set up.", "\n")

    return tDAI_id
