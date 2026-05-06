function(download_pybind11)
  include(FetchContent)

  set(KALDIALIGN_PYBIND11_URL
    "https://github.com/pybind/pybind11/archive/refs/tags/v3.0.4.tar.gz"
    CACHE STRING "URL used to fetch pybind11 when it is not installed."
  )
  set(KALDIALIGN_PYBIND11_HASH
    "SHA256=74b6a2c2b4573a400cafb6ecbf60c98df300cd3d0041296b913d02b2cbbb2676"
    CACHE STRING "Hash for KALDIALIGN_PYBIND11_URL."
  )

  set(pybind11_url_hash_args)
  if(KALDIALIGN_PYBIND11_HASH)
    list(APPEND pybind11_url_hash_args URL_HASH ${KALDIALIGN_PYBIND11_HASH})
  endif()

  FetchContent_Declare(pybind11
    URL               ${KALDIALIGN_PYBIND11_URL}
    ${pybind11_url_hash_args}
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE
  )

  FetchContent_GetProperties(pybind11)
  if(NOT pybind11_POPULATED)
    message(STATUS "Downloading pybind11 ${KALDIALIGN_PYBIND11_URL}")
    FetchContent_Populate(pybind11)
  endif()
  message(STATUS "pybind11 is downloaded to ${pybind11_SOURCE_DIR}")
  add_subdirectory(${pybind11_SOURCE_DIR} ${pybind11_BINARY_DIR} EXCLUDE_FROM_ALL)
endfunction()

function(find_installed_pybind11)
  if(NOT DEFINED PYTHON_EXECUTABLE AND DEFINED Python_EXECUTABLE)
    set(PYTHON_EXECUTABLE "${Python_EXECUTABLE}")
  endif()

  if(NOT DEFINED PYTHON_EXECUTABLE)
    find_package(Python COMPONENTS Interpreter QUIET)
    if(Python_Interpreter_FOUND)
      set(PYTHON_EXECUTABLE "${Python_EXECUTABLE}")
      set(PYTHON_EXECUTABLE "${Python_EXECUTABLE}" PARENT_SCOPE)
    endif()
  endif()

  if(DEFINED PYTHON_EXECUTABLE)
    execute_process(
      COMMAND "${PYTHON_EXECUTABLE}" -m pybind11 --cmakedir
      RESULT_VARIABLE pybind11_cmakedir_status
      OUTPUT_VARIABLE pybind11_cmakedir
      ERROR_QUIET
      OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    if(pybind11_cmakedir_status EQUAL 0)
      set(pybind11_DIR "${pybind11_cmakedir}" PARENT_SCOPE)
    endif()
  endif()
endfunction()

find_installed_pybind11()
find_package(pybind11 3.0.4 CONFIG QUIET)
if(NOT pybind11_FOUND)
  download_pybind11()
endif()
