#!/usr/bin/python

import sys, subprocess, hashlib

from ansible.module_utils.basic import AnsibleModule

# echo -n <password> | iconv -t utf16le | openssl md4
def hash_nt(password): return hashlib.new("md4", password.encode("utf-16-le")).hexdigest().upper()

def parse(line):
	key, value = line.split(":", maxsplit = 1)
	return key.strip(), value.strip() or None

def pdbedit_user(name):
	command = ["pdbedit", "--user", name, "--verbose", "--smbpasswd-style"]
	pdbedit = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = True)
	if pdbedit.returncode == 0 and not pdbedit.stderr: return dict(parse(line) for line in pdbedit.stdout.splitlines())
	if pdbedit.returncode == 255 and pdbedit.stderr == "Username not found!\n": return None
	print(pdbedit.stdout, file = sys.stdout)
	print(pdbedit.stderr, file = sys.stderr)
	pdbedit.check_returncode()
def pdbedit_create(name):
	command = ["pdbedit", "--create", "--user", name, "--password-from-stdin"]
	pdbedit = subprocess.run(command, input = "\n\n", stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = True)
	if pdbedit.returncode == 0 and not pdbedit.stderr: return
	print(pdbedit.stdout, file = sys.stdout)
	print(pdbedit.stderr, file = sys.stderr)
	pdbedit.check_returncode()
def pdbedit_delete(name):
	command = ["pdbedit", "--delete", "--user", name]
	pdbedit = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = True)
	if pdbedit.returncode == 0 and not pdbedit.stderr: return
	print(pdbedit.stdout, file = sys.stdout)
	print(pdbedit.stderr, file = sys.stderr)
	pdbedit.check_returncode()
def pdbedit_modify(name, password):
	command = ["pdbedit", "--modify", "--user", name, "--set-nt-hash", password]
	pdbedit = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = True)
	if pdbedit.returncode == 0 and not pdbedit.stderr: return
	print(pdbedit.stdout, file = sys.stdout)
	print(pdbedit.stderr, file = sys.stderr)
	pdbedit.check_returncode()

def user_get(name):
	entries = pdbedit_user(name)
	return dict(state = "present", password = entries["NT hash"]) if entries else dict(state = "absent", password = None)
def user_add(name, password):
	pdbedit_create(name)
	pdbedit_modify(name, password)
	return "added {} with password {}".format(name, password)
def user_remove(name):
	pdbedit_delete(name)
	return "removed {}".format(name)
def user_password(name, password):
	pdbedit_modify(name, password)
	return "set password for {} to {}".format(name, password)

def adjust(name, expected, actual):
	if expected["state"] == "present" and actual["state"] == "absent": return user_add(name, expected["password"])
	if expected["state"] == "absent" and actual["state"] == "present": return user_remove(name)
	if expected["password"] != actual["password"]: return user_password(name, expected["password"])
	raise ValueError("impossible violation of actual vs. expected state")

def process(name, state, password, check):
	if state == "present" and password is None:
		raise ValueError("when state is 'present', password cannot be 'None'", state, password)
	if state == "absent" and password is not None:
		raise ValueError("when state is 'absent', password has to be 'None'", state, password)
	expected = dict(state = state, password = None if password is None else hash_nt(password))
	actual = user_get(name)
	result = dict(changed = actual != expected, expected = expected, actual = actual)
	return result | {"action": adjust(name, expected, actual)} if result["changed"] and not check else result

def main():
	name = dict(type = 'str', required = True)
	state = dict(type = 'str', choices = ["present", "absent"], default = "present")
	password = dict(type = 'str', no_log = True)
	parameters = dict(name = name, state = state, password = password)
	module = AnsibleModule(parameters, supports_check_mode = True)
	result = process(module.params["name"], module.params["state"], module.params["password"], module.check_mode)
	module.exit_json(**result)

if __name__ == "__main__": main()
