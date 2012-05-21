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

    # bring up a set of instances
    chef-solo-flight up <group> --number {number} --region {region} --size {size} --before {run this before} --after {run this after} --parallel

    # bring down a set of instances
    chef-solo-flight down <group> --number {number} --region {region} --size {size} --before {run this before} --after {run this after} --parallel

    # update a set of instances
    # will not update instances by default, must specify a group or the flag
    chef-solo-flight update (group) --all --parallel

Explanation of arguments and flags:

    group:      Name of the box group to use; see below for a thorough explanation of a box group

    number:     Number of instances to affect. For bringing down instances, will affect the last n instances
    region:     Region of amazon which this command will run against. Will attempt to balance load across zones
    size:       Size of boxes to bring up, like c1.medium or m1.large
    before:     Run this command before running chef-solo-flight. Will have access to chef-solo-flight arguments
    after:      Run this command after running chef-solo-flight. Will have access to chef-solo-flight arguments

    parallel:   Run chef-solo-flight in parallel against all of these instances. Might be funky.
    all:        Run against all availabe instances

## Box Groups

TODO