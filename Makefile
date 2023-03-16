build:
	docker build -t vpemfh7/data-hiding:client -f Dockerfile.client .; docker build -t vpemfh7/data-hiding:server -f Dockerfile.server .

run_server:
	docker run -it -p 8888:8888/tcp -p 8889:8889/udp --rm --env-file=.env vpemfh7/data-hiding:server

run_client:
	docker run -it --rm --env-file=.env vpemfh7/data-hiding:client