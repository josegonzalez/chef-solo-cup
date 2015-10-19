=============
chef-solo-cup
=============

Chef Solo Cup is a wrapper around chef-solo, for booting/updating AWS instances

Installation
============

Using PIP:

From Github::

    pip install git+git://github.com/josegonzalez/chef-solo-cup.git#egg=beaver

From PyPI::

    pip install chef-solo-cup

Usage
=====

CLI Usage is as follows::

    usage: chef-solo-cup [-h] [-a ASG_DNA_PATH] [-b BLACKLIST_RULE] [-c CMD]
                         [-C CONFIG_PATH] [-d DNA_PATTERNS [DNA_PATTERNS ...]]
                         [-D] [-e EXCLUDE [EXCLUDE ...]]
                         [-E RSYNC_EXCLUSIONS [RSYNC_EXCLUSIONS ...]]
                         [-i IP_ADDRESS] [-k KEY_FILENAME]
                         [-l {debug,info,warn,error,fatal}] [-L LOG_PATH]
                         [-o OUTPUT] [-P] [-p [PROVIDERS [PROVIDERS ...]]]
                         [-q QUANTITY] [-r [REGIONS [REGIONS ...]]]
                         [-R REPOSITORY] [-s [SERVICES [SERVICES ...]]]
                         [-S {git,rsync}] [-t TAGS [TAGS ...]] [-u USER] [-v]
                         [--api-password API_PASSWORD] [--api-url API_URL]
                         [--api-username API_USERNAME] [--dry-run]
                         [--chef-version CHEF_VERSION]
                         [--ohai-version OHAI_VERSION]
                         [--chef-file-dest CHEF_FILE_DEST]
                         [--aws-access-key-id AWS_ACCESS_KEY_ID]
                         [--aws-secret-access-key AWS_SECRET_ACCESS_KEY]
                         [--use-private-ips]
                         [--use-alternate-databag USE_ALTERNATE_DATABAG]
                         [{bootstrap,chef,clean,default,gem,inspect,ruby,run,sync,sudo,test,update}]

    Chef-solo-cup, a chef-solo wrapper

    positional arguments:
      {bootstrap,chef,clean,default,gem,inspect,ruby,run,sync,sudo,test,update}
                            command to run

    optional arguments:
      -h, --help            show this help message and exit
      -a ASG_DNA_PATH, --asg-dna-path ASG_DNA_PATH
                            Path to asg dna files (relative to repo base)
      -b BLACKLIST_RULE, --blacklist-rule BLACKLIST_RULE
                            pattern to use to blacklist hosts
      -c CMD, --command CMD
                            command to run
      -C CONFIG_PATH, --config-path CONFIG_PATH
                            relative path from chef file destination to solo
                            config file
      -d DNA_PATTERNS [DNA_PATTERNS ...], --dna-patterns DNA_PATTERNS [DNA_PATTERNS ...]
                            space-separated list of patterns to match against dna
                            filenames
      -D, --debug           enable debug mode
      -e EXCLUDE [EXCLUDE ...], --exclude EXCLUDE [EXCLUDE ...]
                            A regex to exclude hosts by
      -E RSYNC_EXCLUSIONS [RSYNC_EXCLUSIONS ...], --rsync-exclusions RSYNC_EXCLUSIONS [RSYNC_EXCLUSIONS ...]
                            space-separated list of files to exclude in rsync
      -i IP_ADDRESS, --ip-address IP_ADDRESS
                            The ip address to connect to
      -k KEY_FILENAME, --key-filename KEY_FILENAME
                            full path to key filename (pem key)
      -l {debug,info,warn,error,fatal}, --loglevel {debug,info,warn,error,fatal}
                            The chef log level to use
      -L LOG_PATH, --log-path LOG_PATH
                            The path to write logs to
      -o OUTPUT, --output OUTPUT
                            file to pipe output to (in addition to stdout)
      -P, --parallel        whether to run commands in parallel
      -p [PROVIDERS [PROVIDERS ...]], --providers [PROVIDERS [PROVIDERS ...]]
                            space-separated list of providers
      -q QUANTITY, --quantity QUANTITY
                            The number of nodes to provision
      -r [REGIONS [REGIONS ...]], --regions [REGIONS [REGIONS ...]]
                            space-separated list of regions
      -R REPOSITORY, --repository REPOSITORY
                            repository to use when cloning instead of using rsync
      -s [SERVICES [SERVICES ...]], --services [SERVICES [SERVICES ...]]
                            space-separated list of services
      -S {git,rsync}, --sync {git,rsync}
                            method to sync chef with
      -t TAGS [TAGS ...], --tags TAGS [TAGS ...]
                            tags to filter instances by
      -u USER, --user USER  user to run commands as
      -v, --version         Print version and exit
      --api-password API_PASSWORD
                            basic auth password for api
      --api-url API_URL     backing url for api
      --api-username API_USERNAME
                            basic auth username for api
      --dry-run             perform a dry run of all commands
      --chef-version CHEF_VERSION
                            chef version to install
      --ohai-version OHAI_VERSION
                            ohai version to install
      --chef-file-dest CHEF_FILE_DEST
                            chef file destination on disk
      --aws-access-key-id AWS_ACCESS_KEY_ID
                            AWS Access Key
      --aws-secret-access-key AWS_SECRET_ACCESS_KEY
                            AWS Secret Key
      --use-private-ips     Connect to the instances via the private ip address
                            instead of the public
      --use-alternate-databag USE_ALTERNATE_DATABAG
                            Use alternate databag instead of one defined by ASG
                            name

    Chef Solo Cup is pwnage



