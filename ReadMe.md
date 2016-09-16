#mongozbx
Zabbix agent (3.X) externral script for Mongodb monitoring.

The work is based on [m-barthelemy](https://github.com/m-barthelemy)`s [native plugun](https://github.com/m-barthelemy/zabbix-mongo-old).

It can connect to a Mongo server, run basic queries and return a simple value usable by Zabbix server.

An XML template with a few useful example queries databases auto discovery is provided.


##Zabbix Configuration

###Agent configuration
- Install pymongo
```bash
    pip install --upgrade pymongo
```
- Install BSON
```bash
    pip install --upgrade bson
```
- Put [monbozbx.py](mongozbx.py) into your agent's scripts directory.
- Add ```UserParameter=mongo.run[*],<path to your agent's scripts directory>/mongozbx.py "$1" "$2" "$3" "$4"``` to the  zabix_agentd.conf or as a separate .conf file into zabbix_agentd.d folder.
###Server configuration
- Import [zabbix template](zbx_mongodb_template.xml)/
- Link it to target host.
- Set {$MGO_URL}(see [mongo_uri](#mongo_uri))  macro and don`t specify the exact database so [LLD](https://www.zabbix.com/documentation/3.0/manual/discovery/low_level_discovery) can run.

##Usage

The module is called by defining a regular Zabbix agent item:

    mongo.run[<mongo_uri>,<path>,<command>,<query>]

with:

####<a name="mongo_uri"></a>`mongo_uri `:

The Mongo URI to connect, authenticate, select the database:

Format:

    [mongodb://][user:pass@]host1[:port1][,host2[:port2],...][/database][?options]

Example:
    
    mongodb://127.0.0.1/mydb

####`path`:

The path to the wanted value. If empty, the complete result will be returned as a JSON string. if the path points to something not being a simple value, the content is returned as a JSON string.

Format:

    /property/subproperty

Examples:

  If we query "dbStats=1", we get the following JSON object:

    {"avgObjSize":0,"collections":0,"dataSize":0,"db":"test","fileSize":0,"indexSize":0,"indexes":0,"numExtents":0,"objects":0,"ok":1,"storageSize":0}

  If we want to get the value of the `dataSize` property, then `wanted_value` will be `/dataSize `.

  If we want a single value from an array, we can fetch it by its index : `/path/to/array[0]`

More examples in the `zbx_mongodb_template.xml` file.

####`command`:

`command` is the command name such as `serverStatus`, `dbStats`, `find`, `count` and etc.

####`query`: 

`query` is the complete query (including command). Its format closely follows the format of `db.RunCommand()`.

See [MongoDB documentation](https://docs.mongodb.org/manual/reference/command/).

#####Examples:

  `find()` on the "colltest" collection:
  
    find=colltest

  `find()` on the "colltest" collection, only retrieve 1 document:
  
    find=colltest limit=1

  get `dbStats`:
  
    dbStats=1

##Complete examples

    mongo.run[mongodb://127.0.0.1/myDb, /, dbStats, dbStats=1]

    mongo.run[mongodb://127.0.0.1/myDb, /connections/totalCreated, serverStatus, serverStatus=1 repl=0 metrics=0]
