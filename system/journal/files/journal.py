#!/usr/bin/python

import asyncio, json, requests

def discord(url, entries):
	message = '```'
	for entry in entries:
		message += entry['MESSAGE'] + '\n'
	message += '```'
	payload = {'content': message}
	headers = {'Content-Type': 'application/json'}
	r = requests.post(url, headers = headers, data = json.dumps(payload))
	print(r)

async def journal(query):
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
	with open('journal.json') as config:
		configuration = json.load(config)

	for query in configuration:
		asyncio.run(journal(query))

main()
