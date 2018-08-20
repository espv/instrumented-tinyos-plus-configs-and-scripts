cmake_minimum_required(VERSION 3.12)
project(instrumented_tinyos_plus_configs_and_scripts)

set(CMAKE_CXX_STANDARD 14)

add_custom_target(
        Compile-ForwardPacketsAndTraceCSW COMMAND make telosb
        WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/tinyos-main/apps/ForwardPacketsAndTraceCSW
)

add_custom_target(
        Deploy-ForwardPacketsAndTraceCSW-1 COMMAND make telosb install.1
        WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/tinyos-main/apps/ForwardPacketsAndTraceCSW
)

add_custom_target(
        Deploy-ForwardPacketsAndTraceCSW-2 COMMAND make telosb install.2
        WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/tinyos-main/apps/ForwardPacketsAndTraceCSW
)

add_custom_target(
        Deploy-ForwardPacketsAndTraceCSW-3 COMMAND make telosb install.3
        WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/tinyos-main/apps/ForwardPacketsAndTraceCSW
)
