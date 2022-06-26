import asyncio, json, requests, itertools, datetime, time

# TODO: log to syslog, ignore entries originating from this script to avoid loops

def key(entry): return entry["SYSLOG_IDENTIFIER"], int(entry["PRIORITY"])

async def journal(name, unit, timeout, notify):
	print(name, "start watching journal for", unit)
	command = ["journalctl", "--follow", "--lines", "0", "--output", "json"]
	if unit: command += ["--unit", unit]
	process = await asyncio.create_subprocess_exec(*command, stdout = asyncio.subprocess.PIPE)
	entries = []
	while True:
		try:
			print(name, "waiting for line, timeout", timeout if entries else None)
			line = await asyncio.wait_for(process.stdout.readline(), timeout if entries else None)
		except asyncio.TimeoutError:
			print(name, "finish group after timeout")
			notify(entries)
			entries = []
		else:
			if not line: break
			entry = json.loads(line)
			if not entries or key(entry) == key(entries[0]):
				print(name, "add matching entry to group")
				entries.append(entry)
			else:
				print(name, "finish group after non-matching entry")
				notify(entries)
				print(name, "add first entry to new group")
				entries = [entry]
	print(name, "end of file")
	if entries:
		print(name, "finish group after end of file")
		notify(entries)
	await process.wait()

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
		print(f"response status code {response.status_code} ({response.reason})")
		if response.status_code == 200: break
		if response.status_code == 204: break
		if response.status_code == 429:
			delay = float(response.headers["X-RateLimit-Reset-After"])
			print(f"sleeping for {delay} seconds")
			time.sleep(delay)
			continue
		print(f"unexpected response status code {response.status_code} ({response.reason})")
		print(f"response content: {response.text}")
		break

def notify(url, entries):
	identifier, severity = key(entries[0])
	print(f"received group of {len(entries)} entries for {identifier} with severity {severity}")
	post(url, request(identifier, severity, entries))

async def watch(name, query):
	await journal(name, query["unit"], 5, lambda entries: notify(query["url"], entries))

async def main():
	with open("journal.json") as configuration: entries = json.load(configuration)
	watches = (watch(name, query) for name, query in entries.items())
	await asyncio.gather(*watches)

asyncio.run(main())
