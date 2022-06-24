#!/usr/bin/python

import json
import subprocess
import requests

# read the configuration from journal.json
def read_config():
	with open('journal.json') as config: return json.load(config)

# send the message to the discord webhook
def discord_send(url, message):
	payload = {'content': message}
	headers = {'Content-Type': 'application/json'}
	r = requests.post(url, headers = headers, data = json.dumps(payload))
	print(r)

def journal_listen(query):
	print(query['unit'])
	command = ['journalctl', '--unit', query['unit'], '--follow', '--output', 'json']
	print(command)
	with subprocess.Popen(command, stdout = subprocess.PIPE, text = True) as process:
		for line in iter(process.stdout.readline, ""):
			line = json.loads(line)
			message = '`' + line['MESSAGE'] + '`'
			print(message)
			discord_send(query['url'], message)

def main():
	config = read_config()

	# for each query in the config, listen for the query
	for query in config:
		journal_listen(query)

main()
