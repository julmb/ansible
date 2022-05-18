#!/usr/bin/python

import hashlib

from ansible.module_utils.basic import AnsibleModule

# echo -n <password> | iconv -t utf16le | openssl md4
def hash_nt(password): return hashlib.new("md4", password.encode("utf-16-le")).hexdigest().upper()

def run(module, command, data = None, check = True):
	code, out, err = module.run_command(command, data = data)
	if code == 0: return out
	if not check: return None
	print(out); print(err)
	raise ValueError("command returned error code", command, code)

def parse(line):
	key, value = line.split(":", maxsplit = 1)
	return key.strip(), value.strip() or None

def pdbedit_user(module, name):
	out = run(module, "pdbedit --user {} --verbose --smbpasswd-style".format(name), check = False)
	if not out: return None
	return dict(parse(line) for line in out.splitlines())
def pdbedit_create(module, name, password):
	run(module, "pdbedit --create --user {} --password-from-stdin".format(name), "{}\n{}\n".format(password, password))
	return "added {} with password {}".format(name, password)
def pdbedit_delete(module, name):
	run(module, "pdbedit --delete --user {}".format(name))
	return "removed {}".format(name)
def pdbedit_modify(module, name, password):
	run(module, "pdbedit --modify --user {} --set-nt-hash {}".format(name, password))
	return "set password for {} to {}".format(name, password)

def adjust(module, name, expected, actual):
	if expected and not actual: return pdbedit_create(module, name, expected["password"])
	if not expected and actual: return pdbedit_delete(module, name)
	if expected["password"] != actual["password"]: return pdbedit_modify(module, name, expected["password"])
	raise ValueError("impossible violation of actual vs. expected state")

def process(module, name, state, password, check):
	expected = dict(password = hash_nt(password)) if state == "present" else None
	entries = pdbedit_user(module, name)
	actual = dict(password = entries["NT hash"]) if entries else None
	result = dict(changed = actual != expected, expected = expected, actual = actual)
	return result | {"action": adjust(module, name, expected, actual)} if result["changed"] and not check else result

def main():
	name = dict(type = "str", required = True)
	state = dict(type = "str", choices = ["present", "absent"], default = "present")
	password = dict(type = "str", no_log = True)
	parameters = dict(name = name, state = state, password = password)
	required_if = [("state", "present", ["password"])]
	module = AnsibleModule(parameters, required_if = required_if, supports_check_mode = True)
	result = process(module, module.params["name"], module.params["state"], module.params["password"], module.check_mode)
	module.exit_json(**result)

if __name__ == "__main__": main()
