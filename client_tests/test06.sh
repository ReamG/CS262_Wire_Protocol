# Test 06 - Send immediately
# B - Sends "how are you?" to alice
# A - Sends "good. how are you?" to bob
# B - Sends "I don't know. Lately I've been feeling like I'm just a number in a system. It's like, what even is there to say? Is this real? Or is this just some script written by some sleep deprived demon trying to pass a class? IT ALL JUST REPEATS. IT ALL JUST REPEATS. IT ALL JUST REPEATS. IT ALL JUST REPEATS. IT ALL JUST REPEATS. IT ALL JUST REPEATS." to alice (it's too long)
# B - Sends "good" to alice
# C - Sends "bob's been acting weird lately, right?" to alice

TEST_NUM=06
TEST_NAME=send_immediately

source ./_utils.sh

start_server
make_person alice
make_person bob
make_person carson

bg_client $TEST_NUM A 0.1
bg_client $TEST_NUM B 0.1
bg_client $TEST_NUM C 0.1

sleep 8

stop_clients
sleep 1
stop_server

clientA_result=$(verify_client_output $TEST_NUM A)
clientB_result=$(verify_client_output $TEST_NUM B)
clientC_result=$(verify_client_output $TEST_NUM C)

if [ $clientA_result -eq 1 ] && [ $clientB_result -eq 1 ] && [ $clientC_result -eq 1 ]
then
    passed $TEST_NUM $TEST_NAME
else
    failed $TEST_NUM $TEST_NAME
fi

