# Test 06 - Send immediately
# B - Sends "hello" to alice
# A - Sends "hello" to bob

TEST_NUM=05

source ./_utils.sh

start_server
make_person alice
make_person bob

fg_client $TEST_NUM A
fg_client $TEST_NUM E

stop_server

clientA_result=$(verify_client_output $TEST_NUM A)
clientE_result=$(verify_client_output $TEST_NUM E)

if [ $clientA_result -eq 1 ] && [ $clientE_result -eq 1 ]
then
    passed $TEST_NUM
else
    failed $TEST_NUM
fi

