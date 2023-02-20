# Test 01 - Test that the server and client can both start and communicate

TEST_NUM=01

source ./_utils.sh

start_server $TEST_NUM

run_client $TEST_NUM

stop_server

client_result=$(verify_client_output $TEST_NUM)
server_result=$(verify_server_output $TEST_NUM)

if [ $client_result -eq 1 ] && [ $server_result -eq 1 ]
then
    passed $TEST_NUM
else
    failed $TEST_NUM
fi
