# chef-solo-cup

Chef Solo Cup is a wrapper around chef-solo, for booting/updating AWS instances

# Technical Description

Commands:

    # the binary
    chef-solo-flight

    # running commands
    chef-solo-flight [command] <required argument> (optional argument) -f {optional flag}

    # run help
    chef-solo-flight help

    # get a summary of running instances with regions
    chef-solo-flight status (group)

    # start|stop|terminate a set of instances
    chef-solo-flight start|stop|terminate
                        <group>
                        --number {number}
                        --region {region}
                        --size {size}
                        --before {run this before}
                        --after {run this after}
                        --parallel

    # update a set of instances
    # will not update instances by default, must specify a group or the flag
    chef-solo-flight update (group)
                        --all
                        --parallel

Explanation of arguments and flags:

* group:      Name of the box group to use; see below for a thorough explanation of a box group
* number:     Number of instances to affect. For bringing down instances, will affect the last n instances
* region:     Region of amazon which this command will run against. Will attempt to balance load across zones
* size:       Size of boxes to bring up, like c1.medium or m1.large
* before:     Run this command before running chef-solo-flight. Will have access to chef-solo-flight arguments
* after:      Run this command after running chef-solo-flight. Will have access to chef-solo-flight arguments
* parallel:   Run chef-solo-flight in parallel against all of these instances. Might be funky.
* all:        Run against all availabe instances

## Box Groups

A box group is a definition for a set of servers. In a typical server-oriented architecture, you will have several servers that will serve the same purpose. For example, it may be necessary to have 10 background workers, each having a particular set of storage volumes. These would all most likely use the same exact chef setup, and rather than duplicate this in many json files, we will create a single json "template" with this information baked in.

Below is the hypothetical contents of `boxes/bee.json`


    {
        "_box": {
            "service": "sg",
            "storage": [
                {
                    "size": "50",
                    "mount": "/dev/sdf",
                    "snapshot": "343qu4rhiqhe"
                }
            ],
            "region": "us-east-1a",
            "size": "c1.medium",
            "provider": "ec2",
            "ami": "ami-6fa27506"
        }
        "run_list": [
            "role[bee]"
        ]
    }

In our case, you will notice that we can specify storage units to attach to an instance, region to allocate the instances in, as well as instance size. These go under the `_box` top-level key, and all other key/values in the `box.json` file are copied into the dna.json for a particular instance.

There is also a special `service` key, for use in creating instance dna, as follows:

    `:service-:box_group-:provider-:region_shorthand-:number.json`

The name of the box would

These keys are defined as follows:

* service:          What is this service's name? Useful when managing pieces of infrastructure that are mostly independent, such as different websites under a single umbrella organization
* box_group:        The name which is guessed from your box group json file. In the above json, this would be `bee`
* provider:         The name of the cloud provider. At the moment, this defaults to `ec2`. No others are supported at the moment
* region_shorthand: All regions in aws are given a shorthand, such as `use1a` for `us-east-1a`. Pretty easy to guess these, and it is automatically guessed from the `region` selected in either your box group or as a flag to `chef-solo-cup`.
* number:           Instance number. This is derived from the number of instances currently deployed, as well as the number of instances being deployed. Will be a zero padded 5-digit number.

You may also override the naming schema if you think you'll only use a single region, or will have multiple chef-solo-cup installations. This may be overriden in your `solo-cup-config.rb` file.

## Configuration Management

Every chef-solo-cup installation has access to a `solo-cup-config.rb` configuration file. Other than storage, default box configuration can be specified here. `_box` configuration from a specific box group will be merged ONTO the config in `solo-cup-config.rb`. These can be overwritten at runtime using arguments on the `chef-solo-cup` command.

    # A sample solo-cup-config.rb
    # some good defaults
    service                 "sg"
    region                  "us-east-1a"
    size                    "c1.medium"
    ami                     "ami-6fa27506"

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
    ohai_version            0.6.10
    ruby_version            1.9.2

## DNA Generation

Generated dna would follow whatever box group you specify, plus custom configuration available within `_box`. If bringing up 1 more `bee` instance using our above box group, and we already had 4 `bee` instances, the following would be the generated `dna.json`

    {
        "_box": {
            "service": "sg",
            "storage": [
                {
                    "size": "50",
                    "mount": "/dev/sdf",
                    "snapshot": "343qu4rhiqhe"
                }
            ],
            "region": "us-east-1a",
            "size": "c1.medium",
            "provider": "ec2",
            "ami": "ami-6fa27506"
        }
        "box_name": "bee-ec2-05",
        "run_list": [
            "role[bee]"
        ]
    }

The dna files would be placed in `./recipes/dna` by default, and deployed from that path. In this way, you can have your dna files as either part of your chef cookbooks or a submodule thereof.

DNA files will be generated to the following path:

    :dna_path/:provider/:region/:dna_name_template.json

This dna path is used in order to allow quicker filtering by chef-solo-flight.