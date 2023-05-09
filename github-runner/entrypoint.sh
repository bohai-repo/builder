#!/bin/sh

registration_url="https://github.com/${GITHUB_ORG_NAME}"
token_url="https://api.github.com/orgs/${GITHUB_ORG_NAME}/actions/runners/registration-token"
payload=$(curl -sX POST -H "Authorization: token ${GITHUB_PAT}" ${token_url})
export RUNNER_TOKEN=$(echo $payload | jq .token --raw-output)

if [ -z "${RUNNER_NAME}" ]; then
    RUNNER_NAME=$(hostname)
fi

./config.sh --unattended --url https://github.com/${GITHUB_ORG_NAME} --token ${RUNNER_TOKEN} --labels "${RUNNER_LABELS}"

# 在容器被干掉的时候自动向 GitHub 解除注册 Runner
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