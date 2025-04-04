docker image ls

docker build -t leskoiam/openairelay:0.0.4 .
docker image ls

docker tag leskoiam/openairelay:0.0.4 leskoiam/openairelay:latest
docker image ls

docker push leskoiam/openairelay:0.0.4
docker push leskoiam/openairelay:latest