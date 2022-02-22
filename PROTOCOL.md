# RSMQ Protocol
This document describes how RSMQ stores queues and messages within Redis.  By default all RSMQ keys use the standard prefix `rsmq:`, you can override this using the SDK.  All timestamps are seconds or milliseconds since the Unix epoch of January 1st 1970 UTC.

## `rsmq:QUEUES` Set
The `rsmq:QUEUES` key is a set that holds the names of all of the queues on the system.  If there are no queues on the system then the key will not exist.

### Example
Using `redis-cli` check if there are any queues:
```
127.0.0.1:6379> SMEMBERS rsmq:QUEUES
(empty array)
```
Confirm using `rsmqctl`:
```bash
rsmqctl queue list
[]
```

Create a queue using `rsmqctl`:
```bash
rsmqctl queue create -n test-queue
rsmqctl queue list
["test-queue"]
```
Confirm that the `rsmq:QUEUES` key exists and contains the queue identifier:
```
127.0.0.1:6379> SMEMBERS rsmq:QUEUES
1) "test-queue"
```

### `rsmq:<QUEUE_NAME>:Q` Hash
When a queue is created, as well as adding the queue name as a member of the `rsmq:QUEUES` set, a key of type hash is created with the name: `rsmq:<QUEUE_NAME>:Q` where `QUEUE_NAME` is the name of the queue that was added to the `rsmq:QUEUES` set.

After initialization, and before any messages have been sent, the hash contains five fields:
+ `vt` - the default visibility timeout for the queue, in seconds.
+ `delay` - the default message sending delay for the queue, in seconds.
+ `maxsize` - the maximum message size for the queue, in bytes.
+ `created` - the timestamp (seconds) of when the queue was created.
+ `modified` - the timestamp (seconds) of when the queue was last modified.

### Example
Use the `redis-cli` command to list the fields and values:
```
127.0.0.1:6379> HGETALL rsmq:test-queue:Q
 1) "vt"
 2) "30"
 3) "delay"
 4) "0"
 5) "maxsize"
 6) "65535"
 7) "created"
 8) "1645018248"
 9) "modified"
10) "1645018248"
```

## Sending a message and the `rsmq:<QUEUE_NAME>` Zset
When sending a message the SDK generates a unique identifier for the message.  If there are no messages currently on the queue, a key of type zset is created with the name `rsmq:<QUEUE_NAME>` where `QUEUE_NAME` is the name of the queue.  The message ID is added as a member of the `rsmq:<QUEUE_NAME>` zset with it's score set as the timestamp in milliseconds representing when the message will become visible to clients.  If the default delay for the queue is zero and no delay is specified when sending the message, the score value will be the timestamp representing now, and the message will be immediately visible.

The payload of the message is stored as field in the `rsmq:<QUEUE_NAME>:Q` hash.  The field name is the message ID and the field value is the payload of the message.  Another new field is added to the hash, `totalsent`. to store the total number of messages sent to the queue.

### Example
Send a message using `rsmqctl`:
```bash
rsmqctl message send -n test-queue -m "Hello, World"
```

Get the message ID from the `rsmq:test-queue` zset and then get the visibility timestamp using the `redis-cli`:
```
ZRANGE rsmq:test-queue 0 -1
1) "g73zkl38qzSBNq2NcnVVlCldqwqFXRJd"
127.0.0.1:6379> ZSCORE rsmq:test-queue g73zkl38qzSBNq2NcnVVlCldqwqFXRJd
"1645020200667"
```

Use the `redis-cli` command to list the fields and values:
```
127.0.0.1:6379> HGETALL rsmq:test-queue:Q
 1) "vt"
 2) "30"
 3) "delay"
 4) "0"
 5) "maxsize"
 6) "65535"
 7) "created"
 8) "1645018248"
 9) "modified"
10) "1645018248"
11) "g73zkl38qzSBNq2NcnVVlCldqwqFXRJd"
12) "Hello, World"
13) "totalsent"
14) "1"
```

## Receiving Messages
When a client receives a message the timestamp for that message held in the `rsmq:<QUEUE_NAME>` score is set to the current time plus either the default visibility timeout for the queue *or* the current time plus the visibility timeout in the receive call.  The latter overrides the former.

There are two new fields added to the `rsmq:<QUEUE_NAME>:Q` hash:
+ `g73zkl38qzSBNq2NcnVVlCldqwqFXRJd:rc` - the number of times a message has been subject to a receive call.
+ `g73zkl38qzSBNq2NcnVVlCldqwqFXRJd:fr` - the timestamp when the message first became visible on the queue.

### Example
Receive the message using `rsmqctl`:
```bash
rsmqctl message receive -n test-queue
{"id": "g73zkl38qzSBNq2NcnVVlCldqwqFXRJd", "message": "Hello, World", "rc": 1, "ts": 1645021703008}
```

Check the visibility timestamp in the `rsmq:test-queue` using the `redis-cli`:
```
127.0.0.1:6379> ZSCORE rsmq:test-queue g73zkl38qzSBNq2NcnVVlCldqwqFXRJd
"1645021733008"
```

Use the `redis-cli` command to list the fields and values:
```
127.0.0.1:6379> HGETALL rsmq:test-queue:Q
 1) "vt"
 2) "30"
 3) "delay"
 4) "0"
 5) "maxsize"
 6) "65535"
 7) "created"
 8) "1645018248"
 9) "modified"
10) "1645018248"
11) "g73zkl38qzSBNq2NcnVVlCldqwqFXRJd"
12) "Hello, World"
13) "totalsent"
14) "1"
15) "totalrecv"
16) "1"
17) "g73zkl38qzSBNq2NcnVVlCldqwqFXRJd:rc"
18) "1"
19) "g73zkl38qzSBNq2NcnVVlCldqwqFXRJd:fr"
20) "1645021703008"
```

## Changing Message Visibility
When a message's visibility is changed, the score for the message ID member in the `rsmq:<QUEUE_NAME>` zset is changed to the current time plus the visibility timeout in the change message visibility call.

### Example
Use the `redis-cli` command to view the current score for the message in the `rsmq:<QUEUE_NAME>`:
```
127.0.0.1:6379> ZSCORE rsmq:test-queue g7aoitedg36TbsB8eP2yPY8XgaLwfKN3
"1645544346419"
```

Use `rsmqctl` to change the message's visibility"
```bash
rsmqctl message visibility -n test-queue -i g7aoitedg36TbsB8eP2yPY8XgaLwfKN3 -t 600
Message ID: g7aoitedg36TbsB8eP2yPY8XgaLwfKN3 visibility timeout set to 600s
```

Use the `redis-cli` command to view the current score for the message in the `rsmq:<QUEUE_NAME>`:
```
127.0.0.1:6379> ZSCORE rsmq:test-queue g7aoitedg36TbsB8eP2yPY8XgaLwfKN3
"1645545049549"
```

## Deleting Messages
When a message is deleted it's ID member and score are removed from the `rsmq:<QUEUE_NAME>` zset.  The following fields are removed from the `rsmq:<QUEUE_NAME>:Q` hash:
+ `<MESSAGE_ID>`
+ `<MESSAGE_ID>:fr`
+ `<MESSAGE_ID>:rc`