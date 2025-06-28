#!/bin/bash

set -e

CURR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_ROOT="$(dirname ${CURR_DIR})"
DOCKERFILE="Dockerfile"
NAME="agent-app"
TAG="dev"

echo "Running: docker build -t ${NAME}:${TAG} -f ${DOCKERFILE} ${WS_ROOT}"
docker build -t ${NAME}:${TAG} -f ${DOCKERFILE} ${WS_ROOT}
