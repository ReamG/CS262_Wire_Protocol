
RED='\033[41m'
GREEN='\033[42m'
NC='\033[0m'
# Green background

clients=""

# Start the server (in the background)
function start_server() {
    python3 -u ../server.py > ./output/$1_server.out &
    SERVER_PID=$!
    disown
    sleep 1
}

# Kill the server
function stop_server() {
    kill -15 $SERVER_PID
}

# Start a foreground client
function fg_client() {
    cat ip.txt ./input/$1$2_client.in | python3 -u ../client.py  > ./output/$1$2_client.out
}

# Helper function to spin up a client that connects to the server and 
# makes one account with uid $1 and then dies
function make_person() {
    ip=$(cat ip.txt)
    echo "$ip\ncreate\n$1" | python3 ../client.py > /dev/null
}

# $1 is the test number
# $2 is the client letter
# $3 is the number of seconds between lines
function bg_client() {
    cat ip.txt ./input/$1$2_client.in | 
    while read line
    do
        echo $line
        sleep $3
    done | python3 -u ../client.py > ./output/$1$2_client.out &
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
    if ! diff -w ./output/$1$2_client.out ./expected/$1$2_client.exp > /dev/null
    then
        echo 0
    else
        echo 1
    fi
}

# $1 is the test number
# $2 is the client letter
# $3 is the expected output
function verify_client_contains() {
    # Check that the client output contains the expected output
    if ! grep -q "$3" ./output/$1$2_client.out
    then
        echo 0
    else
        echo 1
    fi
}

# $1 is the test number
# $2 is how many lines (from top) of the output should match
# NOTE: Because of weird threading stuff, we scrape newlines here
# which mess up the output for weird reasons (which is why we strip whitespace
# and need the extra flexibility to only look at first x lines)
function verify_server_output() {
    scratch_out=./scratch_server.out
    scratch_exp=./scratch_server.exp
    num_lines=${2-100}
    head -n $num_lines ./output/$1_server.out | tr -d "[:space:]" > $scratch_out
    head -n $num_lines ./expected/$1_server.exp | tr -d "[:space:]" > $scratch_exp
    # Check that the client output matches the expected output
    if ! diff -w "$scratch_out" "$scratch_exp" > /dev/null
    then
        echo 0
    else
        echo 1
    fi
    rm "$scratch_out"
    rm "$scratch_exp"
}

# $1 is the test number
# $2 is the test name
function passed() {
    printf "Test $1 ${GREEN}PASS${NC} ($2)\n"
}

function failed() {
    printf "Test $1 ${RED}FAIL${NC} ($2)\n"
}