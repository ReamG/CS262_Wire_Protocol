# Test 06 - Send on demand
# B - Sends "hey! it's bob" to alice
# C - Sends "carson! carson!" to alice
# D - Sends "dave is sad" to alice
# A - Logs in, should see all these messages delivered on demand in correct order

TEST_NUM=07
TEST_NAME=send_on_demand

source ./_utils.sh

start_server

make_person alice
make_person bob
make_person carson
make_person dave

fg_client $TEST_NUM B
fg_client $TEST_NUM C
fg_client $TEST_NUM D
fg_client $TEST_NUM A

stop_server

receiveB_result=$(verify_client_contains $TEST_NUM A "hey! it's bob")
receiveC_result=$(verify_client_contains $TEST_NUM A "carson! carson!")
receiveD_result=$(verify_client_contains $TEST_NUM A "dave is sad")


if [ $receiveB_result -eq 1 ] && [ $receiveC_result -eq 1 ] && [ $receiveD_result -eq 1 ];
then
    passed $TEST_NUM $TEST_NAME
else
    failed $TEST_NUM $TEST_NAME
fi

