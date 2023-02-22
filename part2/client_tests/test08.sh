# Test 03 - Test account creation
# A - Creates an account
# B - Lists accounts and sees A
# B - Sends a message to A
# A - Logs in and sees B's message then deletes account
# B - Lists accounts and does not see A
# B - Tries to send a message to A, fails

TEST_NUM=08
TEST_NAME=account_deletion

source ./_utils.sh

start_server

make_person alice
make_person bob

fg_client $TEST_NUM B
fg_client $TEST_NUM A
fg_client $TEST_NUM B2

sleep 1

stop_server

clientA_result=$(verify_client_contains $TEST_NUM A "hello!")
clientB_result=$(verify_client_output $TEST_NUM B)
clientB2_result=$(verify_client_output $TEST_NUM B2)

if [ $clientA_result -eq 1 ] && [ $clientB_result -eq 1 ] && [ $clientB2_result -eq 1 ]
then
    passed $TEST_NUM $TEST_NAME
else
    failed $TEST_NUM $TEST_NAME
fi

