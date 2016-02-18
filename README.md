# perf_check
A lightweight python terminal/console/cli style monitor that lets you monitor other hosts via SSH.
The application uses threads and subprocesses to enable asynchronos fetching of data.
The application is meant to be runned as a standalone application due to its graphical output.

# Dependencies
* ConfigParser
* thread
* time
* subprocess
* sys
* os
* re
* resource
* calendar
* itertools
* tabulate
* SAR(*nix measuring tool)
* SSH keys(non-python/shell), for every host that you might want to monitor, you must exchange the SSH key for passwordless login.

# Usage
Install dependencies, fill out the config/host file, consult the help menu for how to start the script.

# Disclaimer
This application is used on your own risk, I take no responsibility how you use this application.
This application is under development and may not be seen as the final product.
There are alot of bugs...
Please contribute if you wish to keep the project alive. :-)
