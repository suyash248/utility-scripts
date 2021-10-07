import sys, subprocess, os
from collections import namedtuple
from typing import Dict, Any, List
from pathlib import Path

fields = ('name', 'description', 'required')
# Arg = namedtuple('Arg', fields, defaults=(None,) * len(fields))
Arg = namedtuple('Arg', fields)
Arg.__new__.__defaults__ = (None,) * len(Arg._fields)

class ArgParser(object):
    def __init__(self, arg_options: List[Arg]):
        self.arg_options = arg_options
        self.args: List[Arg] = []

    def __validate_args__(self, config: Dict[str, Any]):
        for arg_opt in self.arg_options:
            if arg_opt.required and arg_opt.name not in config:
                print("{} is required. Use --help option to get details.".format(arg_opt.name))
                return False
        return True

    def parse_args(self) -> Dict[str, Any]:
        config = dict()
        for opt in sys.argv[1:]:
            if opt.find('=') >= 0:
                opt = opt.split('=')
            else:
                opt = opt.split(' ')
            if opt[0] == '--help':
                print("\nOPTIONS:\n")
                for arg_opt in self.arg_options:
                    print('{} - {}'.format(arg_opt.name, arg_opt.description))
                return None
            else:
                config[opt[0][2:]] = opt[1]

        if not self.__validate_args__(config):
            return None
        return config

arg_parser: ArgParser = ArgParser(arg_options=[
    Arg('remote_hosts', required=True, description="Remote hosts(comma-separated), e.g. john@128.19.10.65,john@129,19.10.67"),
    Arg('jumphost', required=True, description="Jumphost/Bastion host, e.g. john@149.12.0.1"),
    # Arg('password', required=True, description="Password"),
    Arg('alias', required=True, description="Alias prefix, sequence number will be appended, e.g. prod. It will become prod_1, prod_2...prod_N")
])
config: Dict[str, str] = arg_parser.parse_args()
if config is None:
    sys.exit(0)

def make_aliases():
    home_dir = str(Path.home())
    bash_aliases_path = '{}/.bash_aliases'.format(home_dir)
    i = 1
    alias_lines = ['\n']

    for remote_host in config['remote_hosts'].split(','):
        ssh_copy_id_cmd = "ssh-copy-id -o ProxyJump={} {}".format(config['jumphost'], remote_host) # echo '{}' |
        os.system(ssh_copy_id_cmd)

        alias_cmd = 'alias {}_{}="ssh -J {} {}"\n'.format(config['alias'], i, config['jumphost'], remote_host)
        alias_lines.append(alias_cmd)
        i += 1

    with open(bash_aliases_path, "a") as bash_aliases:
        bash_aliases.writelines(alias_lines)

if __name__ == '__main__':
    make_aliases()
# ssh-copy-id -o ProxyJump=jumphost remote.host
# alias prod_1="ssh -J jumphost suyash@142.93.78.199"
