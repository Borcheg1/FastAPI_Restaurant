#!/bin/sh -ex

celery -A src.task.config beat -l debug &
celery -A src.task.config worker -l info &
tail -f /dev/null
