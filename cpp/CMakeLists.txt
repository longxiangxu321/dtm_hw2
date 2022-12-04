project(hw02)

cmake_minimum_required(VERSION 3.2)


FILE(GLOB SRC_FILES src/*.cpp)
add_executable(hw02 ${SRC_FILES})

set_target_properties(hw02 PROPERTIES CXX_STANDARD 11)

if (WIN32)
    set_property(DIRECTORY PROPERTY VS_STARTUP_PROJECT "hw02")
endif (WIN32)
