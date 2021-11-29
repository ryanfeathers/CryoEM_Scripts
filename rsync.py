#!/usr/bin/env python
"""
rsync data

Author: Ryan Feathers jrf296
Date: 11/29/2021
"""

import os, sys, subprocess, pipes, time, argparse



parser = argparse.ArgumentParser()
parser.add_argument('--u', type=str, required=True, help='remote user name')
parser.add_argument('--i', type=str, required=True, help='remote ip address')
parser.add_argument('--p', type=str, required=True, help='full path to data dir')
parser.add_argument('--d', type=str, required=True, help='full path to remote dest')
args = parser.parse_args()

def exists_remote(host, path):
    """Test if a file exists at path on a host accessible with SSH."""
    status = subprocess.call(
        ['ssh', host, 'test -f {}'.format(pipes.quote(path))])
    if status == 0:
        return True
    if status == 1:
        return False
    raise Exception('SSH failed')

ssh = args.u+"@"+args.i
datadir = args.d
rsync = "rsync -aP "+args.p+" "+ssh+":"+datadir
while True:
		try:
			os.system(rsync)
		except:
			print("rsync command failed:"+rsync)
		time.sleep(300)
		current_time = time.strftime("%H:%M:%S", time.localtime())

		print('\n'+'Directory is current as of: '+current_time+'\n')

		if exists_remote(ssh, datadir+"stop"):
			break
print("Stop file detected, ending rsync"+'\n')



