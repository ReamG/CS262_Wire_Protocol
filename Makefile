freeze:
	pip3 freeze > requirements.txt

server:
	python3 server.py

client:
	python3 client.py

generate:
	python3 -m grpc_tools.protoc -I=. --python_out=. --pyi_out=. --grpc_python_out=. ./part2/schema.proto
