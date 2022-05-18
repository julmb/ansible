#!/usr/bin/python

from itertools import islice, dropwhile
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.tools import fst, snd, single, pairwise, iterate

def parse_value(text):
	if text == "-": return None
	if text == "off": return False
	if text == "on": return True
	try: return int(text); return float(text)
	except ValueError: return text
def print_value(value):
	if value is None: return ""
	if value is False: return "off"
	if value is True: return "on"
	return str(value)

def parse_tree(lines, layer):
	if not lines or not lines[0].startswith("\t" + layer * "  "): return None
	return lines.pop(0).split()[0], list(iterate(lambda: parse_tree(lines, layer + 1)))

def zpool_status(module, name):
	rc, out, _ = module.run_command("zpool status {}".format(name))
	if rc != 0: return None
	_, vdevs = parse_tree(list(islice(dropwhile(lambda line: "config:" not in line, out.splitlines()), 3, None)), 0)
	return list((name.split("-")[0], list(map(fst, devices))) if devices else ("disk", name) for name, devices in vdevs)
def zpool_get(module, name, props):
	_, out, _ = module.run_command("zpool get -H -p -o property,value {} {}".format(",".join(props), name), check_rc = True)
	return dict((prop, parse_value(value)) for line in out.splitlines() for prop, value in [line.split("\t")])
def zpool_set(module, name, props, current):
	for prop, value in props.items():
		if current[prop] != value:
			module.run_command("zpool set {}={} {}".format(prop, print_value(value), name), check_rc = True)
def zpool_create(module, name, force, vdevs, props):
	if any(kind1 != "disk" and kind2 == "disk" for (kind1, _), (kind2, _) in pairwise(vdevs)):
		module.fail_json("cannot create pool with disk vdev after group vdev", vdevs = vdevs)
	pvdevs = " ".join(devices if kind == "disk" else " ".join([kind] + devices) for kind, devices in vdevs)
	pprops = " ".join("-o {}={}".format(prop, print_value(value)) for prop, value in props.items())
	module.run_command("zpool create {} {} {} {}".format("-f" if force else "", pprops, name, pvdevs), check_rc = True)
def zpool_destroy(module, name, force):
	module.run_command("zpool destroy {} {}".format("-f" if force else "", name), check_rc = True)

def adjust(module, name, force, expected, actual):
	if expected and not actual: zpool_create(module, name, force, expected["vdevs"], expected["props"])
	elif not expected and actual: zpool_destroy(module, name, force)
	elif expected["vdevs"] != actual["vdevs"]: module.fail_json("vdev adjustment is not supported", expected = expected, actual = actual)
	elif expected["props"] != actual["props"]: zpool_set(module, name, expected["props"], actual["props"])
	else: raise ValueError("impossible violation of actual vs. expected state")

def process(module, name, state, force, vdevs, props, check):
	expected = dict(vdevs = list(single(vdev.items()) for vdev in vdevs), props = props or {}) if state == "present" else None
	vdevs = zpool_status(module, name)
	actual = dict(vdevs = vdevs, props = zpool_get(module, name, props) if props else {}) if vdevs else None
	if actual != expected and not check: adjust(module, name, force, expected, actual)
	return dict(changed = actual != expected, expected = expected, actual = actual)

def main():
	name = dict(type = "str", required = True)
	state = dict(type = "str", choices = ["present", "absent"], default = "present")
	force = dict(type = "bool", default = False)
	vdevs = dict(type = "list", elements = "dict")
	properties = dict(type = "dict", default = None)
	parameters = dict(name = name, state = state, force = force, vdevs = vdevs, properties = properties)
	required_if = [("state", "present", ["vdevs"])]
	module = AnsibleModule(parameters, required_if = required_if, supports_check_mode = True)
	result = process(module, module.params["name"], module.params["state"], module.params["force"], module.params["vdevs"], module.params["properties"], module.check_mode)
	module.exit_json(**result)

if __name__ == "__main__": main()
