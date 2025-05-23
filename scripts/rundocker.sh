#!/bin/bash
if [[ -z "$1" ]]; then
  export CONTAINER_NAME="compute"
else
  export CONTAINER_NAME=$1
fi
# docker exec -it compute bash
DJ_DIR=dj_sd
docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME
docker run -id --rm --name $CONTAINER_NAME --network host \
      -v $HOME/$DJ_DIR:/$DJ_DIR --workdir /$DJ_DIR djsd:latest bash
