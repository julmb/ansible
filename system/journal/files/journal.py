#!/usr/bin/python

import json
import asyncio
import asyncio.subprocess
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

async def journal_listen(query):
	command = ['journalctl', '--unit', query['unit'], '--follow', '--output', 'json']
	process = await asyncio.create_subprocess_exec(*command, stdout = asyncio.subprocess.PIPE)
	lines = []
	while True:
		try:
			print("waiting for line")
			line = await asyncio.wait_for(process.stdout.readline(), 5)
			lines.append(line)
		except asyncio.TimeoutError:
			print("timeout", "collected lines", len(lines))
			lines = []

	# with subprocess.Popen(command, stdout = subprocess.PIPE, text = True) as process:
	# 	while True:
	# 		try: outs, errs = process.communicate(timeout = 5)
	# 		except subprocess.TimeoutExpired: continue
	# 		line = json.loads(line)
	# 		message = '`' + line['MESSAGE'] + '`'
	# 		print(message)
	# 		discord_send(query['url'], message)

def main():
	config = read_config()

	# for each query in the config, listen for the query
	for query in config:
		asyncio.run(journal_listen(query))

main()
