```shell


# Vega-market-sim


cd /home/daniel/www/vega
go build -o /home/daniel/www/vega-market-sim/vega_sim/bin/vega ./cmd/vega/

cd /home/daniel/www/vega-market-sim/
poetry run pytest -s -v -m integration --log-cli-level INFO -k test_update_market_instrument



/tmp/vega-sim-tvraqt9c
/tmp/vega-sim-flr7pdrd
/tmp/vega-sim-elhvl46o


cd /home/daniel/www/vega
go build -o /home/daniel/www/vega-market-sim/vega_sim/bin/vega ./cmd/vega/

cd /home/daniel/www/vega-market-sim/
poetry run pytest -s -v -m integration --log-cli-level INFO -k 'test_devops_scenarios[ETHUSD]' 



https://github.com/vegaprotocol/jenkins-shared-library/commit/21bb850335682f0eb1568a3022d9f3d633952a76

wget https://github.com/vegaprotocol/vega/releases/download/v0.71.6/vegawallet-darwin-amd64.zip

export VEGA_WALLET_PATH=/home/daniel/www/vega-market-sim/tmp/vegawallet
export VEGA_USER_WALLET_NAME=vegamarketsim
export VEGA_WALLET_TOKENS_PASSPHRASE_FILE=$(pwd)/wallet-passphrase.txt
export VEGA_WALLET_TOKENS_FILE=$(pwd)/wallet-info.json

echo -n "123456789" > ./wallet-passphrase.txt

make networks

/home/daniel/www/vega-market-sim/tmp/vegawallet create \
  --wallet vegamarketsim \
  --output=json \
  --passphrase-file ./wallet-passphrase.txt > wallet-create.json

/home/daniel/www/vega-market-sim/tmp/vegawallet api-token init \
  --output=json \
  --passphrase-file ./wallet-passphrase.txt > api-token-init.json

/home/daniel/www/vega-market-sim/tmp/vegawallet api-token generate \
  --wallet-name vegamarketsim \
  --wallet-passphrase-file  ./wallet-passphrase.txt \
  --tokens-passphrase-file  ./wallet-passphrase.txt \
  --output=json > api-token-generate.json

export WALLET_TOKEN=$(jq -r '.token' api-token-generate.json)

cat <<EOT > wallet-info.json
{
  "vegamarketsim": "${WALLET_TOKEN}"
}
EOT




/home/daniel/www/vega-market-sim/tmp/vegawallet service run --network mainnet-mirror --load-tokens --tokens-passphrase-file ~/www/vega-market-sim/wallet-passphrase.txt         


vegawallet key generate -w vegamarketsim -m "name:main" --output=json --passphrase-file ./wallet-passphrase.txt > key-generate-main.json
vegawallet key generate -w vegamarketsim -m "name:market_creator" --output=json --passphrase-file ./wallet-passphrase.txt > key-generate-market_creator.json
vegawallet key generate -w vegamarketsim -m "name:market_settler" --output=json --passphrase-file ./wallet-passphrase.txt > key-generate-market_settler.json
vegawallet key generate -w vegamarketsim -m "name:auction_trader_a" --output=json --passphrase-file ./wallet-passphrase.txt > key-generate-auction_trader_a.json
vegawallet key generate -w vegamarketsim -m "name:auction_trader_b" --output=json --passphrase-file ./wallet-passphrase.txt > key-generate-auction_trader_b.json
vegawallet key generate -w vegamarketsim -m "name:market_maker" --output=json --passphrase-file ./wallet-passphrase.txt > key-generate-market_maker.json
vegawallet key generate -w vegamarketsim -m "name:random_trader_a" --output=json --passphrase-file ./wallet-passphrase.txt > key-generate-random_trader_a.json
vegawallet key generate -w vegamarketsim -m "name:random_trader_b" --output=json --passphrase-file ./wallet-passphrase.txt > key-generate-random_trader_b.json
vegawallet key generate -w vegamarketsim -m "name:random_trader_c" --output=json --passphrase-file ./wallet-passphrase.txt > key-generate-random_trader_c.json
vegawallet key generate -w vegamarketsim -m "name:momentum_trader_a" --output=json --passphrase-file ./wallet-passphrase.txt > key-generate-momentum_trader_a.json
vegawallet key generate -w vegamarketsim -m "name:momentum_trader_b" --output=json --passphrase-file ./wallet-passphrase.txt > key-generate-momentum_trader_b.json
vegawallet key generate -w vegamarketsim -m "name:momentum_trader_c" --output=json --passphrase-file ./wallet-passphrase.txt > key-generate-momentum_trader_c.json
vegawallet key generate -w vegamarketsim -m "name:momentum_trader_d" --output=json --passphrase-file ./wallet-passphrase.txt > key-generate-momentum_trader_d.json
vegawallet key generate -w vegamarketsim -m "name:momentum_trader_e" --output=json --passphrase-file ./wallet-passphrase.txt > key-generate-momentum_trader_e.json
vegawallet key generate -w vegamarketsim -m "name:sensitive_trader_a" --output=json --passphrase-file ./wallet-passphrase.txt > key-generate-sensitive_trader_a.json
vegawallet key generate -w vegamarketsim -m "name:sensitive_trader_b" --output=json --passphrase-file ./wallet-passphrase.txt > key-generate-sensitive_trader_b.json
vegawallet key generate -w vegamarketsim -m "name:sensitive_trader_c" --output=json --passphrase-file ./wallet-passphrase.txt > key-generate-sensitive_trader_c.json
vegawallet key generate -w vegamarketsim -m "name:agent" --output=json --passphrase-file ./wallet-passphrase.txt > key-generate-agent.json

export PARTIES=$(./tmp/vegawallet key list --wallet vegamarketsim --passphrase-file ./wallet-passphrase.txt --output=json | jq -r '[.keys | .[] | .publicKey ] | join(",")')

export PARTIES="9f8b247510cb0b58b97b28bd9750466335703905d8e7a4e8ce6da492a306d9f0,0cbf58755d290f5bdc482d8c2610bc9921ea781efcb80f32a440f9210c3c3782,1d18accbbbdc20eefeddc1de4c2df09788deb4ed639898f80643524d7eb78a30,4adac7c9fe1d80c3a8e5030b50576bd97f880be9a6106f366e5efd8427e30de6,410aee3cdf93064c7fc5c038c29290311c2fd424e91957942cb31b968aab9d06,92affbaa7eb72390840e5cfe70530df273d740d9bbbd88e5e137388da711143e,c3ca61e42c39042be40f49ae84f93beaa9261fcfb7f71b483a9e9771d0630259,ce98299716c78d8d6b401b436f096f2734f187d95a2557ad5a5d01083a2e96f1,61c01eaa68fe08159f596ce1a9b0e26a90a3b1e655927e8c3c170f9161e50f01,d1f30baccbeb8ccf4a464298fec0267ab7661ca0e7dfd58f40d3d251b73a7f84,59e48fbd1beb9288c99fcc6190e9f783c0e8e6b99b04e95df1ebac4990a0016d,0523118a394515c9f777f41dba6dc8332ed5464379017459811b2fbb11cae603,357a9f4baa8797f124a0466fe6a52557190012a4c42020975756cc65eed8d6a7,0d2e19dabaa1113b6720b0b4cacb4321e8265e1a63d6f8fcf50f1c02391ec0e4,779df2b5ecb18fa1921c049e9306e171a7a7e5c06a8accef5ba9110fca3f9f88,98df8b390a1d2acc1aa40db32da1dde6329a49a6cb8e66c18227285ec37b6a8c,c0a23ba0f6fe1edab05eafb19e0499e845bc1f4bebd26ab191a5f91d5870ad3b,0f408f1c007834b9b1d8c693f03127bf4d8430f2de3d30d54760578eebdfd28c,4bab52bbab3c32216b8a2671e8ac905cbd53a05a18e181855cd39efdbac600aa"


go run main.go topup parties --network mainnet-mirror --erc20-token-address 0x973cB2a51F83a707509fe7cBafB9206982E1c3ad --amount 50000 --parties $PARTIES



```