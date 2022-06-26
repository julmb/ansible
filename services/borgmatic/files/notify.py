#!/usr/bin/env python3

import subprocess, json, requests, time

def run(name):
	# TODO: use structured json output and generate embeds from it
	command = ["borgmatic", "--verbosity", "1", "--syslog-verbosity", "-1", "--config", f"/etc/borgmatic.d/{name}.yaml", "create", "--files", "--stats"]
	process = subprocess.run(command, capture_output = True, text = True)
	return process.stdout

def request(text):
	if len(text) + 6 < 2000: return dict(json = { "content": "```" + text + "```" })
	else: return dict(files = { "files[0]": ("borgmatic.log", text) })
	post(webhook, request)

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

def main():
	with open("/etc/borgmatic-notify.json") as configuration: entries = json.load(configuration)
	for name, entry in entries.items(): post(entry["webhook"], request(run(name)))

main()
