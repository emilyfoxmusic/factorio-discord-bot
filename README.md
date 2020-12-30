# Factorio Discord Bot

This bot provides you the ability to run factorio servers on AWS, and control it all from discord.

Pricing is extremely reasonable as it uses AWS's [spot pricing](https://aws.amazon.com/ec2/spot/pricing/) (an average sized server is somewhere in the region of 2 cents an hour!)

The Cloudformation part of this project is taken from Michael Chandler's [factorio spot pricing](https://github.com/m-chandler/factorio-spot-pricing).


## Usage

### Admin commands
These commands require the `factorio-admin` permission in discord (created by the bot).

`!new <name> <version> <mods>`
Creates a new game with the specified name, version and mods. See the [factorio-docker](https://github.com/factoriotools/factorio-docker) readme for information about supported versions. Common choices will be 'latest' or 'stable'.

`!delete <name>`
Deletes the game specified. DATA WILL BE LOST unless you take a backup.

`!set-game <name>`
Specifies that the current discord channel should control the game specified (see game commands).

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

## Setup

### Pre-requisites

* An AWS account, with billing set up.
  - For security it is strongly recommended to set up an IAM user specifically for the bot to use, see below for detail on permissions required.
* Somewhere to run the bot itself.
  - This could be a home server, or could be hosted on the web.

### AWS setup

## Hosting the bot on a linux machine using a systemd service