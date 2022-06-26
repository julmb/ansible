#!/usr/bin/env python3

import asyncio, json, requests, datetime, time, syslog

async def journal(options, timeout, key, notify):
	command = ["journalctl", "--follow", "--lines", "0", "--output", "json"]
	options = [item for option in options for name, value in option.items() for item in ("--" + name, value)]
	process = await asyncio.create_subprocess_exec(*(command + options), stdout = asyncio.subprocess.PIPE)

	entries = []
	while True:
		try: line = await asyncio.wait_for(process.stdout.readline(), timeout if entries else None)
		except asyncio.TimeoutError: notify(entries); entries = []
		else:
			if not line: break
			entry = json.loads(line)
			if entries and key(entry) != key(entries[0]): notify(entries); entries = []
			entries.append(entry)
	if entries: notify(entries)

	await process.wait()

def request(identifier, severity, entries):
	severities = ["Emergency", "Alert", "Critical", "Error", "Warning", "Notice", "Information", "Debug"]
	colors = [0xFF00FF, 0xFF007F, 0xFF0000, 0xFF3F3F, 0xFFFF7F, 0x7FFF7F, 0x7F7FFF, 0xAFAFAF]

	description = "".join(map(lambda entry: "```" + entry["MESSAGE"] + "```", entries))
	attachment = "{}.log".format(identifier), "\n".join(map(lambda entry: entry["MESSAGE"], entries))
	fields = [{"name": "Severity", "value": severities[severity]}]
	timestamp = datetime.datetime.utcfromtimestamp(int(entries[0]["__REALTIME_TIMESTAMP"]) * 1e-6).isoformat()
	embed = {"title": identifier, "color": colors[severity], "fields": fields, "timestamp": timestamp}

	if len(description) < 4096: return dict(json = {"embeds": [embed | {"description": description}]})
	else: return dict(data = {"payload_json": json.dumps({"embeds": [embed]})}, files = {"files[0]": attachment})

def post(webhook, request):
	while True:
		response = requests.post(f"https://discord.com/api/webhooks/{webhook['id']}/{webhook['token']}", **request)
		if response.status_code == 200: break
		if response.status_code == 204: break
		if response.status_code == 429:
			data = response.json()
			message = data["message"]
			delay = float(data["retry_after"]) * 1e-3
			syslog.syslog(syslog.LOG_INFO, f"Received status code {response.status_code} ({response.reason}): {message}")
			syslog.syslog(syslog.LOG_INFO, f"Retrying request after {delay} seconds")
			time.sleep(delay)
			continue
		syslog.syslog(syslog.LOG_ERR, f"Received unexpected status code {response.status_code} ({response.reason}): {response.text}")
		break

async def run(query):
	def key(entry): return entry["SYSLOG_IDENTIFIER"], int(entry["PRIORITY"])
	def notify(entries): post(query["webhook"], request(*key(entries[0]), entries))
	await journal(query.get("options", []), query.get("timeout", 10), key, notify)

async def main():
	with open("/etc/journal-notify.json") as configuration: queries = json.load(configuration)
	await asyncio.gather(*map(run, queries))

asyncio.run(main())
