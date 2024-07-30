This repository contains a collection of Ansible roles to set up various operating systems, services, and applications.

Most of the roles are written for Debian and should work both on regular Debian installations and on Raspberry Pi devices.
Some of the roles also work on Windows.

# Roles

Roles can be found in the `roles` directory.

## Operating System Setup

Roles in this section can be found in the `setup` subdirectory.

| Role     | Description                                                     |
| -------- | --------------------------------------------------------------- |
| `debian` | Generate Debian preseed images                                  |
| `rpi`    | Adjust Raspberry Pi configuration to behave like regular Debian |

## Operating System Configuration

Roles in this section can be found in the `system` subdirectory.

| Role       | Description                                  |
| ---------- | -------------------------------------------- |
| `hostname` | Set hostname based on Ansible inventory      |
| `users`    | Configure system users and group memberships |
| `network`  | Configure network interfaces                 |
| `ssh`      | Set OpenSSH system and user configuration    |
| `apt`      | Enable APT unattended upgrades               |
| `zfs`      | Configure ZFS pools and datasets             |

## Services

Roles in this section can be found in the `services` subdirectory.

| Role        | Description                                      |
| ----------- | ------------------------------------------------ |
| `nftables`  | Firewall                                         |
| `docker`    | Container engine                                 |
| `borg`      | Backup server                                    |
| `borgmatic` | Backup client                                    |
| `smart`     | Disk monitoring                                  |
| `jourdis`   | Discord notification sevice for systemd-journald |
| `ddclient`  | Dynamic dns client                               |

## Applications

Roles in this section can be found in the `applications` subdirectory.

| Role           | Description                   |
| -------------- | ----------------------------- |
| `db2`          | Database server               |
| `dnsmasq`      | DHCP and DNS server           |
| `drone`        | Continuous integration server |
| `drone-runner` | Continuous integration runner |
| `act-runner`   | Automation runner             |
| `gitea`        | Forge software                |
| `jellyfin`     | Media server                  |
| `libvirt`      | Virtualization host           |
| `mediawiki`    | Wiki software                 |
| `postgres`     | Database server               |
| `proxy`        | HTTPS reverse proxy           |
| `registry`     | Docker registry               |
| `samba`        | SMB file server               |

# Example

There is a small example configuration in the `example` directory.
