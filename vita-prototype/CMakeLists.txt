cmake_minimum_required(VERSION 3.18)
if(NOT DEFINED ENV{VITASDK})
  message(FATAL_ERROR "Set VITASDK to the pinned SDK directory; see docs/prototypes/vita.md")
endif()
set(VITASDK "$ENV{VITASDK}")
set(CMAKE_TOOLCHAIN_FILE "${VITASDK}/share/vita.toolchain.cmake" CACHE FILEPATH "Vita toolchain")
project(stt_vita_prototype C)
include("${VITASDK}/share/vita.cmake" REQUIRED)
add_executable(stt_vita_prototype src/main.c src/control.c src/render.c src/snapshot.c src/asset.c src/weapon.c ../pose-runtime/stt_pose.c
  ../combat-lab/src/stt_combat.c ../contracts/stt_play.c)
target_include_directories(stt_vita_prototype PRIVATE src ../combat-lab/include ../contracts ../pose-runtime)
set_property(TARGET stt_vita_prototype PROPERTY C_STANDARD 99)
target_compile_options(stt_vita_prototype PRIVATE -O2 -Wall -Wextra -Werror)
target_link_libraries(stt_vita_prototype m SceCtrl_stub SceDisplay_stub ScePower_stub)
vita_create_self(stt_vita_prototype.self stt_vita_prototype)
# Separate identity: NEVER replace STTM00001 (STT Vita Monitor).
vita_create_vpk(stt_vita_prototype.vpk STTP00001 stt_vita_prototype.self
  VERSION 00.13 NAME "STT Vita Prototype"
  FILE assets/hunter-body.pose.json assets/hunter-body.pose.json
  FILE assets/quaternius-sword.pose.json assets/quaternius-sword.pose.json
  FILE assets/QUATERNIUS-NOTICE.txt assets/QUATERNIUS-NOTICE.txt)
