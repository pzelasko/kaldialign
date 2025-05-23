if (CMAKE_VERSION VERSION_GREATER_EQUAL "4.0.0")
  set(CMAKE_POLICY_VERSION_MINIMUM 3.5)
endif()
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

# Please remember to also change line 3 of ./scripts/conda/kaldialign/meta.yaml
set(KALDIALIGN_VERSION "0.9.2")

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

list(APPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake)
include(pybind11)

pybind11_add_module(_kaldialign
  ./extensions/kaldi_align.cpp
  ./extensions/kaldialign.cpp
)

install(TARGETS _kaldialign
  DESTINATION ../
)