========
UPCOMING
========

Technical Description
=====================

Commands::

    # the binary
    chef-solo-cup

    # running commands
    chef-solo-cup [command] <required argument> (optional argument) -f {optional flag}

    # run help
    chef-solo-cup help

    # get a summary of running instances with regions
    chef-solo-cup status (group)

    # start|stop|terminate a set of instances
    chef-solo-cup start|stop|terminate
                        <group>
                        --number {number}
                        --region {region}
                        --size {size}
                        --before {run this before}
                        --after {run this after}
                        --parallel

    # update a set of instances
    # will not update instances by default, must specify a group or the flag
    chef-solo-cup update (group)
                        --all
                        --parallel

Explanation of arguments and flags:

* group:      Name of the box group to use; see below for a thorough explanation of a box group. Also supports regex for box groups.
* number:     Number of instances to affect. For bringing down instances, will affect the last n instances
* region:     Region of amazon which this command will run against. Will attempt to balance load across zones
* size:       Size of boxes to bring up, like c1.medium or m1.large
* before:     Run this command before running chef-solo-flight. Will have access to chef-solo-flight arguments
* after:      Run this command after running chef-solo-flight. Will have access to chef-solo-flight arguments
* parallel:   Run chef-solo-flight in parallel against all of these instances. Might be funky.
* all:        Run against all availabe instances

Box Groups
==========

A box group is a definition for a set of servers. In a typical server-oriented architecture, you will have several servers that will serve the same purpose. For example, it may be necessary to have 10 background workers, each having a particular set of storage volumes. These would all most likely use the same exact chef setup, and rather than duplicate this in many json files, we will create a single json "template" with this information baked in.

Below is the hypothetical contents of ``boxes/bee.json``:

::


    {
        "_box": {
            "service":          "sg",
            "storage": [
                {
                    "size":     "50",
                    "mount":    "/dev/sdf",
                    "snapshot": "343qu4rhiqhe"
                }
            ],
            "region":           "us-east-1a",
            "size":             "c1.medium",
            "provider":         "ec2",
            "ami":              "ami-6fa27506",
            "security_groups":  [ "sg-123456", "sg-789012" ]
        },
        "run_list": [
            "role[bee]"
        ]
    }

In our case, you will notice that we can specify storage units to attach to an instance, region to allocate the instances in, as well as instance size. These go under the ``_box`` top-level key, and all other key/values in the ``box.json`` file are copied into the dna.json for a particular instance.

``_box`` is a MAGIC key. DO NOT USE IT FOR YOUR OWN USES. It should only be used to define box groups.

There is also a special ``service`` key, for use in creating instance dna, as follows::

    ``:service-:box_group-:provider-:region_shorthand-:number.json``

The name of the box would be the same as the filename, without the ``json`` extension.

These keys are defined as follows:

