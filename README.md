# puppetdoc.py

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
