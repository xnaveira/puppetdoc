#!/usr/bin/python
"""
April 2014
Xavier Naveira

This script generates html formated documentation using puppet doc from a directory with
puppet modules and uploads it via rsync over ssh to a, presumably, a web server for its
display. The following parameters must be given to the script:

    ./puppetdoc -d <modules_directory> -s <destination_server> -p <destination_path> -k <key_file> [-h]

    -d <modules_directory>: The directory where the puppet modules to
    document are.
    -s <destination_server>: The address to the server where the
    documentation will be synced over
    -p <destination_path>: The path in the <destination_server> where the
    files will be synced to.
    -k <key_file>: The file containing the private key used to open an ssh
    session to run rsync in. IMPORTANT: The file must be named in the form
    username.pri where username is the username that will be used in the
    ssh session and the key must NOT contain any password.
    -h (optional): Gives this help

The idea is to schedule the execution of this script in a puppet server (ie
via cron) to automatically generate the documentation
"""

import sys
import os
import subprocess
import getopt
import fabric.api
import fabric.contrib
import fabric.contrib.files
import fabric.contrib.project
import fabric.operations
import logging
import re

logfile = 'puppetdoc.log'

logging.basicConfig(filename=logfile,level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s')

def _usage():
    puppet_help_command = 'pydoc puppetdoc'
    with fabric.api.settings(warn_only=True):
        fab_result=fabric.operations.local(puppet_help_command)

def _exception(e):
    print e
    logging.error(e)
    raise SystemExit

def main(argv):

    try:
        opts, args = getopt.getopt(argv, "d:s:p::k:h")
    except getopt.GetoptError:
        _usage()
        raise SystemExit

    if opts == [] or len(opts) < 4:
        _usage()
        sys.exit(0)

    for opt, arg in opts:
        if opt == "-h":
            _usage()
            sys.exit(0)
        elif opt == "-d":
            modules_directory = arg
        elif opt == "-s":
            destination_server = arg
        elif opt == "-p":
            destination_path = arg
        elif opt == "-k":
            key_file = arg

    #Check for modules directory
    try:
        os.listdir(modules_directory)
    except OSError as e:
        _exception(e)
    logging.debug('Modules directory exists')

    #Load the fabric credentials
    try:
        with open(key_file,'r') as f:
            #the cred file must be named as usename.pri
            username = f.name.split('.')[0]
    except IOError as e:
        _exception(e)
    logging.debug('Credentials exists')

    #Run the puppet doc
    puppet_doc_command = 'puppet doc --mode rdoc --modulepath ' + modules_directory
    with fabric.api.settings(warn_only=True):
        fab_result=fabric.operations.local(puppet_doc_command,capture=True)
        if fab_result.failed:
            print 'Something went wrong with puppet doc:\n ' + fab_result.stderr
            logging.error('Something went wrong with puppet doc, run in console to see the error')
            raise SystemExit
    logging.debug('Documentation was generated in the doc directory')

    #Sync the local configured doc with the one in the server
    with fabric.api.settings(host_string=destination_server,user=username,key_filename=key_file,quiet=True):
        fab_result=fabric.contrib.project.rsync_project(remote_dir=destination_path + '/puppetdoc',local_dir='doc',delete=True,capture=True)
        if fab_result.failed:
            print 'Something went wrong with doc sync\n ' + fab_result.stderr
            logging.error('Something went wrong with doc sync')
            raise SystemExit
    logging.debug('Sync successfull')

if __name__ == "__main__":
    main(sys.argv[1:])

