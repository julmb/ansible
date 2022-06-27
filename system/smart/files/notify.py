#!/usr/bin/env python3

import json, os, requests, datetime, time, syslog

def request():
	title = os.environ["SMARTD_SUBJECT"]
	description = os.environ["SMARTD_MESSAGE"]
	fields = [{"name": "Device Information", "value": os.environ["SMARTD_DEVICEINFO"]}]
	timestamp = datetime.datetime.utcfromtimestamp(int(os.environ["SMARTD_TFIRSTEPOCH"])).isoformat()
	embed = {"title": title, "description": description, "color": 0xFF3F3F, "fields": fields, "timestamp": timestamp}

	return dict(json = {"embeds": [embed]})
	# return dict(data = {"payload_json": json.dumps({"embeds": [embed]})}, files = {"files[0]": attachment})

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
	with open("/etc/smartd-notify.json") as configuration: webhook = json.load(configuration)
	post(webhook, request())

main()
