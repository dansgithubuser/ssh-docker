#! /usr/bin/env python3

#===== imports =====#
import argparse
import copy
import datetime
import os
import re
import subprocess
import sys

#===== args =====#
parser = argparse.ArgumentParser()
parser.add_argument('--pull', '-p', action='store_true')
parser.add_argument('--run', '-r', action='store_true')
args = parser.parse_args()

#===== consts =====#
DIR = os.path.dirname(os.path.realpath(__file__))

#===== setup =====#
os.chdir(DIR)

#===== helpers =====#
def blue(text):
    return '\x1b[34m' + text + '\x1b[0m'

def timestamp():
    return '{:%Y-%m-%d %H:%M:%S.%f}'.format(datetime.datetime.now())

def invoke(
    *args,
    popen=False,
    no_split=False,
    out=False,
    quiet=False,
    **kwargs,
):
    if len(args) == 1 and not no_split:
        args = args[0].split()
    if not quiet:
        print(blue('-'*40))
        print(timestamp())
        print(os.getcwd()+'$', end=' ')
        if any([re.search(r'\s', i) for i in args]):
            print()
            for i in args: print(f'\t{i} \\')
        else:
            for i, v in enumerate(args):
                if i != len(args)-1:
                    end = ' '
                else:
                    end = ';\n'
                print(v, end=end)
        if kwargs: print(kwargs)
        if popen: print('popen')
        print()
    if kwargs.get('env') != None:
        env = copy.copy(os.environ)
        env.update(kwargs['env'])
        kwargs['env'] = env
    if popen:
        return subprocess.Popen(args, **kwargs)
    else:
        if 'check' not in kwargs: kwargs['check'] = True
        if out: kwargs['capture_output'] = True
        result = subprocess.run(args, **kwargs)
        if out:
            result = result.stdout.decode('utf-8')
            if out != 'exact': result = result.strip()
        return result

#===== main =====#A
if args.pull:
    invoke('docker pull linuxserver/openssh-server')

if args.run:
    os.makedirs('volume', exist_ok=True)
    if os.path.exists('run_extra_args.txt'):
        with open('run_extra_args.txt') as f:
            extra_args = f.read().split()
    else:
        extra_args = []
    invoke(
        'docker', 'run', '-d',
        '--name=openssh-server',
        '-e', 'PUID=1000',
        '-e', 'PGID=1000',
        '-e', 'USER_NAME=q',
        '-v', f'{DIR}/volume:/volume',
        '--restart', 'unless-stopped',
        *extra_args,
        'linuxserver/openssh-server',
    )
