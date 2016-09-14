#!/usr/bin/env python

import sys
def stderr(error, code=1):
    sys.stderr.write('Error: {0}.\n'.format(
        str(error)))
    return code

import json
import argparse
try:
    import pymongo
    from bson import SON
    from bson import json_util
except ImportError as _err:
    sys.exit(
        stderr(_err))

_SCRIPT_VERSION = '0.1'

class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help()
        sys.exit(
            stderr(message))

def parse_args():
    parser = ArgumentParser(
        description='Zabbix agent (3.0) native plugin for Mongodb monitoring.',
        add_help=False)
    parser.add_argument(
        'uri',
        help='the Mongo URI to connect, authenticate, select the database.')
    parser.add_argument(
        'path',
        help='the path to the wanted value.'
        'If the path points to something not being a simple value, the content is returned as a JSON string.')
    parser.add_argument(
        'command',
        help='command is the command name such as serverStatus, dbStats, find, count and etc.')
    parser.add_argument(
        'query', nargs='*', default='',
        help='query is the complete query (including command).')
    return parser.parse_args()

class q_handler:
    _instr_ = [
        'discoverDatabases']

    def __init__(self, uri, command, query):
        if isinstance(command, str) is False or len(command) == 0:
            raise Exception('Command invalid')
        self.mongoclient = pymongo.MongoClient(uri)
        if command in self._instr_:
            self.db = self.mongoclient.get_database(name='admin')
        else:
            self.db = self.mongoclient.get_default_database()
        self.command = command
        self.query = query

    def __del__(self):
        if self.mongoclient:
            self.mongoclient.close()

    def execute(self):
        if self.command in self._instr_:
            glob = globals()
            function = glob.get(self.command)
            if function is not None:
                return function(self.db)
            else:
                raise Exception('Function \'{0}\' not found'.format(
                    self.command))
        else:
            return self.db.command(
                SON(self.prepare()))
        return {}

    def prepare(self):
        command = self.command
        query = self.query
        if isinstance(query, list) is False or len(query) == 0:
            raise Exception('Query invalid')
        i = 0
        while True:
            i += 1
            if 0 < i < len(query):
                if '=' not in query[i]:
                    query[i-1] += ' ' + query.pop(i)
                    i = 0
            else:
                break
        for item in query:
            if '=' not in item:
                raise Exception('Query is not correct')
        query = dict(s.split('=') for s in query)
        if command not in query:
            raise Exception('Didn\'t find command \'{0}\' in query'.format(command))
        qlist = []
        qkeys = list(
            query.keys())
        qlist.append(
            (command, query.get(command)))
        del qkeys[qkeys.index(command)]
        for key in qkeys:
            qlist.append(
                (key, query.get(key)))
        return qlist

def stdout(message=''):
    sys.stdout.write('{0}\n'.format(message))

def get_value_through_path(data, path):
    item = data
    try:
        if len(path) > 1:
            for i in path.strip('/').split('/'):
                if i.isdigit():
                    item = item[int(i)]
                else:
                    item = item.get(i)
    except:
        pass
    return item

# Special methods
def discoverDatabases(db):
    response = db.command(
        SON({'listDatabases': 1 }))
    result = []
    databases = response.get('databases')
    if databases is None:
        raise Exception('Get databases list failed')
    for item in databases:
        dbname = item.get('name')
        if dbname is not None:
            result.append({'{#DBNAME}': dbname})
    return {'data': result}

# Main
def main():
    try:
        args = parse_args()
        hdlr = q_handler(args.uri, args.command, args.query)
        try:
            response = hdlr.execute()
            stdout(json.dumps(
                get_value_through_path(response, args.path), default=json_util.default))
        except Exception as _err:
            raise _err
        finally:
            del hdlr
    except Exception as _err:
        sys.exit(
            stderr(_err))
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()