import asyncio, json, requests, itertools

# "PRIORITY": "6"
# "_COMM": "zpool"
# "__REALTIME_TIMESTAMP": "1656033052945870"
# "_SYSTEMD_UNIT": "zpool-scrub@pool2.service"
# "MESSAGE": "\t    device  ONLINE       0     0     0"
# "__MONOTONIC_TIMESTAMP": "274795432440"
# "_PID": "1130150"
# "_HOSTNAME": "host1"
# "SYSLOG_IDENTIFIER": "sh"

severities = ["Emergency", "Alert", "Critical", "Error", "Warning", "Notice", "Information", "Debug"]
colors = [0xFF0000, 0xFF0000, 0xFF0000, 0x7F0000, 0xFFFF00, 0x00FF00, 0x000000, 0x0000FF]

def notify(url, entries):
	print("sending notification for", len(entries), "entries")
	def key(entry): return int(entry["PRIORITY"]), entry["SYSLOG_IDENTIFIER"], entry["_SYSTEMD_UNIT"], entry["_COMM"]
	for (severity, identifier, unit, command), entries in itertools.groupby(entries, key):
		content = "\n".join(map(lambda entry: entry["MESSAGE"], entries))
		fields = [
			dict(name = "Severity", value = severities[severity], inline = True),
			dict(name = "Identifier", value = identifier, inline = True),
			dict(name = "Unit", value = unit, inline = True),
			dict(name = "Command", value = command, inline = True)
		]
		info = dict(color = colors[severity], fields = fields)
		if len(content) + 6 < 2000:
			payload = { "content": "```" + content + "```", "embeds": [info] }
			r = requests.post(url, json = payload)
		else:
			payload = { "embeds": [info] }
			data = { "payload_json": json.dumps(payload) }
			files = { "files[0]": ("log.txt", content) }
			r = requests.post(url, data = data, files = files)
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
