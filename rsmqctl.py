from tabnanny import verbose
import click
import json
import sys

from redis import Redis
from rsmq import RedisSMQ

@click.group()
@click.option('-h', '--host', 'host', default='127.0.0.1')
@click.option('-p', '--port', 'port', default=6379, type=int)
@click.option('-v', '--verbose', 'verbose', is_flag=True)
@click.pass_context
def cli(ctx, host, port, verbose):
    redis_client = Redis(host=host, port=port)
    client = RedisSMQ(client=redis_client)
    if verbose:
        client.exceptions(True)
    else:
        client.exceptions(False)
    ctx.obj = client

@cli.group()
@click.pass_context
def queue(ctx):
    pass

@queue.command()
@click.pass_context
def list(ctx):
    queues = ctx.obj.listQueues().execute()
    result = map(lambda b: b.decode('UTF-8'), queues)
    print(json.dumps(sorted(result)))
    sys.exit(0)

@queue.command()
@click.option('-n', '--name', 'name', required=True)
@click.pass_context
def describe(ctx, name):
    attributes = ctx.obj.getQueueAttributes(qname=name, quiet=True).execute()
    if attributes:
        print(json.dumps(attributes))
        sys.exit(0)
    else:
        print('No such queue: {}'.format(name))
        sys.exit(1)

@queue.command()
@click.option('-n', '--name', 'name', required=True)
@click.option('-t', '--vt', 'vt', default=30)
@click.option('-d', '--delay', 'delay', default=0)
@click.option('-m', '--maxsize', 'maxsize', default=65535)
@click.pass_context
def create(ctx, name, vt, delay, maxsize):
    queue = ctx.obj.getQueueAttributes(qname=name, quiet=True).execute()
    if queue:
        print('Queue already exists: {}'.format(name))
        sys.exit(1)
    
    success = ctx.obj.createQueue(qname=name, vt=vt, delay=delay, maxsize=maxsize).execute()
    if success:
        sys.exit(0)
    else:
        print('Failed to create queue: {}'.format(name))
        sys.exit(1)


@queue.command()
@click.option('-n', '--name', 'name', required=True)
@click.pass_context
def delete(ctx, name):
    queue = ctx.obj.getQueueAttributes(qname=name, quiet=True).execute()
    if not queue:
        print('No such queue: {}'.format(name))
        sys.exit(1)

    success = ctx.obj.deleteQueue(qname=name).execute()
    if success:
        sys.exit(0)
    else:
        print('Failed to delete queue: {}'.format(name))
        sys.exit(1)

if __name__ == '__main__':
    cli()