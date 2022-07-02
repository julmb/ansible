#!/usr/bin/env python3

import time, subprocess, syslog
import json, requests

# TODO: use structured json output and generate embeds from it
def borgmatic(name):
	command = ["borgmatic", "--verbosity", "1", "--syslog-verbosity", "-1"]
	options = ["--config", f"/etc/borgmatic.d/{name}.yaml"]
	action = ["create", "--files", "--stats"]
	process = subprocess.run(command + options + action, capture_output = True, text = True)
	return process.stdout

def request(name, text):
	title = f"Finished backup {name}"
	content = title + "\n" + "```" + text + "```"
	attachment = f"{name}.log", text
	if len(content) < 2000: return dict(json = {"content": content})
	else: return dict(data = {"payload_json": json.dumps({"content": title})}, files = {"files[0]": attachment})

def post(webhook, request):
	while True:
		try: response = requests.post(f"https://discord.com/api/webhooks/{webhook['id']}/{webhook['token']}", **request)
		except requests.exceptions.ConnectionError as error:
			delay = 10
			syslog.syslog(syslog.LOG_INFO, f"Connection error: {error}")
			syslog.syslog(syslog.LOG_INFO, f"Retrying request after {delay} seconds")
			time.sleep(delay)
			continue
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
	with open("/etc/borgmatic-notify.json") as configuration: backups = json.load(configuration)
	for name, backup in backups.items(): post(backup["webhook"], request(name, borgmatic(name)))

main()
