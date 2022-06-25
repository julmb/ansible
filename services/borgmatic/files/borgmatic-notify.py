#!/usr/bin/env python3

import sys, os, subprocess, json, time, asyncio, requests

def notify(url, file, content):
		fields = [dict(name = "File", value = file)]
		info = dict(fields = fields)

		if len(content) + 6 < 2000:
			payload = { "content": "```" + content + "```", "embeds": [info] }
			args = dict(json = payload)
		else:
			payload = { "embeds": [info] }
			data = { "payload_json": json.dumps(payload) }
			files = { "files[0]": ("borgmatic.log", content) }
			args = dict(data = data, files = files)
		
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

	# for each yaml file in /etc/borgmatic.d/ run borgmatic --config <file> using subprocess.run
	for file in os.listdir("/etc/borgmatic.d"):
		if file.endswith(".yaml"):
			command = ["borgmatic", "--config", "/etc/borgmatic.d/" + file, "create", "--files", "--stats"]
			process = subprocess.run(command, capture_output = True, text = True)
			notify(url, file, process.stdout)

main()
