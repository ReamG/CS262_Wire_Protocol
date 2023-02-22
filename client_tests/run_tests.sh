# Runs tests $1 - $2

source ./_utils.sh

for i in $(seq -f "%02g" $1 $2)
do
    source ./test$i.sh
    sleep 1
done
