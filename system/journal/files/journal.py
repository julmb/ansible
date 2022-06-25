import asyncio, json, requests

def notify(url, entries):
	print("sending notification for", len(entries), "entries")
	message = "```" + "\n".join(map(lambda entry: entry["MESSAGE"], entries)) + "```"
	payload = { "content": message }
	r = requests.post(url, json = payload)
	print(r)
	print(r.text)

async def journal(unit, timeout, notify):
	print("start watching journal for", unit)
	command = ["journalctl", "--follow", "--lines", "0", "--output", "json", "--unit", unit]
	# TODO: check documentation of create_subprocess_exec, see if it needs with statement and how that would look like
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
	with open("journal.json") as config: configuration = json.load(config)
	for query in configuration:
		asyncio.run(journal(query["unit"], 5, lambda entries: notify(query["url"], entries)))

main()
