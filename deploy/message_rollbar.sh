#!/bin/bash
set -e

set -a
source /opt/star-burger/.env
set +a

echo "Уведомление Rollbar о деплое..."

REVISION=$(git rev-parse HEAD)
ENVIRONMENT="production"

curl -X POST https://api.rollbar.com/api/1/deploy/ \
  -H "X-Rollbar-Access-Token: $ROLLBAR" \
  -d environment=$ENVIRONMENT \
  -d revision=$REVISION \
  -d local_username=$(whoami)

