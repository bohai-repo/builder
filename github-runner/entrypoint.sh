#!/bin/sh


personal(){
    if [ -n "${ADDITIONAL_PACKAGES}" ]; then
    TO_BE_INSTALLED=$(echo ${ADDITIONAL_PACKAGES} | tr "," " " )
    echo "Installing additional packages: ${TO_BE_INSTALLED}"
    sudo apt-get update && sudo apt-get install -y ${TO_BE_INSTALLED} && sudo apt-get clean
    fi

    if [ ${RUNNER_LABELS} == '' ];then
        RUNNER_LABELS=$(hostname)
    fi

    registration_url="https://github.com/${GITHUB_OWNER}"
    token_url="https://api.github.com/orgs/${GITHUB_OWNER}/actions/runners/registration-token"

    if [ -n "${GITHUB_TOKEN}" ]; then
        echo "Using given GITHUB_TOKEN"

        if [ -z "${GITHUB_REPOSITORY}" ]; then
            echo "When using GITHUB_TOKEN, the GITHUB_REPOSITORY must be set"
            return
        fi

        registration_url="https://github.com/${GITHUB_OWNER}/${GITHUB_REPOSITORY}"
        export RUNNER_TOKEN=$GITHUB_TOKEN

    else
        if [ -n "${GITHUB_REPOSITORY}" ]; then
            token_url="https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPOSITORY}/actions/runners/registration-token"
            registration_url="${registration_url}/${GITHUB_REPOSITORY}"
        fi

        echo "Requesting token at '${token_url}'"

        payload=$(curl -sX POST -H "Authorization: token ${GITHUB_PAT}" ${token_url})
        export RUNNER_TOKEN=$(echo $payload | jq .token --raw-output)

    fi

    if [ -z "${RUNNER_NAME}" ]; then
        RUNNER_NAME=$(hostname)
    fi

    ./config.sh \
        --name "${RUNNER_NAME}" \
        --token "${RUNNER_TOKEN}" \
        --url "${registration_url}" \
        --work "${RUNNER_WORKDIR}" \
        --labels "${RUNNER_LABELS}" \
        --unattended \
        --replace
}

organizational(){
    export registration_url="https://github.com/${GITHUB_ORG_NAME}"
    export token_url="https://api.github.com/orgs/${GITHUB_ORG_NAME}/actions/runners/registration-token"
    export payload=$(curl -sX POST -H "Authorization: token ${GITHUB_PAT}" ${token_url})
    export RUNNER_TOKEN=$(echo $payload | jq .token --raw-output)

    if [ -z "${RUNNER_NAME}" ]; then
        RUNNER_NAME=$(hostname)
    fi

    if [ ${RUNNER_LABELS} == '' ];then
        RUNNER_LABELS=$(hostname)
    fi

    ./config.sh --unattended --url https://github.com/${GITHUB_ORG_NAME} --token ${RUNNER_TOKEN} --labels "${RUNNER_LABELS}"
}

if [ ${REGIST_TYPE} == 'personal' ];then
    personal
elif [ ${REGIST_TYPE} == 'organizational' ];then
    organizational
else
    personal
fi

remove() {
    if [ -n "${GITHUB_RUNNER_TOKEN}" ]; then
        export REMOVE_TOKEN=$GITHUB_RUNNER_TOKEN
    else
        payload=$(curl -sX POST -H "Authorization: token ${GITHUB_PAT}" ${token_url%/registration-token}/remove-token)
        export REMOVE_TOKEN=$(echo $payload | jq .token --raw-output)
    fi

    ./config.sh remove --unattended --token "${RUNNER_TOKEN}"
}

trap 'remove; exit 130' INT
trap 'remove; exit 143' TERM

./runsvc.sh "$*" &

wait $!