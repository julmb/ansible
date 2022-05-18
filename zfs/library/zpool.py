#!/usr/bin/python

import ansible.module_utils.basic

# TODO: can we pattern match on 2-tuple so that this doesn't work on sequences?
def fst(tuple): return tuple[0]
def snd(tuple): return tuple[1]
def single(sequence): [item] = sequence; return item
def pairs(sequence): return zip(sequence, sequence[1:])
def iterate(get):
	while item := get(): yield item

def run(module, command, check = True):
	code, out, err = module.run_command(command)
	if code == 0: return out
	if not check: return None
	print(out); print(err)
	raise ValueError("command returned error code", command, code)

def parse_tree(lines, layer):
	if not lines or not lines[0].startswith("\t" + layer * "  "): return None
	return lines.pop(0).split()[0], list(iterate(lambda: parse_tree(lines, layer + 1)))

def parse_value(text):
	if text == "-": return None
	if text == "off": return False
	if text == "on": return True
	try: return int(text); return float(text)
	except ValueError: return text
def print_value(value):
	if value == False: return "off"
	if value == True: return "on"
	return str(value)

def zpool_status(module, name):
	out = run(module, "zpool status {}".format(name), False)
	if not out: return None
	lines = out.splitlines()
	list(iterate(lambda: None if "config:" in lines.pop(0) else "entry"))
	vdevs = snd(parse_tree(lines[2:], 0))
	return list((name.split("-")[0], list(map(fst, devices))) if devices else ("disk", name) for name, devices in vdevs)
def zpool_get(module, name, properties):
	if not properties: return properties
	out = run(module, "zpool get -H -p -o property,value {} {}".format(",".join(properties), name))
	return {prop: parse_value(value) for line in out.splitlines() for prop, value in [line.split("\t")]}
def zpool_set(module, name, properties, current):
	properties = {prop: value for prop, value in properties.items() if value != current[prop]}
	for prop, value in properties.items(): run(module, "zpool set {}={} {}".format(prop, print_value(value), name))
	return "set properties {} of {}".format(properties, name)
def zpool_create(module, name, vdevs, properties):
	if any(kind1 != "disk" and kind2 == "disk" for kind1, kind2 in pairs(list(map(fst, vdevs)))):
		raise NotImplementedError("cannot create pool with disk vdev following group vdev", vdevs)
	pvdevs = " ".join(devices if kind == "disk" else " ".join([kind] + devices) for kind, devices in vdevs)
	pproperties = " ".join("-o {}={}".format(prop, print_value(value)) for prop, value in properties.items())
	run(module, "zpool create {} {} {}".format(pproperties, name, pvdevs))
	return "created zpool {}".format(name)
def zpool_destroy(module, name):
	run(module, "zpool destroy {}".format(name))
	return "destroyed zpool {}".format(name)

def adjust(module, name, expected, actual):
	if expected and not actual: return zpool_create(module, name, expected["vdevs"], expected["properties"])
	if not expected and actual: return zpool_destroy(module, name)
	if expected["vdevs"] != actual["vdevs"]:
		raise NotImplementedError("vdev adjustment is not supported", actual["vdevs"], expected["vdevs"])
	if expected["properties"] != actual["properties"]:
		return zpool_set(module, name, expected["properties"], actual["properties"])
	raise ValueError("impossible violation of actual vs. expected state")

# TODO: name is never used in expected/actual
def process(module, name, state, vdevs, properties, check):
	vdevs = list(single(vdev.items()) for vdev in vdevs)
	expected = dict(name = name, vdevs = vdevs, properties = properties) if state == "present" else None
	status = zpool_status(module, name)
	actual = dict(name = name, vdevs = status, properties = zpool_get(module, name, properties)) if status else None
	result = dict(changed = actual != expected, expected = expected, actual = actual)
	return result | {"action": adjust(module, name, expected, actual)} if result["changed"] and not check else result

def main():
	name = dict(type = "str", required = True)
	state = dict(type = "str", choices = ["present", "absent"], default = "present")
	vdevs = dict(type = "list", elements = "dict")
	properties = dict(type = "dict", default = {})
	parameters = dict(name = name, state = state, vdevs = vdevs, properties = properties)
	required_if = [("state", "present", ["vdevs"])]
	module = ansible.module_utils.basic.AnsibleModule(parameters, required_if = required_if, supports_check_mode = True)
	result = process(module, module.params["name"], module.params["state"], module.params["vdevs"], module.params["properties"], module.check_mode)
	module.exit_json(**result)

if __name__ == "__main__": main()
