#!/usr/bin/env bash

# Getting dynamic relative path so script can be executed from anywhere.
RELATIVE_PATH=$(dirname ${0})

if [[ "${RELATIVE_PATH}/../sovpn_config_pointer.txt" ]]; then
    POINTER_PATH=$(realpath "${RELATIVE_PATH}/../sovpn_config_pointer.txt")
else
    echo "> Can't find SOVPN configuration file."
    exit 1
fi

which jq 1> /dev/null

if [[ "${?}" != '0' ]]; then
    echo "> You are missing 'jq' command, plase add it to your PATH or install it."
fi

CONFIG_FILE_PATH=$(realpath $(cat "${POINTER_PATH}"))
EASY_RSA_PATH=$(jq .server.easy_rsa_dir ${CONFIG_FILE_PATH} | tr -d '"')

# Changes build-key command to be non-interactive.
if [[ -f "${EASY_RSA_PATH}/build-key" ]]; then
    if [[ ! -f "${EASY_RSA_PATH}/build-key.dist" ]]; then
        cp "${EASY_RSA_PATH}/build-key" "${EASY_RSA_PATH}/build-key.dist"
        sed -i 's/ --interact//g' "${EASY_RSA_PATH}/build-key" 
    fi
fi

