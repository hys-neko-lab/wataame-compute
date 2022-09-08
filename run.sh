trap 'kill $(jobs -p)' EXIT
python3 initserver.py &
python3 rpcserver.py &
wait