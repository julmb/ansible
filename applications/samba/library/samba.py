#!/usr/bin/python

import hashlib

from ansible.module_utils.basic import AnsibleModule

def parse(line):
	key, value = line.split(":", maxsplit = 1)
	return key.strip(), value.strip() or None

def pdbedit_user(module, name):
	rc, out, _ = module.run_command("pdbedit --user {} --verbose --smbpasswd-style".format(name))
	return dict(map(parse, out.splitlines())) if rc == 0 else None
def pdbedit_create(module, name):
	module.run_command("pdbedit --create --user {} --password-from-stdin".format(name), check_rc = True, data = "\n\n")
def pdbedit_delete(module, name):
	module.run_command("pdbedit --delete --user {}".format(name), check_rc = True)
def pdbedit_modify(module, name, nt_hash):
	module.run_command("pdbedit --modify --user {} --set-nt-hash {}".format(name, nt_hash), check_rc = True)

def adjust(module, name, expected, actual):
	if expected and not actual: pdbedit_create(module, name); pdbedit_modify(module, name, expected["nt_hash"])
	elif not expected and actual: pdbedit_delete(module, name)
	elif expected["nt_hash"] != actual["nt_hash"]: pdbedit_modify(module, name, expected["nt_hash"])
	else: raise ValueError("impossible violation of actual vs. expected state")

def process(module, name, state, nt_hash, password, check):
	# echo -n <password> | iconv -t utf16le | openssl md4
	if not nt_hash: nt_hash = hashlib.new("md4", password.encode("utf-16-le")).hexdigest().upper()
	expected = dict(nt_hash = nt_hash) if state == "present" else None
	entries = pdbedit_user(module, name)
	actual = dict(nt_hash = entries["NT hash"]) if entries else None
	if actual != expected and not check: adjust(module, name, expected, actual)
	return dict(changed = actual != expected, expected = expected, actual = actual)

def main():
	name = dict(type = "str", required = True)
	state = dict(type = "str", choices = ["present", "absent"], default = "present")
	nt_hash = dict(type = "str", no_log = True)
	password = dict(type = "str", default = "", no_log = True)
	parameters = dict(name = name, state = state, nt_hash = nt_hash, password = password)
	mutually_exclusive = [("nt_hash", "password")]
	module = AnsibleModule(parameters, mutually_exclusive = mutually_exclusive, supports_check_mode = True)
	result = process(module, module.params["name"], module.params["state"], module.params["nt_hash"], module.params["password"], module.check_mode)
	module.exit_json(**result)

if __name__ == "__main__": main()
