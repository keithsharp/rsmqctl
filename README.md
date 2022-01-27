# RSMQ Command Line Interface
`rsmqctl` is a command line interface for [RSMQ](https://github.com/smrchy/rsmq).  The CLI is developed and tested in Python using the [PyRSMQ](https://github.com/mlasevich/PyRSMQ) package.

## Installation
I've not yet made a release and published `rsmqpctl` to [PyPi](https://pypi.org), so for the time being you need to clone the [repository](https://github.com/keithsharp/rsmqctl) or [download a release](https://github.com/keithsharp/rsmqctl/releases/).  You can then use [pip](https://pypi.org/project/pip/) to install:
```bash
pip3 install -e .
```

## Using `rsmqctl`
`rsmqctl` has two commands each with a number of subcommands, one for dealing with queues and one for dealing with messages.  On success `rsmqctl` exits with a return code of 0.  On failure the return code is 1, and a message is printed to standard error.  Help is available by using `--help` on the subcommands.

If you need additional debugging information, you can supply is `-v` or `--verbose` option to the top-level `rsmqctl` command.  This turns off the suppression of Python exceptions and full tracebacks will be printed.

### Queues
To create a queue:
```bash
$ rsmqctl queue create -n test-queue
```
There is no printed response on success.

To delete a queue:
```bash
$ rsmqctl queue delete -n test-queue
```
There is no printed response on success.

To list existing queues:
```bash
$ rsmqctl queue list                
["another-queue", "test-queue"]
```
The response is a JSON list of queue names.

To describe the properties of a queue:
```bash
$ rsmqctl queue describe -n test-queue 
{"vt": 30.0, "delay": 0.0, "maxsize": 65535, "totalrecv": 0, "totalsent": 0, "created": 1643280027, "modified": 1643280027, "msgs": 0, "hiddenmsgs": 0}
```
The response is a JSON object containing the queues properties.

### Messages
To send a message:
```bash
$ rsmqctl message send -n test-queue -m "Hello, World"
g6hste7p6xVioNo5Hz3OgAHsobrtEVeY
```
The response is the message ID.

To receive first message on a queue (marks message as hidden for length of visibility timeout):
```bash
$ rsmqctl message receive -n test-queue
{"id": "g6hste7p6xVioNo5Hz3OgAHsobrtEVeY", "message": "Hello, World", "rc": 1, "ts": 1643280991915}
```
The response is a JSON object containing the message ID, the message, how many time it has be received, and the timestamp when the message was sent.

To delete a message:
```bash
$ rsmqctl message delete -n test-queue -i g6hste7p6xVioNo5Hz3OgAHsobrtEVeY
```
There is no printed response on success.

To pop the first message from the queue (combines `receive` and `delete` in  single command):
```bash
$ rsmqctl message pop -n test-queue                   
{"id": "g6ht1jwe62tRYBzBVcKIf6H8jVCyPkOy", "message": "Hello, World", "rc": 1, "ts": 1643281386411}
```
The response is a JSON object containing the message ID, the message, how many time it has be received, and the timestamp when the message was sent.

### Redis
By default `rsmqctl` connects to the Redis instance listening on localhost at port 6379.  You can override this by supplying a Redis URL:
```bash
$ rsmqctl -r "redis://localhost:6379" queue list
["test-queue"]
```
You can also supply the Redis URL as an environment variable: `REDIS_URL`:
```bash
$ REDIS_URL="redis://localhost:6379" rsmqctl queue list
["test-queue"]
```
If your Redis instance requires a username, password, or uses TLS, you will need to use the `-r` or `--redis-url` option or the `REDIS_URL` environment variable to supply the appropriate URL.

# Copyright and License
Copyright 2022, Keith Sharp, kms@passback.co.uk.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.