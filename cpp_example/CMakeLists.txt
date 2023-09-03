cmake_minimum_required(VERSION 3.10)
project(SocketProgramming)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

include_directories(include)

add_executable(Server src/server.cpp src/server_main.cpp)
add_executable(Client src/client.cpp src/client_main.cpp)
