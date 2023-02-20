
RED='\033[41m'
GREEN='\033[42m'
NC='\033[0m'
# Green background

clients=""

# Start the server (in the background)
function start_server() {
    python3 -u ../server.py > ./output/$1_server.out &
    SERVER_PID=$!
    sleep 1
    disown
}

# Kill the server
function stop_server() {
    kill -15 $SERVER_PID
}

# Start a foreground client
function fg_client() {
    python3 ../client.py < ./input/$1$2_client.in > ./output/$1$2_client.out
}

# $1 is the test number
# $2 is the client letter
# $3 is the number of seconds between lines
function bg_client() {
    while read line
    do
        sleep $3
        echo $line
    done < ./input/$1$2_client.in | python3 ../client.py > ./output/$1$2_client.out &
    #cat ./input/$1$2_client.in | pv --quiet --line-mode --rate-limit 1 | python3 ../client.py > ./output/$1$2_client.out &
    clients+="$! "
    disown
}

# Kill all background clients
function stop_clients() {
    for client in "$clients"
    do
        kill -15 $client
    done
    clients=()
}

# $1 is the test number
# $2 is the client letter
function verify_client_output() {
    # Check that the client output matches the expected output
    if ! cmp -s ./output/$1$2_client.out ./expected/$1$2_client.exp
    then
        echo 0
    else
        echo 1
    fi
}

# $1 is the test number
function verify_server_output() {
    # Check that the client output matches the expected output
    if ! cmp -s ./output/$1_server.out ./expected/$1_server.exp
    then
        echo 0
    else
        echo 1
    fi
}

function passed() {
    printf "Test $1 - ${GREEN}PASS${NC}\n"
}

function failed() {
    printf "Test $1 - ${RED}FAIL${NC}\n"
}