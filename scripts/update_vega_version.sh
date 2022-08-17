current_env=`cat .env`
vega_tag=`git ls-remote https://github.com/vegaprotocol/vega HEAD | awk '{ print substr($1,1,10) }'`
echo "VEGA_SIM_VEGA_TAG=${vega_tag}
VEGA_SIM_CONSOLE_TAG=master" > .env

make
poetry run pytest
if [ "$?" == 0 ]
then
    echo "Test run successful, keeping updated versions"
    sed -i "s/defaultValue: '[^']*'/defaultValue: '${vega_tag}'/g" Jenkinsfile
else
    echo "Test run failed, reverting to previous versions"
    echo "$current_env" > .env
fi