* service:          What is this service's name? Useful when managing pieces of infrastructure that are mostly independent, such as different websites under a single umbrella organization
* box_group:        The name which is guessed from your box group json file. In the above json, this would be ``bee``
* provider:         The name of the cloud provider. At the moment, this defaults to ``ec2``. No others are supported at the moment
* region_shorthand: All regions in aws are given a shorthand, such as ``use1a`` for ``us-east-1a``. Pretty easy to guess these, and it is automatically guessed from the ``region`` selected in either your box group or as a flag to ``chef-solo-cup``.
* number:           Instance number. This is derived from the number of instances currently deployed, as well as the number of instances being deployed. Will be a zero padded 5-digit number.

You may also override the naming schema if you think you'll only use a single region, or will have multiple chef-solo-cup installations. This may be overriden in your ``solo-cup-config.rb`` file.

Configuration Management
========================

Every chef-solo-cup installation has access to a ``solo-cup-config.rb`` configuration file. Other than storage, default box configuration can be specified here. ``_box`` configuration from a specific box group will be merged ONTO the config in ``solo-cup-config.rb``. These can be overwritten at runtime using arguments on the ``chef-solo-cup`` command.

::

    # A sample solo-cup-config.rb
    # some good defaults
    service                 "sg"
    region                  "us-east-1a"
    size                    "c1.medium"
    ami                     "ami-6fa27506"
    # These are defaults, and other groups are merged ONTO these
    # default is the "default" security group
    security_groups         [ "sg-123456", "sg-789012" ]

    # Limit overrides to the following keys
    allow_override          [ :ami, :size ]

    # Turn on parallel deploys, it's off by default
    parallel                true

    # Path to generated dna files
    dna_path                "./recipes/dna"
    dna_name_template       ":service-:box_group-:provider-:region_shorthand-:number"

    # aws auth info
    aws_access_key_id:      AAAAAAAAAAAAAAAAAAAA
    aws_secret_access_key:  iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii

    # stuff for chef/ruby
    chef_version            0.10.10
    ohai_version            6.14.0
    chef_version            10.12.0

DNA Generation
==============

Generated dna would follow whatever box group you specify, plus custom configuration available within ``_box``. If bringing up 1 more ``bee`` instance using our above box group, and we already had 4 ``bee`` instances, the following would be the generated ``dna.json``

::

    {
        "_box": {
            "service":          "sg",
            "storage": [
                {
                    "size":     "50",
                    "mount":    "/dev/sdf",
                    "snapshot": "343qu4rhiqhe"
                }
            ],
            "region":           "us-east-1a",
            "size":             "c1.medium",
            "provider":         "ec2",
            "ami":              "ami-6fa27506",
            "security_groups":  [ "sg-123456", "sg-789012" ]
        },
        "box_name": "sg-bee-ec2-use1a-05",
        "run_list": [
            "role[bee]"
        ]
    }

The dna files would be placed in ``./recipes/dna`` by default, and deployed from that path. In this way, you can have your dna files as either part of your chef cookbooks or a submodule thereof.

DNA files will be generated to the following path::

    :dna_path/:provider/:region/:dna_name_template.json

This dna path is used in order to allow quicker filtering by chef-solo-cup.

DNS Integration
===============

Handle this within a recipe. Tooling to do this will only get it wrong. You can use ``node[:box_name]`` to figure out what the alias should be for the instance.

AWS Integration
===============

If you specify AWS credentials (hopefully in a file instead on the CLI) and regions, chef-solo-cup can query autoscaling groups to bring more nodes. These currently look in `dna/asg` for the DNA files.

Referencing other nodes
=======================

How do we simulate chef-server? The primary reason why you'd want to know of different nodes is to be able to write configuration files to services, datastores, etc. based upon the other nodes.

Because we know the roles of other nodes, it may be possible to load up the json for each node within a ``nodes`` attribute in the ``dna.json``. This can be dynamic and compiled once at runtime, then merged in.

Potential issues:

- Because you are provisioning new servers all the time, how do you notify old servers that the new ones are up?
  * Could have a note after the commands that detects changes in the config - ``up`` and ``down`` change stuff by default, ``update`` can be detected as a change by hashing existing json against server json - and provides a note to the user to update all the instances as appropriate
- DNS from new instances would be nice to have in other instances ``/etc/hosts`` file
  * ``chef-solo-cup bulk`` might be able to toss a single ``dna.json`` at all the instances - as filtered by flags - so we can quickly run some recipes to update key infrastructure
- No search capabilities, do not know inline what libraries are installed or packages etc.
  * Your recipes should be clear as to what library is installed on what node, so then you can infer this based upon the box group.
