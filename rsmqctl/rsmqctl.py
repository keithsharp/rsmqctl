import click
import json
import sys

from redis import Redis
from rsmq import RedisSMQ

@click.group()
@click.option('-r', '--redis-url', 'redis_url', envvar='REDIS_URL', default='redis://localhost:6379', 
    help='connection URL for the Redis server')
@click.option('-v', '--verbose', 'verbose', is_flag=True, help='show Python tracebacks on error')
@click.pass_context
def cli(ctx, redis_url, verbose):
    '''Manage RSMQ queues and messages.'''
    redis_client = Redis.from_url(redis_url)
    client = RedisSMQ(client=redis_client)
    if verbose:
        client.exceptions(True)
    else:
        client.exceptions(False)
    ctx.obj = client

@cli.group()
@click.pass_context
def queue(ctx):
    '''Manage RSMQ queues'''
    pass

@queue.command()
@click.pass_context
def list(ctx):
    '''List all queues on the server'''
    queues = ctx.obj.listQueues().execute()
    result = map(lambda b: b.decode('UTF-8'), queues)
    print(json.dumps(sorted(result)))
    sys.exit(0)

@queue.command()
@click.option('-n', '--name', 'name', required=True, help='queue name')
@click.pass_context
def describe(ctx, name):
    '''Describe the attributes of a queue'''
    attributes = ctx.obj.getQueueAttributes(qname=name, quiet=True).execute()
    if attributes:
        print(json.dumps(attributes))
        sys.exit(0)
    else:
        print('No such queue: {}'.format(name), file=sys.stderr)
        sys.exit(1)

@queue.command()
@click.option('-n', '--name', 'name', required=True, help='queue name')
@click.option('-t', '--visibility-timeout', 'vt', default=30, help='visibility timeout for messages on this queue, default is 30 seconds')
@click.option('-d', '--delay', 'delay', default=0, help='initial delay in making message visible, default is 0 seconds')
@click.option('-m', '--maxsize', 'maxsize', default=65535, help='maximum message size, default is 65535 bytes')
@click.pass_context
def create(ctx, name, vt, delay, maxsize):
    '''Create a new queue'''
    queue = ctx.obj.getQueueAttributes(qname=name, quiet=True).execute()
    if queue:
        print('Queue already exists: {}'.format(name), file=sys.stderr)
        sys.exit(1)
    
    success = ctx.obj.createQueue(qname=name, vt=vt, delay=delay, maxsize=maxsize).execute()
    if success:
        sys.exit(0)
    else:
        print('Failed to create queue: {}'.format(name), file=sys.stderr)
        sys.exit(1)


@queue.command()
@click.option('-n', '--name', 'name', required=True, help='the queue name')
@click.pass_context
def delete(ctx, name):
    '''Delete a queue'''
    queue = ctx.obj.getQueueAttributes(qname=name, quiet=True).execute()
    if not queue:
        print('No such queue: {}'.format(name), file=sys.stderr)
        sys.exit(1)

    success = ctx.obj.deleteQueue(qname=name).execute()
    if success:
        sys.exit(0)
    else:
        print('Failed to delete queue: {}'.format(name), file=sys.stderr)
        sys.exit(1)

@cli.group()
@click.pass_context
def message(ctx):
    '''Manage RSMQ messages'''
    pass

@message.command()
@click.option('-n', '--name', 'name', required=True, help='the queue name')
@click.option('-m', '--message', 'message', required=True, help='body of the message, limited by the queue max message size')
@click.option('-d', '--delay', 'delay', default=0, help='initial delay in making message visible, if not set will use queue default')
@click.pass_context
def send(ctx, name, message, delay):
    '''Publish a message to the queue'''
    queue = ctx.obj.getQueueAttributes(qname=name, quiet=True).execute()
    if not queue:
        print('No such queue: {}'.format(name), file=sys.stderr)
        sys.exit(1)

    result = ctx.obj.sendMessage(qname=name, message=message, delay=delay, quiet=True).execute()
    if result:
        print(result)
        sys.exit(0)
    else:
        print('Failed to send message: {}'.format(message), file=sys.stderr)
        sys.exit(1)

@message.command()
@click.option('-n', '--name', 'name', required=True, help='the queue name')
@click.option('-i', '--message-id', 'id', required=True, help='message identifier')
@click.pass_context
def delete(ctx, name, id):
    '''Delete a message'''
    queue = ctx.obj.getQueueAttributes(qname=name, quiet=True).execute()
    if not queue:
        print('No such queue: {}'.format(name), file=sys.stderr)
        sys.exit(1)
    
    result = ctx.obj.deleteMessage(qname=name, id=id, quiet=True).execute()
    if result:
        sys.exit(0)
    else:
        print('Failed to delete message ID: {}'.format(id), file=sys.stderr)
        sys.exit(1)

@message.command()
@click.option('-n', '--name', 'name', required=True, help='the queue name')
@click.option('-t', '--visibility-timeout', 'vt', type=int, help='visibility timeout for the message, if not set will use queue default')
@click.pass_context
def receive(ctx, name, vt):
    '''Fetch next message from the queue and mark hidden'''
    queue = ctx.obj.getQueueAttributes(qname=name, quiet=True).execute()
    if not queue:
        print('No such queue: {}'.format(name), file=sys.stderr)
        sys.exit(1)
    
    client = ctx.obj.receiveMessage(qname=name, quiet=True)
    if vt:
        client.vt(vt)
    message = client.execute()
    if message:
        message['id'] = message['id'].decode('UTF-8')
        message['message'] = message['message'].decode('UTF-8')
        print(json.dumps(message))
    else:
        print('No messages on queue: {}'.format(name))
    sys.exit(0)

@message.command()
@click.option('-n', '--name', 'name', required=True, help='the queue name')
@click.pass_context
def pop(ctx, name):
    '''Fetch and then delete the next message from the queue'''
    queue = ctx.obj.getQueueAttributes(qname=name, quiet=True).execute()
    if not queue:
        print('No such queue: {}'.format(name), file=sys.stderr)
        sys.exit(1)

    message = ctx.obj.popMessage(qname=name, quite=True).execute()
    if message:
        message['id'] = message['id'].decode('UTF-8')
        message['message'] = message['message'].decode('UTF-8')
        print(json.dumps(message))
    else:
        print('No messages on queue: {}'.format(name))
    sys.exit(0)

@message.command()
@click.option('-n', '--name', 'name', required=True, help='the queue name')
@click.option('-i', '--message-id', 'id', required=True, help='message identifier')
@click.option('-t', '--visibility-timeout', 'vt', required=True, type=int, help='visibility timeout for the message')
@click.pass_context
def visibility(ctx, name, id, vt):
    queue = ctx.obj.getQueueAttributes(qname=name, quiet=True).execute()
    if not queue:
        print('No such queue: {}'.format(name), file=sys.stderr)
        sys.exit(1)
    
    result = ctx.obj.changeMessageVisibility(qname=name, id=id, vt=vt).execute()
    if result:
        print('Message ID: {} visibility timeout set to {}s'.format(id, vt))
        sys.exit(0)
    else:
        print('Failed to change visibility timeout for message ID: {}'.format(id), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    cli()