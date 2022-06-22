#!/bin/bash

header="Content-Type: application/json"
data="{ \"content\": \"recipient: $SMARTD_ADDRESS\nsubject: $SMARTD_SUBJECT\nmessage\n${SMARTD_FULLMESSAGE//$'\n'/\\n}\" }"

curl --silent --header "$header" --data "$data" {{ url }}
