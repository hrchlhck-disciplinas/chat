build:
	docker build -t hrchlhck/data-hiding:client -f Dockerfile.client . 
	docker build -t hrchlhck/data-hiding:server -f Dockerfile.server .

server:
	docker run -it -p 8888:8888/tcp --rm --env-file=.env hrchlhck/data-hiding:server

client:
	docker run -it --env-file=.env hrchlhck/data-hiding:client
