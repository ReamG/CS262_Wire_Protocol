# Test 03 - Test account creation
# A - Creates an account
# A - Tests that you can only create one account per client
# B - Tries to create an account with a username that's already taken
# B - Tries to create an account with a username that's empty
# B - Tries to create an account with a username that's too long
# B - Creates a second account

# NOTE: The server is not killed after this test

TEST_NUM=03

source ./_utils.sh

start_server $TEST_NUM

fg_client $TEST_NUM A 10
fg_client $TEST_NUM B 10

sleep 2

stop_server

clientA_result=$(verify_client_output $TEST_NUM A)
clientB_result=$(verify_client_output $TEST_NUM B)

if [ $clientA_result -eq 1 ] && [ $clientB_result -eq 1 ]
then
    passed $TEST_NUM
else
    failed $TEST_NUM
fi

