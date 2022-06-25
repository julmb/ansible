import asyncio, json, requests, itertools, datetime, time

severities = ["Emergency", "Alert", "Critical", "Error", "Warning", "Notice", "Information", "Debug"]
colors = [0xFF00FF, 0xFF007F, 0xFF0000, 0xFF3F3F, 0xFFFF7F, 0x7FFF7F, 0xAFAFAF, 0x7F7FFF]

def notify(url, entries):
	print("sending notification for", len(entries), "entries")
	def key(entry): return int(entry["PRIORITY"]), entry["SYSLOG_IDENTIFIER"], entry["_SYSTEMD_UNIT"]
	for (severity, identifier, unit), entries in itertools.groupby(entries, key):
		entries = list(entries)
		content = "\n".join(map(lambda entry: entry["MESSAGE"], entries))
		fields = [
			dict(name = "Severity", value = severities[severity], inline = True),
			dict(name = "Identifier", value = identifier, inline = True),
			dict(name = "Unit", value = unit, inline = True)
		]
		timestamp = datetime.datetime.utcfromtimestamp(int(entries[0]["__REALTIME_TIMESTAMP"]) / 1e6).isoformat()
		info = dict(color = colors[severity], fields = fields, timestamp = timestamp)
		if len(content) + 6 < 2000:
			payload = { "content": "```" + content + "```", "embeds": [info] }
			r = requests.post(url, json = payload)
		else:
			payload = { "embeds": [info] }
			data = { "payload_json": json.dumps(payload) }
			files = { "files[0]": ("borgmatic.log", content) }
			r = requests.post(url, data = data, files = files)
		print(r)
		print(r.text)
		time.sleep(1)

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
