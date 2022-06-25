#!/usr/bin/env python3

import subprocess, json, time, asyncio, requests

def run(name):
	print("running backup", name)

	# TODO: use structured json output and generate embeds from it
	command = ["borgmatic", "--config", "/etc/borgmatic.d/{}.yaml".format(name), "create", "--files", "--stats"]
	process = subprocess.run(command, capture_output = True, text = True)
	print(process)
	return process.stdout

def notify(name, webhook, text):
	print("notifying", name)

	url = "https://discord.com/api/webhooks/{}/{}".format(webhook["id"], webhook["token"])

	if len(text) + 6 < 2000: args = dict(json = { "text": "```" + text + "```" })
	else: args = dict(files = { "files[0]": ("borgmatic.log", text) })
	
	while True:
		response = requests.post(url, **args)
		print("response code", response.status_code)
		print("response headers", response.headers)
		print("response text", response.text)
		if response.status_code == 429:
			print("current time", datetime.datetime.now().isoformat())
			print("reset on", datetime.datetime.utcfromtimestamp(int(response.headers["X-RateLimit-Reset"])).isoformat())
			print("reset in", int(response.headers["X-RateLimit-Reset-After"]))
			print("retry after", int(response.headers["Retry-After"]))
			print("sleeping for", int(response.headers["X-RateLimit-Reset-After"]), "seconds")
			time.sleep(int(response.headers["X-RateLimit-Reset-After"]))
		# TODO: properly handle all error codes
		else: break

def main():
	with open("/etc/borgmatic-notify.json") as configuration: entries = json.load(configuration)
	for name, entry in entries.items(): notify(name, entry["webhook"], run(name))

main()
