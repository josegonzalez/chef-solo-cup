Changelog
=========

0.3.0 (2016-04-05)
------------------

- Allow deciding dna file to use by ec2 tag. [Jose Diaz-Gonzalez]

- Properly format function. [Jose Diaz-Gonzalez]

0.2.0 (2016-03-11)
------------------

- Remove the json extension to ensure we do proper file matching. [Jose
  Diaz-Gonzalez]

  The `.json` extension would otherwise be sluggified, causing only partial matches and potentially incorrect ones.


- Log more information on matching databag info. [Jose Diaz-Gonzalez]

0.1.0 (2016-01-20)
------------------

- Add release script. [Jose Diaz-Gonzalez]

- Add more logging statements. [Jose Diaz-Gonzalez]

- Ignore build directory. [Jose Diaz-Gonzalez]

- Upgrade python requirements. [Jose Diaz-Gonzalez]

- Ensure dna files and names are sluggified. [Jose Diaz-Gonzalez]

- Add support for filtering hosts by aws tags. [Jose Diaz-Gonzalez]

0.0.39 (2015-09-11)
-------------------

- Make regex matches case insensitive. [Jose Diaz-Gonzalez]

0.0.38 (2015-08-19)
-------------------

- Use dummymp to fix issues with multiprocessing. [Jose Diaz-Gonzalez]

- Fix issue with filtering chef runs. [Jose Diaz-Gonzalez]

  this was broken when adding support for instances inside of VPC


0.0.36 (2015-07-29)
-------------------

- Ugly hack to make it so private ips are returned even when the group
  name and the host name are entirely different. [Evan Carter]

0.0.35 (2015-07-29)
-------------------

- Fix blacklist_rules. [Jose Diaz-Gonzalez]

0.0.34 (2015-07-15)
-------------------

- Adding ability to use different databag file so it works with vpc.
  [Evan Carter]

- Making this work with vpcs by adding an argument to connect to the
  private ips instead of public. [Evan Carter]

0.0.33 (2015-05-14)
-------------------

- Add a command to install chef via the chef install.sh script. [Jose
  Diaz-Gonzalez]

0.0.32 (2015-05-11)
-------------------

- Add ability to filter hosts from specific commands. [Jose Diaz-
  Gonzalez]

- Ensure we don't accidentally re-clone rsync exclusions. [Jose Diaz-
  Gonzalez]

- Add gitignore. [Jose Diaz-Gonzalez]

- Strip empty lines from logging output. [Jose Diaz-Gonzalez]

- Fix issue where arbitrary commands are not run due to shadowing
  `command` key. [Jose Diaz-Gonzalez]

- Fix issues with filtering nodes via the api. [Jose Diaz-Gonzalez]

0.0.29 (2015-02-06)
-------------------

- Add support for an api alternative to retrieving ec2 instances. [Jose
  Diaz-Gonzalez]

- Fix more references to args as a Namespace object. [Jose Diaz-
  Gonzalez]

- Switch to using a dictionary for arguments. [Jose Diaz-Gonzalez]

0.0.28 (2015-02-06)
-------------------

- Full PEP8 pass. [Jose Diaz-Gonzalez]

- Partial PEP8 pass. [Jose Diaz-Gonzalez]

- Add utf-8 encoding to all python files. [Jose Diaz-Gonzalez]

- Allow boto to be greater than 2.15.0. [Jose Diaz-Gonzalez]

0.0.27 (2014-03-31)
-------------------

- Add support for broken autoscale groups with whitespace. [Jose Diaz-
  Gonzalez]

0.0.26 (2014-02-04)
-------------------

- Logging improvements. Closes #9. [Jose Diaz-Gonzalez]

  With the customized logging output for parallel runs, it is now possible to export all logs to disk. It will log to a timestamped directory for each parallel run.

  The logging format for disk is:

      [IS0-8601 DATE] LEVEL   message

  While the logging format for stdout is:

      [HOST] [IS0-8601 DATE] LEVEL   message

  The reason they are different is because the files themselves contain the hostname, so there is no need to prepend it. Stdout/Stderr will also use colors in output, whereas this is omitted in the logfiles for clarity.

  Note that chef_solo_cup will attempt to create all missing directories.


0.0.25 (2014-01-20)
-------------------

- Summarize command output. [Jose Diaz-Gonzalez]

- Make deletion of files optional in update command. [Jose Diaz-
  Gonzalez]

- Set pool_size to 12. [Jose Diaz-Gonzalez]

- Add option to exclude items from being rsync'd. [Jose Diaz-Gonzalez]

- Return command results. [Jose Diaz-Gonzalez]

- Add inspect command. [Jose Diaz-Gonzalez]

- Fix detection of asg dna files when files end with .json. [Jose Diaz-
  Gonzalez]

0.0.23 (2013-11-19)
-------------------

- Set pool size to number of colors available. [Jose Diaz-Gonzalez]

0.0.22 (2013-11-19)
-------------------

- Colorized log output. Refs #9. [Jose Diaz-Gonzalez]

- Add support for running commands in parallel. [Jose Diaz-Gonzalez]

0.0.21 (2013-11-09)
-------------------

- Fix path issues when running chef. [Jose Diaz-Gonzalez]

0.0.20 (2013-11-09)
-------------------

- Standardize key names. [Jose Diaz-Gonzalez]

0.0.19 (2013-11-09)
-------------------

- Add missing import. [Jose Diaz-Gonzalez]

0.0.18 (2013-11-09)
-------------------

- Enable the .json extension on asg dna files. [Jose Diaz-Gonzalez]

- Enable configuring of asg dna path. Closes #10. [Jose Diaz-Gonzalez]

0.0.17 (2013-11-09)
-------------------

