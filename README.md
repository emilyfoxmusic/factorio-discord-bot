# Factorio Discord Bot

This bot provides you the ability to run factorio servers on AWS, and control it all from discord. It provides the following features:
- creating/deleting games
- starting/stopping servers
- automatic backup to S3 on server stop/delete
- autoshutdown of servers due to inactivity

Pricing is extremely reasonable as it uses AWS's [spot pricing](https://aws.amazon.com/ec2/spot/pricing/) (an average sized server is somewhere in the region of 2 cents an hour!)

The Cloudformation part of this project is taken from Michael Chandler's [factorio spot pricing](https://github.com/m-chandler/factorio-spot-pricing).


## Usage

When the bot starts up it creates the following in your discord guild:
- A new 'Factorio' role
- A new private category called 'Factorio servers', set up so that only people with the 'Factorio' role can see it.

In order to see the server channels you need to opt in to get the 'Factorio' role (see below).

### Opt-in / out
`!count-me-in`
Assigns the commandee the Factorio role, to enable them to see the server channels.

You will either need to DM the bot to do this, or use a channel where the bot is invited, that's not hidden behind the Factorio role.

`!count-me-out`
Removes the Factorio role from the commandee.


### Admin commands
`!new <name> <version> <*mods>`
Creates a new game with the specified name, version and mods. See the [factorio-docker](https://github.com/factoriotools/factorio-docker) readme for information about supported versions. Common choices will be 'latest' or 'stable'.

A new discord channel is created automatically for controlling this game under the Factorio servers category.

`!delete <name>`
Deletes the game specified.

`!set-game <name>`
Specifies that the current discord channel should control the game specified (see game commands). Since a channel is automatically created for each game, you shouldn't need this by default.

`!list`
Lists the active games, and their current status.

### Game commands
The following commands will only work inside a discord channel linked to the game (see `!set-game`).

`!start`
Starts the server.

`!stop`
Stops the server.

`!status`
Asks for the status of the server (e.g. running, stopped, starting).

`!ip`
Gets the IP address of the game (if running).

`!let-me-live`
Resets the idle counter for the server (and causes it to stay running for another ~30mins).

### Backups
Backups are copied from the server and saved to S3. The download links are publically available.

`!backup`
Take a backup of the game, and post the link in discord.

`!list-backups [number=1]`
Post links to the latest backup(s). The number posted is 1 by default.

### Healtcheck
`!heartbeat`
Prints a generic message - used for sanity checking that the bot is responding.

## Setup

### Pre-requisites

* An AWS account, with billing set up.
  - For security it is strongly recommended to set up an IAM user specifically for the bot to use, see below for detail on permissions required.
* Somewhere to run the bot itself.
  - This could be a home server, or could be hosted on the web.

### AWS setup

1. Create your AWS account, if you don't already have one.
2. Create an IAM (API) user with the following permissions:
    * AmazonEC2FullAccess
    * IAMFullAccess
    * AmazonS3FullAccess
    * AmazonDynamoDBFullAccess
    * AutoScalingConsoleFullAccess
    * AmazonECS_FullAccess
    * AmazonSSMFullAccess
    * AmazonElasticFileSystemFullAccess
    * AWSCloudFormationFullAccess
(Note: if any AWS people out there know how I can reduce the permissions required and wants to raise a PR here, that would be ace!)
3. Create an SSH key pair for the IAM user

### Bot setup
You need to create a file called `.env` in the root of this repo to house all your secrets :) It should have the following keys:
    * DISCORD_TOKEN=(your discord bot API token)
    * AWS_ACCESS_KEY_ID=(from your IAM user)
    * AWS_SECRET_ACCESS_KEY=(from your IAM user)
    * AWS_DEFAULT_REGION=(the AWS region you want to use)
    * BOT_IP=(the IP where the bot will be hosted)
    * SSH_KEY_NAME=(the name of your SSH key pair)
    * SSH_KEY_LOCATION=(where you saved the ssh key (.pem))
    * FACTORIO_USERNAME=(your factorio username, used for downloading/updating the mods)
    * FACTORIO_TOKEN=(your factorio token - found in `\Factorio\player-data.json` under the name 'service-token')

## Hosting the bot on a linux machine using a systemd service