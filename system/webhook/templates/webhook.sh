#!/bin/sh

header='Content-Type: application/json'
data='{ "content": "{{ content }}" }'

curl --header "$header" --data "$data" {{ url }}