- Retrieve configuration from alternative sources. [Jose Diaz-Gonzalez]

0.0.16 (2013-11-08)
-------------------

- Add the ability to version autoscale groups. [Jose Diaz-Gonzalez]

  If you have the following autoscale group:

      app_www-12_04

  And the following dna file:

      dna/asg/app_www-12_04

  And you wish to roll over to a new autoscale group named:

      app_www-12_04-v001

  Then rather than make you create new dna files/whatever, you can simply run chef-solo-cup against the new autoscale group and it will automatically pick up the existing dna file.

  This also makes it simple to do something like:

      # new asg node on a new version of the os
      app_www-12_04 => app_www-14_04

  and use the following dna file:

      dna/asg/app_www

  Notes:

  - Logic goes: Match if exact, else match by substring, else just use the autoscale group name.
  - this is a very naive string match, so if multiple things match, you'll be SOL. Don't do that


0.0.15 (2013-10-16)
-------------------

- Add the ability to limit hosts to a number. [Jose Diaz-Gonzalez]

0.0.14 (2013-10-06)
-------------------

- Add multi-region asg support. [Jose Diaz-Gonzalez]

0.0.13 (2013-09-27)
-------------------

- Fix cleans at the end of bootstrap. Closes #8. [Jose Diaz-Gonzalez]

- Asg: Handle empty autoscaling groups. [Philip Cristiano]

  If the group was empty it would cause a search for instance_id = [] which would match all hosts. Now if the hosts in the ASG are empty it will skip the group.

0.0.12 (2013-06-27)
-------------------

- Catch EC2ResponseError. [Jose Diaz-Gonzalez]

0.0.11 (2013-06-17)
-------------------

- Asg: Include full AGS, instance name for matching. [Philip Cristiano]

- Asg: Support include / excludes. [Philip Cristiano]

  ASG hosts were included with every run ignoring include and exclude operations.

- Check that args.regions is set before using it. [Jose Diaz-Gonzalez]

- Readme: Docs that this feature at least exists. [Philip Cristiano]

- Parser: Fix description. [Philip Cristiano]

- Helpers: More specific imports. [Philip Cristiano]

- Helpers: More compatible string formatting. [Philip Cristiano]

- Requirements: Specify boto version. [Philip Cristiano]

- Args: Include defaults for AWS. [Philip Cristiano]

- Mostly working but undocumented AWS support. [Philip Cristiano]

  Add to your config:
      "aws_access_key_id": "XXX",
      "aws_secret_access_key": "XXX",
      "regions": ["us-east-1"]


- Sort hosts before running anything against them. [Jose Diaz-Gonzalez]

0.0.10 (2013-04-02)
-------------------

- Fail chef run if rsync command fails. Closes #4. [Jose Diaz-Gonzalez]

- Support multiple json config files. Closes #7. [Jose Diaz-Gonzalez]

- Fix version flag. Closes #5. [Jose Diaz-Gonzalez]

- Call clean at the end of a bootstrap call. Closes #6. [Jose Diaz-
  Gonzalez]

0.0.9 (2013-03-24)
------------------

- Fix config path. [Jose Diaz-Gonzalez]

0.0.8 (2013-03-24)
------------------

- Allow specifying the config-path and fix certain edge cases with cache
  directories. [Jose Diaz-Gonzalez]

- Allow parsing of a chef-solo-cup json file to set argparse defaults.
  [Jose Diaz-Gonzalez]

0.0.7 (2013-03-24)
------------------

- Pull version in from package. [Jose Diaz-Gonzalez]

- Guard against fabric.exceptions.NetworkError. [Jose Diaz-Gonzalez]

- Add info message when running in dry-run mode. Closes #2. [Jose Diaz-
  Gonzalez]

- Fix issue where dry-run mode caused stacktraces. [Jose Diaz-Gonzalez]

- Add exclude by regex support as analogue to dna-patterns. closes #1.
  [Jose Diaz-Gonzalez]

- Added regex support to filtering by dna_pattern. [Jose Diaz-Gonzalez]

- Added support for running tasks against a specified ip-address. [Jose
  Diaz-Gonzalez]

- Use dashes instead of underscores for argparse flags. [Jose Diaz-
  Gonzalez]

0.0.5 (2013-01-11)
------------------

- Fixed issue with referencing chef and ohai versions. [Jose Diaz-
  Gonzalez]

0.0.4 (2013-01-11)
------------------

- Return result from sudo_dry and run_dry. [Jose Diaz-Gonzalez]

0.0.3 (2013-01-11)
------------------

- Use args and logger. [Jose Diaz-Gonzalez]

0.0.2 (2013-01-08)
------------------

- Fixed issue with missing module. [Jose Diaz-Gonzalez]

0.0.1 (2013-01-08)
------------------

- Added a repository sync command, with initial support for git and
  rsync. [Jose Diaz-Gonzalez]

- Added clean command. [Jose Diaz-Gonzalez]

- Use a dict when calling chef-solo-cup commands. [Jose Diaz-Gonzalez]

- Fixed reference to non-argument. [Jose Diaz-Gonzalez]

- Move around functions. [Jose Diaz-Gonzalez]

- Further refactoring of commands. [Jose Diaz-Gonzalez]

- Work on packaging chef-solo-cup. [Jose Diaz-Gonzalez]

- Flight => cup. [Jose Diaz-Gonzalez]

- Thoughts on referencing other nodes. [Jose Diaz-Gonzalez]

- Note about dns integration. [Jose Diaz-Gonzalez]

- Clarified box names. [Jose Diaz-Gonzalez]

- Elaborated on dna generation. [Jose Diaz-Gonzalez]

- Initial commit. [Jose Diaz-Gonzalez]


