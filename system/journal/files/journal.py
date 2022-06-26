import asyncio, json, requests, itertools, datetime, time

async def journal(unit, timeout, notify):
	print("start watching journal for", unit)
	command = ["journalctl", "--follow", "--lines", "0", "--output", "json"]
	if unit: command += ["--unit", unit]
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

def request(identifier, severity, entries):
	severities = ["Emergency", "Alert", "Critical", "Error", "Warning", "Notice", "Information", "Debug"]
	colors = [0xFF00FF, 0xFF007F, 0xFF0000, 0xFF3F3F, 0xFFFF7F, 0x7FFF7F, 0x7F7FFF, 0xAFAFAF]

	description = "".join(map(lambda entry: "```" + entry["MESSAGE"] + "```", entries))
	attachment = "{}.log".format(identifier), "\n".join(map(lambda entry: entry["MESSAGE"], entries))
	fields = [{"name": "Severity", "value": severities[severity]}]
	timestamp = datetime.datetime.utcfromtimestamp(int(entries[0]["__REALTIME_TIMESTAMP"]) / 1e6).isoformat()
	embed = {"title": identifier, "color": colors[severity], "fields": fields, "timestamp": timestamp}

	if len(description) < 4096: return dict(json = {"embeds": [embed | {"description": description}]})
	else: return dict(data = {"payload_json": json.dumps({"embeds": [embed]})}, files = {"files[0]": attachment})

def post(url, request):
	while True:
		response = requests.post(url, **request)
		print("response code", response.status_code)
		print("response headers", response.headers)
		print("response text", response.text)
		if response.status_code == 429:
			print("sleeping for", float(response.headers["X-RateLimit-Reset-After"]), "seconds")
			time.sleep(float(response.headers["X-RateLimit-Reset-After"]))
		# TODO: properly handle all error codes
		else: break

def notify(entries, url):
	def key(entry): return entry["SYSLOG_IDENTIFIER"], int(entry["PRIORITY"])
	print("sending notification for", len(entries), "entries")
	for (identifier, severity), entries in itertools.groupby(entries, key):
		post(url, request(identifier, severity, list(entries)))

def main():
	with open("journal.json") as configuration: entries = json.load(configuration)
	for name, query in entries.items():
		asyncio.run(journal(query["unit"], 5, lambda entries: notify(entries, query["url"])))

main()
