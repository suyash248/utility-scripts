# pip3 install cassandra-driver
# python3 pycqlsh.py

import sys, traceback
from collections import namedtuple
from typing import Dict, Set, Any

from cassandra.cluster import Cluster, ResultSet
from cassandra.protocol import SyntaxException
from cassandra.query import Statement, SimpleStatement, dict_factory

stop_commands = ('EXIT', 'QUIT', 'STOP', '', None)

fields = ('name', 'description', 'required', 'default')
Arg = namedtuple('Arg', fields)
Arg.__new__.__defaults__ = (None,) * len(Arg._fields)

class ArgParser(object):
    def __init__(self, arg_options: Set[Arg]):
        self.arg_options = arg_options
        self.args: Set[Arg] = set()

    def __validate_args__(self, config: Dict[str, Any]):
        for arg_opt in self.arg_options:
            if arg_opt.required and arg_opt.name not in config:
                print("{} is required. Use --help option to get details.".format(arg_opt.name))
                return False
            if arg_opt.name not in config and arg_opt.default:
                config[arg_opt.name] = arg_opt.default
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
                    print('{} - {}. default: {}'.format(arg_opt.name, arg_opt.description, arg_opt.default))
                print("\nEnter 'EXIT/STOP' to exit.")
                return None
            else:
                config[opt[0][2:]] = opt[1]


        if not self.__validate_args__(config):
            return None
        return config

arg_parser: ArgParser = ArgParser(arg_options={
    Arg('cassandra_contact_points', required=False, default='172.18.0.2',
        description="Cassandra contact points(comma-separated), e.g. 10.0.0.1,10.0.0.2"),
    Arg('cassandra_port', required=False, default='9042', description="Cassandra port"),
    Arg('keyspace', required=False, default='quicko', description="Cassandra keyspace"),
    Arg('paging', required=False, default='100', description="PAGING OFF/<number>"),
    Arg('expand', required=False, default='ON', description="EXPAND ON/OFF"),
})
config: Dict[str, str] = arg_parser.parse_args()
if config is None:
    sys.exit(0)

cluster = Cluster(contact_points=config.get('cassandra_contact_points').split(','), port=config.get('cassandra_port'),
                  connect_timeout=30, control_connection_timeout=30)
session = cluster.connect(config.get('keyspace'))
session.row_factory = dict_factory

def yield_rows(stmt: Statement, bound_params=None):
    stmt.fetch_size = 100 if config['paging'] == 'OFF' else int(config['paging'])
    rs: ResultSet = session.execute(stmt, parameters=bound_params)
    has_pages = True
    while has_pages:
        yield from rs.current_rows
        has_pages = rs.has_more_pages
        if config.get('paging') != 'OFF' and has_pages:
            input('\n---MORE---\n')
        rs = session.execute(stmt, parameters=bound_params, paging_state=rs.paging_state)

def execute(cql: str):
    stmt: SimpleStatement = SimpleStatement(cql)
    num_rows: int = 0
    for row_dict in yield_rows(stmt):
        num_rows += 1
        if config['expand'] == 'OFF':
            print(row_dict)
        elif config['expand'] == 'ON':
            print(''.join(['-'] * 100))
            print('Row-{}'.format(num_rows))
            print(''.join(['-'] * 100))
            for k, v in row_dict.items():
                print('{} -> {}'.format(k, v))
    print('\n{} row(s) found'.format(num_rows))


if __name__ == '__main__':
    while True:
        cql = input("<cqlsh:{}> ".format(config['keyspace']))
        if cql.endswith(';'):
            cql = cql[:-1]
        try:
            if cql.strip().upper() in stop_commands:
                break
            if cql:
                execute(cql)
                print('\n{delimiter} END {delimiter}\n'.format(delimiter=''.join(['#'] * 50)))
        except SyntaxException as syex:
            print("Inavalid CQL: {}".format(syex.message))
        except Exception as ex:
            print("Error occurred")
            traceback.print_exc()

    print('Closing session...')
    session.shutdown()
    cluster.shutdown()
