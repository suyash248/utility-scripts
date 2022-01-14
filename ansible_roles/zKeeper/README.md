# zKeeper - Role to install zookeeper

#### Prerequisites
- **Java 1.8** - Can be installed using `java_1_8` role.

#### Settings/Variables

Following variables can be overwritten by passing `extra-vars` option, or in a template created using *ansible tower*

```yaml
---
zookeeper_home: "/etc/installers/zookeeper"
zookeeper:
  home: "{{ zookeeper_home }}"
  version: 3.6.1
  scala_version: 2.13
  config_file: "zoo.cfg"
  data_dir: "{{ zookeeper_home }}/data/zookeeper"
  log_dir: "{{ zookeeper_home }}/logs"
  apt_cache_timeout: 3600
  client_port: 2181
  init_limit: 5
  sync_limit: 2
  tick_time: 2000
  hosts_file: "/etc/hosts"
  force_install: "no" # yes
  daemon:
    name: "zookeeper"
    type: "service" # systemctl
    start_on_boot: "yes" # no
```

#### Inventory/hosts
```
[zookeeper_hosts]
zookeeper1 ansible_host=116.2.142.21 alias=zookeeper1 private_ip=172.2.12.82 zookeeper_id=1 client_port=2181
zookeeper2 ansible_host=116.2.142.22 alias=zookeeper2 private_ip=172.2.12.83 zookeeper_id=2 client_port=2181
zookeeper3 ansible_host=116.2.142.23 alias=zookeeper3 private_ip=172.2.12.84 zookeeper_id=3 client_port=2181
```

#### Playbook
Sample playbook can be found in `zKeeper/tests` directory.

```yaml
---
- hosts: zookeeper_hosts
  vars:
  	ansible_python_interpreter: /usr/bin/python3
  roles:
  	- role: zKeeper
  	  become: yes
```

#### Test
```bash
$ bash bin/zkServer.sh status
/usr/bin/java
ZooKeeper JMX enabled by default
Using config: /etc/installers/zookeeper/bin/../conf/zoo.cfg
Client port found: 2181. Client address: localhost.
Mode: follower
```
