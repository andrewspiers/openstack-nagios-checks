openstack-nagios-checks
=======================

The [openstack operations guide](http://docs.openstack.org/trunk/openstack-ops/content/)
Describes the creation of process monitoring: Basic monitoring to ensure that
at least one instance of the various openstack processes is running.

Whilst the best way to create and manage your nagios checks is probably to use
something like Puppet exported resources, in some circumstances this is not
possible, such as when the nagios server has a different puppetmaster from what
it is monitoring.

Creating the Nagios checks and NRPE commands to run them is tiresome. That is
where this script comes in. If you run the script with the option checks, it will
generate Nagios commands to set up checks. These should be put on your Nagios
server in its configuration tree. If you run the script with the option
'commands', it will create the commands that belong in /etc/nagios/nrpe.d/ on
the machine you wish to monitor.
 
