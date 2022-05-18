#!/usr/bin/python

import hashlib
import ansible.module_utils.basic

def parse(line):
	key, value = line.split(":", maxsplit = 1)
	return key.strip(), value.strip() or None

def pdbedit_user(module, name):
	rc, out, _ = module.run_command("pdbedit --user {} --verbose --smbpasswd-style".format(name))
	if rc != 0: return None
	return dict(map(parse, out.splitlines()))
def pdbedit_create(module, name):
	module.run_command("pdbedit --create --user {} --password-from-stdin".format(name), check_rc = True, data = "\n\n")
def pdbedit_delete(module, name):
	module.run_command("pdbedit --delete --user {}".format(name), check_rc = True)
def pdbedit_modify(module, name, nt_hash):
	module.run_command("pdbedit --modify --user {} --set-nt-hash {}".format(name, nt_hash), check_rc = True)

def adjust(module, name, expected, actual):
	if expected and not actual: pdbedit_create(module, name); pdbedit_modify(module, name, expected["nt_hash"])
	if not expected and actual: pdbedit_delete(module, name)
	if expected["nt_hash"] != actual["nt_hash"]: pdbedit_modify(module, name, expected["nt_hash"])
	raise ValueError("impossible violation of actual vs. expected state")

def process(module, name, state, password, check):
	# echo -n <password> | iconv -t utf16le | openssl md4
	nt_hash = hashlib.new("md4", password.encode("utf-16-le")).hexdigest().upper()
	expected = dict(nt_hash = nt_hash) if state == "present" else None
	entries = pdbedit_user(module, name)
	actual = dict(nt_hash = entries["NT hash"]) if entries else None
	if actual != expected and not check: adjust(module, name, expected, actual)
	return dict(changed = actual != expected, expected = expected, actual = actual)

def main():
	name = dict(type = "str", required = True)
	state = dict(type = "str", choices = ["present", "absent"], default = "present")
	password = dict(type = "str", default = "", no_log = True)
	parameters = dict(name = name, state = state, password = password)
	module = ansible.module_utils.basic.AnsibleModule(parameters, supports_check_mode = True)
	result = process(module, module.params["name"], module.params["state"], module.params["password"], module.check_mode)
	module.exit_json(**result)

if __name__ == "__main__": main()
