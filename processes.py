
"""
Copyright 2013 Andrew Spiers

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import socket
import sys

usage = "usage: type 'checks' or 'commands'."


openstack_monitored_components = set(['nova', 'glance', 'cinder', 'keystone'])

pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]


def cmdline(pid):
    """given a pid, return its cmdline by reading proc filesystem"""
    with open(os.path.join('/proc', pid, 'cmdline'), 'r') as cmdfile:
        return cmdfile.read()


def cmdlist(pid):
    """given a pid, return the commandline as a list,
     using the null as a separator, and only if the
    commandline contains a slash."""
    line = cmdline(pid)
    if "/" in line:
        return line.split('\x00')
    else:
        return False


def pythoncommand(line):
    """given a list, if the first argument contains the word 'python',
     then return the next item in the list"""
    if "python" in line[0]:
        return line[1]
    else:
        return False


def openstackprocs(pids, components):
    """given a list of process numbers, and a set of the
    openstack components, return a list of those processes that are python
    processes that have an openstack component as part of the name."""
    pythoncommands = set()
    out = []

    for i in pids:
        command = cmdlist(i)
        if  command:
            args = pythoncommand(command)
            if args:
                pythoncommands.add(os.path.basename(args))

    for i in pythoncommands:
        for j in openstack_monitored_components:
            if j in i:
                out.append(i)
    return out


def write_check(process, fqdn=socket.getfqdn(),
                contact_groups="systems-admins"):
    """given the name of a process, and the fqdn of the machine we
    are checkning, write a nagios process check,
    which will alert if the process is not running."""
    out = []
    indent = 4 * " "
    out.append("define service {")
    i_s = []  # indented section
    i_s.append("host_name " + fqdn)
    i_s.append("service_description " + process)
    i_s.append("check_command check_nrpe_1arg!check_" + process + "_proc")
    i_s.append("contact_groups " + contact_groups)
    i_s.append("use generic-service")
    indentedpart = "\n".join([indent + i for i in i_s])
    out.append(indentedpart)
    out.append("}\n\n")
    return "\n".join(out)


def write_nrpe_commands(proclist,
                        checkprocsbinary=
                        "/usr/lib/nagios/plugins/check_procs"):
    """given a list of strings which are a list of process names to monitor,
    create a nrpe conifguration line to check that at least one instance of a
    process with that name as an argument is running."""
    out = []
    for i in proclist:
        out.append("command[check_"
                   + i + "_proc]=" + checkprocsbinary + " -c 1: -a " + i)
    return "\n".join(out)


p = openstackprocs(pids, openstack_monitored_components)

output_checks = ""
for i in p:
    output_checks += write_check(i)

if len(sys.argv) != 2:
    print (usage)
    sys.exit(2)

if sys.argv[1] == "checks":
    print output_checks
elif sys.argv[1] == "commands":
    print (write_nrpe_commands(p))
else:
    print usage
    sys.exit(2)
