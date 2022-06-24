#!/usr/bin/python

import asyncio, json, requests

# read the configuration from journal.json
def read_config():
	with open('journal.json') as config: return json.load(config)

def discord(url, entries):
	message = '```'
	for entry in entries:
		message += entry['MESSAGE'] + '\n'
	message += '```'
	payload = {'content': message}
	headers = {'Content-Type': 'application/json'}
	r = requests.post(url, headers = headers, data = json.dumps(payload))
	print(r)

async def journal_listen(query):
	# TODO: start follow without returning recent entries
	command = ['journalctl', '--unit', query['unit'], '--follow', '--output', 'json']
	process = await asyncio.create_subprocess_exec(*command, stdout = asyncio.subprocess.PIPE)
	entries = []
	while True:
		try:
			print("waiting for line")
			line = await asyncio.wait_for(process.stdout.readline(), 5 if entries else None)
			entries.append(json.loads(line))
		except asyncio.TimeoutError:
			print("timeout, collected entries:", len(entries))
			if not entries: continue
			discord(query['url'], entries)
			entries = []

def main():
	config = read_config()

	# for each query in the config, listen for the query
	for query in config:
		asyncio.run(journal_listen(query))

main()
