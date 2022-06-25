#!/usr/bin/env python3

import sys, os, subprocess, json, time, asyncio, requests

def notify(url, content):
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
	url = "<url>"

	# TODO: enumerate configuration files from ansible configuration
	# for each yaml file in /etc/borgmatic.d/ run borgmatic --config <file> using subprocess.run
	for file in os.listdir("/etc/borgmatic.d"):
		if file.endswith(".yaml"):
			# TODO: use structured json output and generate embeds from it
			command = ["borgmatic", "--config", "/etc/borgmatic.d/" + file, "create", "--files", "--stats"]
			process = subprocess.run(command, capture_output = True, text = True)
			notify(url, process.stdout)

main()
