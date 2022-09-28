if("x${CMAKE_SOURCE_DIR}" STREQUAL "x${CMAKE_BINARY_DIR}")
  message(FATAL_ERROR "\
In-source build is not a good practice.
Please use:
  mkdir build
  cd build
  cmake ..
to build this project"
  )
endif()

cmake_minimum_required(VERSION 3.8 FATAL_ERROR)

project(kaldialign CXX)

set(KALDIALIGN_VERSION "0.4")

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

list(APPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake)
include(pybind11)

pybind11_add_module(_kaldialign
  ./extensions/kaldi_align.cpp
  ./extensions/kaldialign.cpp
)

if(UNIX AND NOT APPLE)
  target_link_libraries(_kaldialign PUBLIC ${PYTHON_LIBRARY})
elseif(WIN32)
  target_link_libraries(_kaldialign PUBLIC ${PYTHON_LIBRARIES})
endif()

install(TARGETS _kaldialign
  DESTINATION ../
)
