# Test 05 - Test list
# A - Tries to list accounts without logging in first
# A - Logs in as alice
# A - Lists accounts using wildcard "" first page (alice, bob, carson, dave)
# A - Lists accounts using wildcard "" second page (empty)
# A - Lists accounts using wildcard "a" first page (alice, dave, carson)
# A - Lists accounts using wildcard "alice" first page (alice)
# A - Lists accounts using wildcard "eve" first page (empty)
# E - Creates a fifth account, "eve"
# E - Lists accounts using wildcard "" first page (alice, bob, carson, dave)
# E - Lists accounts using wildcard "" second page (eve)
# E - Lists accounts using wildcard "eve" first page (eve)

TEST_NUM=05

source ./_utils.sh

start_server
make_person alice
make_person bob
make_person carson
make_person dave

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

