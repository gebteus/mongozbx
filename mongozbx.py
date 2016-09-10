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
        'query', nargs='*',
        help='query is the complete query (including command).')
    return parser.parse_args()

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

def connect(uri):
    return pymongo.MongoClient(uri)

def prepare_query(command, query):
    if not command or not isinstance(command, str):
        raise Exception('Command invalid')
    if not query or not isinstance(query, list):
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

def main():
    try:
        args = parse_args()
        mclient = pymongo.MongoClient(args.uri)
        try:
            db = mclient.get_default_database()
            query = prepare_query(args.command, args.query)
            response = db.command(
                SON(query))
            stdout(json.dumps(
                get_value_through_path(response, args.path), default=json_util.default))
        except Exception as _err:
            raise _err
        finally:
            mclient.close()
    except Exception as _err:
        sys.exit(
            stderr(_err))
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()