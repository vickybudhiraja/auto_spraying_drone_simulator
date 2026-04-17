# A simulation environment for an autonomous weed detection and spraying drone


docker ps --format 'table {{.ID}}\t{{.Image}}\t{{.Names}}'

docker stop <container_id>

xhost +local:docker
docker run --rm -it --privileged \
  --network host \
  -e DISPLAY=$DISPLAY \
  -e PX4_SIM_MODEL=gz_x500 \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  px4io/px4-sitl-gazebo:latest


   ### With camera module:

  docker run --rm -it --privileged \
  --network host \
  -e DISPLAY=$DISPLAY \
  -e PX4_SIM_MODEL=gz_x500_mono_cam_down \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  px4io/px4-sitl-gazebo:latest

  ### With terrain image:
    xhost +local:docker

    docker run --rm -it --privileged \
    --network host \
    -e DISPLAY=$DISPLAY \
    -e PX4_SIM_MODEL=gz_x500_mono_cam_down \
    -e PX4_GZ_WORLD=real_patch \
    -e PX4_HOME_LAT=28.539171751544192 \
    -e PX4_HOME_LON=77.2400333478031 \ 
    -e PX4_HOME_ALT=0 \
    -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
    -v "/media/vicky/data/MyTraining/auto_spraying_drone_simulator/myworld:/opt/px4-gazebo/share/gz/worlds:ro" \
    px4io/px4-sitl-gazebo:latest

  ### With DEM AW3D30 terrain
    xhost +local:docker

    docker run --rm -it --privileged \
    --network host \
    -e DISPLAY=$DISPLAY \
    -e PX4_SIM_MODEL=gz_x500_mono_cam_down \
    -e PX4_GZ_WORLD=real_terrain \
    -e PX4_HOME_LAT=28.613333333325453 \
    -e PX4_HOME_LON=77.27694444448068 \
    -e PX4_HOME_ALT=0 \
    -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
    -v "/media/vicky/data/MyTraining/auto_spraying_drone_simulator/myworld:/opt/px4-gazebo/share/gz/worlds:ro" \
    px4io/px4-sitl-gazebo:latest  


  ### headless run
docker run --rm -it --privileged \
  --network host \
  -e HEADLESS=1 \
  -e PX4_SIM_MODEL=gz_x500_mono_cam_down \
  -e PX4_GZ_WORLD=real_terrain_fixed \
  -e PX4_HOME_LAT=28.613333333325453 \
  -e PX4_HOME_LON=77.27694444448068 \
  -e PX4_HOME_ALT=0 \
  -v "/media/vicky/data/MyTraining/auto_spraying_drone_simulator/myworld:/opt/px4-gazebo/share/gz/worlds:ro" \
  px4io/px4-sitl-gazebo:latest

### Starting the image bridge
source /opt/ros/jazzy/setup.bash
ros2 run ros_gz_bridge parameter_bridge \
  /world/default/model/x500_mono_cam_down_0/link/camera_link/sensor/camera/image@sensor_msgs/msg/Image@gz.msgs.Image

Refer: [Use ROS 2 to interact with Gazebo](https://gazebosim.org/docs/latest/ros2_integration/)







docker run --rm -it --privileged \
  --network host \
  -e HEADLESS=1 \
  -e PX4_SIM_MODEL=gz_x500_mono_cam_down \
  -e PX4_GZ_WORLD=real_terrain_mesh \
  -e PX4_HOME_LAT=28.613333333325453 \
  -e PX4_HOME_LON=77.27694444448068 \
  -e PX4_HOME_ALT=0 \
  -v "/media/vicky/data/MyTraining/auto_spraying_drone_simulator/myworld:/opt/px4-gazebo/share/gz/worlds:ro" \
  px4io/px4-sitl-gazebo:latest


  docker run --rm -it   --network host   --gpus all   -e DISPLAY=$DISPLAY   -e NVIDIA_VISIBLE_DEVICES=all   -e NVIDIA_DRIVER_CAPABILITIES=all   -e PX4_SIM_MODEL=gz_x500_mono_cam_down   -e PX4_GZ_WORLD=real_terrain   -e PX4_HOME_LAT=28.613333333325453   -e PX4_HOME_LON=77.27694444448068   -e PX4_HOME_ALT=0   -v /tmp/.X11-unix:/tmp/.X11-unix:ro   -v "/media/vicky/data/MyTraining/auto_spraying_drone_simulator/myworld:/opt/px4-gazebo/share/gz/worlds:ro"   px4io/px4-sitl-gazebo:latest 
