# The following lines of boilerplate have to be in your project's CMakeLists
# in this exact order for cmake to work correctly
cmake_minimum_required(VERSION 3.5)

list(APPEND EXTRA_COMPONENT_DIRS    
"./driver_user/"
)

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(as5600_dev)
