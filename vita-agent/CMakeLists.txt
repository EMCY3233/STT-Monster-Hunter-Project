cmake_minimum_required(VERSION 3.18)
if(NOT DEFINED ENV{VITASDK})
  message(FATAL_ERROR "Set VITASDK to the installed SDK directory")
endif()
set(VITASDK "$ENV{VITASDK}")
set(CMAKE_TOOLCHAIN_FILE "${VITASDK}/share/vita.toolchain.cmake" CACHE FILEPATH "Vita toolchain")
project(stt_vita_monitor C)
include("${VITASDK}/share/vita.cmake" REQUIRED)
include(FetchContent)
FetchContent_Declare(vita_samples
  GIT_REPOSITORY https://github.com/vitasdk/samples.git
  GIT_TAG fe8fbef570f3280586c0c20157146e3faefb2181
  SOURCE_SUBDIR stt-no-cmake-subdirectory)
FetchContent_MakeAvailable(vita_samples)
add_executable(stt_vita_monitor src/main.c src/telemetry.c src/recovery.c
  "${vita_samples_SOURCE_DIR}/common/debugScreen.c")
target_include_directories(stt_vita_monitor PRIVATE "${vita_samples_SOURCE_DIR}/common")
set_property(TARGET stt_vita_monitor PROPERTY C_STANDARD 99)
target_compile_options(stt_vita_monitor PRIVATE -Wall -Wextra)
target_link_libraries(stt_vita_monitor SceNet_stub SceNetCtl_stub SceSysmodule_stub SceCtrl_stub
  ScePower_stub SceRtc_stub SceDisplay_stub)
vita_create_self(stt_vita_monitor.self stt_vita_monitor)
# Developer package only; no installation or transfer automation.
vita_create_vpk(stt_vita_monitor.vpk STTM00001 stt_vita_monitor.self
  VERSION 00.40 NAME "STT Vita Monitor")
