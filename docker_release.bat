docker image ls

docker build -t leskoiam/openairelay:0.0.1 .
docker image ls

docker tag leskoiam/openairelay:0.0.1 leskoiam/openairelay:latest
docker image ls

docker push leskoiam/openairelay:0.0.1
docker push leskoiam/openairelay:latest