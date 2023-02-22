# Test 04 - Test login
# A - Logs in to an account
# A - Tests that you can only log in to one account per client session
# B - Tries to log into an account that already has an active session
# B - Tries to log in with an empty username
# B - Tries to log in to a non-existent user
# B - Logs in as bob

# NOTE: Assumes the server is still running from test 03
# NOTE: The padding on client in is to make sure it stalls long enough
# to still be logged in when B tries to double up

TEST_NUM=04
TEST_NAME=login

source ./_utils.sh

start_server
make_person alice
make_person bob

bg_client $TEST_NUM A 1
sleep 4
fg_client $TEST_NUM B

sleep 1

stop_clients
sleep 1
stop_server

clientA_result=$(verify_client_output $TEST_NUM A)
clientB_result=$(verify_client_output $TEST_NUM B)

if [ $clientA_result -eq 1 ] && [ $clientB_result -eq 1 ]
then
    passed $TEST_NUM $TEST_NAME
else
    failed $TEST_NUM  $TEST_NAME
fi

