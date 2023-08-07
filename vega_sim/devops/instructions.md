```shell


# Vega-market-sim


cd /Users/daniel/www/vega/vega
go build -o /Users/daniel/www/vega/vega-market-sim/vega_sim/bin/vega ./cmd/vega/

cd /Users/daniel/www/vega/vega-market-sim/
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

export VEGA_WALLET_PATH=/Users/daniel/www/vega/vega-market-sim/tmp/vegawallet
export VEGA_USER_WALLET_NAME=vegamarketsim
export VEGA_WALLET_TOKENS_PASSPHRASE_FILE=$(pwd)/wallet-passphrase.txt
export VEGA_WALLET_TOKENS_FILE=$(pwd)/wallet-info.json

echo -n "123456789" > ./wallet-passphrase.txt

make networks

/Users/daniel/www/vega/vega-market-sim/tmp/vegawallet create \
  --wallet vegamarketsim \
  --output=json \
  --passphrase-file ./wallet-passphrase.txt > wallet-create.json

/Users/daniel/www/vega/vega-market-sim/tmp/vegawallet api-token init \
  --output=json \
  --passphrase-file ./wallet-passphrase.txt > api-token-init.json

/Users/daniel/www/vega/vega-market-sim/tmp/vegawallet api-token generate \
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


e7fb35296f5c0dfca3a22a74adf0b171f35140aa4f8cc8da6414c7b90b0fae86,c1bc5a040cd1689e9f2734da0b50d630a643743ef1c5924c7752fb7c5d093ed7,84e60ddcdd178f6b2d4417e168b4496fff39a5f6c19d3026dd368bd33cae5892,6a6f8f077868d704076ace4464916790c23aa7a22296fade5cd87f74c7dede0f,9c3e28bc6f7a4d521dce8cde8aab7c5598583be7c8d90fda08f5b86be2601a99,dca6ef3758d80c16666596dd54294636905c957fa077e5b340d1263738aa6f54,cf56b071daa4fb6f37b8b28af9eb1f3b9fa6cc4bff5221aaedb32d087a0aa880,1fd013bd62c2cb4b71f4311a90c45251a14304cda1bad3cd99e2a6e382c2ddc1,d7092bab28b4cbd2f478e87a600fdb7f06e1e21db8ceacd1d071f56a06b7a81d,6957610c068d2a7b6e4d41da326672e3c5772c115884c827c8535931b927be7c,ef08760e7d1740da60b6566f4eddfb886e55689f4f3b607f191702c80e18c533,ff96e0954ed7d6bcfbb275595710c2dfbe1118aad0c16a8e74f664d7f7096def,f460760cc368477e1202b34abf4ca7f0a31386a5d0dba080c407df6b3410c648,ed631a6be07a909cdd330cb09b4c85f6c5af68d09168aca6d53b3167c0bae8ff,8e59e66cf12d72ef358a8db2e8545e227fd7358afece3ab60a136d62029ffbd5,3c10c378f1547b3aecfda149339d606157959b3c7da06d3ca504a7b157b30e01,1f00777e026a7ed68e2fa9b411301cb29f66ac3d771276288ea6d7991e49546a,aaf69da01eb054207cf8ca5d705694e3c3c93d52172d035ada4bf2968c59f613,db2f6cab4afd3fb98df643014fde613f2ffb13601630d55c4fc3d7a0cf961d3f


go run main.go topup parties --network mainnet-mirror --erc20-token-address 0x973cB2a51F83a707509fe7cBafB9206982E1c3ad --amount 50000 --parties $PARTIES



```