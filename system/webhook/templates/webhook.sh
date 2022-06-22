#!/bin/bash

recipient=$4
subject=$3
message=$(cat $1)

header="Content-Type: application/json"
data="{ \"content\": \"recipient: $recipient\nsubject: $subject\nmessage\n${message//$'\n'/\\n}\" }"

curl --silent --header "$header" --data "$data" {{ url }}
