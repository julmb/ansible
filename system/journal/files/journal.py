#!/usr/bin/python

import asyncio, json, requests

def notify(url, entries):
	print("sending notification for", len(entries), "entries")
	message = '```'
	for entry in entries: message += entry['MESSAGE'] + '\n'
	message += '```'
	payload = {'content': message}
	headers = {'Content-Type': 'application/json'}
	r = requests.post(url, headers = headers, data = json.dumps(payload))
	print(r)

async def journal(unit, timeout, notify):
	print("start watching journal for", unit)
	# TODO: start follow without returning recent entries
	command = ['journalctl', '--follow', '--output', 'json', '--unit', unit]
	process = await asyncio.create_subprocess_exec(*command, stdout = asyncio.subprocess.PIPE)
	entries = []
	while True:
		try:
			print("waiting for line, timeout", timeout if entries else None)
			line = await asyncio.wait_for(process.stdout.readline(), timeout if entries else None)
		except asyncio.TimeoutError:
			print("timeout")
			notify(entries)
			entries = []
		else:
			if not line: break
			print("append entry")
			entries.append(json.loads(line))
	print("end of file")
	notify(entries)

def main():
	with open('journal.json') as config: configuration = json.load(config)
	for query in configuration:
		asyncio.run(journal(query['unit'], 5, lambda entries: notify(query['url'], entries)))

main()
