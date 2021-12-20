from enum import Enum
import logging
from ..services import game_service, game_message_service, rcon_service
from ..helpers import status_helper
from ..exceptions import InvalidOperationException


IDLE_TRACKERS = {}
PREVIOUS_IDLE_STATUSES = {}


async def auto_shutdown_loop(bot):
    logging.info('Running auto-shutdown loop')
    games = await game_service.list_games()
    for game in games:
        status = games[game]
        if status != status_helper.Status.RUNNING:
            logging.info(
                '%s is not running so will not be monitored for inactivity', game)
            _deregister_game(game)
        elif game not in IDLE_TRACKERS:
            logging.info('%s is now being monitored for inactivity', game)
            await _register_game(game)
        else:
            logging.info('Checking idle status for %s', game)
            idle_status = IDLE_TRACKERS[game].check_idle_status()
            previous_idle_status = PREVIOUS_IDLE_STATUSES.get(game)

            if idle_status == previous_idle_status:
                logging.info(
                    'No change in idle status for %s - still %s', game, idle_status)
                return

            # Only react when the status changes - not on every iteration
            logging.info('Idle status for %s has changed - was %s, now %s',
                         game, previous_idle_status, idle_status)
            PREVIOUS_IDLE_STATUSES[game] = idle_status
            if idle_status == IdleStatus.SHUTDOWN or idle_status == IdleStatus.UNKNOWN_SHUTDOWN:
                logging.info('Stopping %s due to inactivity', game)
                await game_message_service.send_shutdown_notification(bot, game)
                try:
                    force = previous_idle_status == IdleStatus.SHUTDOWN_FAILED
                    logging.info('Stopping %s with force=%s', game, force)
                    await game_service.stop(game, force)
                    await game_message_service.send_shutdown_finished(bot, game)
                except InvalidOperationException:
                    await game_message_service.send_shutdown_failed(bot, game)
                    logging.error(
                        'Failed to stop %s, will use force next time', game)
                    PREVIOUS_IDLE_STATUSES[game] = IdleStatus.SHUTDOWN_FAILED
            if idle_status == IdleStatus.UNKNOWN:
                await game_message_service.send_unknown_idle_status_message(bot, game)
            if idle_status == IdleStatus.WARNING:
                await game_message_service.send_shutdown_warning(bot, game)
            if idle_status == IdleStatus.IDLE:
                await game_message_service.send_idle_message(bot, game)


def reset_idle_counter(game):
    if game in IDLE_TRACKERS:
        IDLE_TRACKERS[game].reset_count()
        PREVIOUS_IDLE_STATUSES[game] = None


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
    UNKNOWN = 5
    UNKNOWN_SHUTDOWN = 6
    SHUTDOWN_FAILED = 7


WARNING_COUNT = 2
SHUTDOWN_COUNT = 3

UNKNOWN_SHUTDOWN_COUNT = 3


class IdleTracker():
    def __init__(self, rcon_client):
        self.rcon_client = rcon_client
        self.game_time = None
        self.idle_count = 0
        self.unknown_count = 0

    def check_idle_status(self):
        try:
            latest_game_time = self.rcon_client.game_time()
            self.unknown_count = 0
            if latest_game_time == self.game_time:
                self.idle_count += 1
                if self.idle_count >= SHUTDOWN_COUNT:
                    return IdleStatus.SHUTDOWN
                if self.idle_count >= WARNING_COUNT:
                    return IdleStatus.WARNING
                return IdleStatus.IDLE
            self.game_time = latest_game_time
            self.idle_count = 0
            return IdleStatus.IN_USE
        except Exception:  # pylint: disable=broad-except
            self.unknown_count += 1
            if self.unknown_count >= UNKNOWN_SHUTDOWN_COUNT:
                return IdleStatus.UNKNOWN_SHUTDOWN
            return IdleStatus.UNKNOWN

    def reset_count(self):
        self.idle_count = 0
        self.unknown_count = 0
