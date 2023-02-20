# Test 02 - Test that multiple clients can connect to the server

TEST_NUM=02

source ./_utils.sh

start_server $TEST_NUM

bg_client $TEST_NUM A 10
sleep 1
bg_client $TEST_NUM B 10
sleep 1
bg_client $TEST_NUM C 10
sleep 1
bg_client $TEST_NUM D 10

sleep 2

stop_clients
stop_server

server_result=$(verify_server_output $TEST_NUM)

if [ $server_result -eq 1 ]
then
    passed $TEST_NUM
else
    failed $TEST_NUM
fi

