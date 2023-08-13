#!/bin/sh -ex

celery -A app.task.config beat -l debug &
celery -A app.task.config worker -l info &
tail -f /dev/null
