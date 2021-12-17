from enum import Enum
import logging
from ..services import game_service, game_message_service, rcon_service
from ..helpers import status_helper


IDLE_TRACKERS = {}
PREVIOUS_IDLE_STATUSES = {}


async def auto_shutdown_loop(bot):
    logging.info('Running auto-shutdown loop')
    games = await game_service.list_games()
    for game in games:
        status = games[game]
        if status != status_helper.Status.RUNNING:
            logging.info(
                '%s is no longer running so will not be monitored for inactivity', game)
            _deregister_game(game)
        elif game not in IDLE_TRACKERS:
            logging.info('%s is now being monitored for inactivity', game)
            await _register_game(game)
        else:
            logging.debug('Checking idle status for %s', game)
            idle_status = IDLE_TRACKERS[game].check_idle_status()
            previous_idle_status = PREVIOUS_IDLE_STATUSES.get(game)
            # Only react when the status changes - not on every iteration
            if idle_status != previous_idle_status:
                logging.info('Idle status for %s has changed - was %s, now %s',
                             game, previous_idle_status, idle_status)
                if idle_status == IdleStatus.SHUTDOWN:
                    logging.info('Stopping %s due to inactivity')
                    await game_message_service.send_shutdown_notification(bot, game)
                    await game_service.stop(game)
                    await game_message_service.send_shutdown_finished(bot, game)
                if idle_status == IdleStatus.WARNING:
                    await game_message_service.send_shutdown_warning(bot, game)
                if idle_status == IdleStatus.IDLE:
                    await game_message_service.send_idle_message(bot, game)
            PREVIOUS_IDLE_STATUSES[game] = idle_status


def reset_idle_counter(game):
    if game in IDLE_TRACKERS:
        IDLE_TRACKERS[game].reset_count()


async def _register_game(game):
    rcon_client = await rcon_service.get_rcon_client(game)
    IDLE_TRACKERS[game] = IdleTracker(rcon_client)


def _deregister_game(game):
    IDLE_TRACKERS.pop(game, None)
    PREVIOUS_IDLE_STATUSES.pop(game, None)


class IdleStatus(Enum):
    IN_USE = 1
    IDLE = 2
    WARNING = 3
    SHUTDOWN = 4


WARNING_COUNT = 2
SHUTDOWN_COUNT = 3


class IdleTracker():
    def __init__(self, rcon_client):
        self.rcon_client = rcon_client
        self.game_time = self.rcon_client.game_time()
        self.idle_count = 0

    def check_idle_status(self):
        latest_game_time = self.rcon_client.game_time()
        if latest_game_time == self.game_time:
            self.idle_count += 1
            if self.idle_count >= SHUTDOWN_COUNT:
                return IdleStatus.SHUTDOWN
            elif self.idle_count >= WARNING_COUNT:
                return IdleStatus.WARNING
            else:
                return IdleStatus.IDLE
        else:
            self.game_time = latest_game_time
            self.idle_count = 0
            return IdleStatus.IN_USE

    def reset_count(self):
        self.idle_count = 0
