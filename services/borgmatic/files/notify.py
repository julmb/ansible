#!/usr/bin/env python3

import sys, os, subprocess, json, time, asyncio, requests

def notify(name, webhook, content):
	print("notifying", name)
	url = "https://discord.com/api/webhooks/{}/{}".format(webhook["id"], webhook["token"])
	if len(content) + 6 < 2000: args = dict(json = { "content": "```" + content + "```" })
	else: args = dict(files = { "files[0]": ("borgmatic.log", content) })
	
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
	with open("/etc/borgmatic-notify.json") as config: configuration = json.load(config)
	for name, entry in configuration.items():
		# TODO: use structured json output and generate embeds from it
		command = ["borgmatic", "--config", "/etc/borgmatic.d/{}.yaml".format(name), "create", "--files", "--stats"]
		print("running backup", name)
		process = subprocess.run(command, capture_output = True, text = True)
		notify(name, entry["webhook"], process.stdout)

main()
