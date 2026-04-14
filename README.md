## A simulation environment for an autonomous weed detection and spraying drone


docker ps --format 'table {{.ID}}\t{{.Image}}\t{{.Names}}'

docker stop <container_id>

xhost +local:docker
docker run --rm -it --privileged \
  --network host \
  -e DISPLAY=$DISPLAY \
  -e PX4_SIM_MODEL=gz_x500 \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  px4io/px4-sitl-gazebo:latest
  