# Test 02 - Test that multiple clients can connect to the server

TEST_NUM=02

source ./_utils.sh

start_server $TEST_NUM

bg_client $TEST_NUM A 6
sleep 0.5
bg_client $TEST_NUM B 6
sleep 0.5
bg_client $TEST_NUM C 6
sleep 0.5
bg_client $TEST_NUM D 6
sleep 0.5

stop_clients
sleep 1
stop_server
sleep 1


server_result=$(verify_server_output $TEST_NUM trim_newlines)

if [ $server_result -eq 1 ]
then
    passed $TEST_NUM
else
    failed $TEST_NUM
fi

