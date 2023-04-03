# Setup

1. Define virtual machine with one boot disk and four identical data disks.
2. Run `ansible-playbook glados/setup.yml` to generate `glados.iso`.
3. Use the generated `preseed/glados.iso` to set up the virtual machine.

# Configure

1. Run `ansible-playbook glados/configure.yml` to configure the virtual machine.
