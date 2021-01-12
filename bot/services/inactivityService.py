from enum import Enum
import logging
from ..services import gameService, gameMessageService, rconService
from ..clients import rconClient
from ..helpers import statusHelper


idle_trackers = {}
previous_idle_statuses = {}

async def auto_shutdown_loop(bot):
  global idle_trackers, previous_idle_statuses
  logging.info('Running auto-shutdown loop')
  games = await gameService.list_games()
  for game in games:
    status = games[game]
    if status != statusHelper.Status.RUNNING:
      logging.info('%s is no longer running so will not be monitored for inactivity', game)
      _deregister_game(game)
    elif game not in idle_trackers:
      logging.info('%s is now being monitored for inactivity', game)
      await _register_game(game)
    else:
      logging.debug('Checking idle status for %s', game)
      idle_status = idle_trackers[game].check_idle_status()
      previous_idle_status = previous_idle_statuses.get(game)
      # Only react when the status changes - not on every iteration
      if idle_status != previous_idle_status:
        logging.info('Idle status for %s has changed - was %s, now %s', game, previous_idle_status, idle_status)
        if idle_status == IdleStatus.SHUTDOWN:
          logging.info('Stopping %s due to inactivity')
          await gameMessageService.send_shutdown_notification(bot, game)
          await gameService.stop(game)
          await gameMessageService.send_shutdown_finished(bot, game)
        if idle_status == IdleStatus.WARNING:
          await gameMessageService.send_shutdown_warning(bot, game)
        if idle_status == IdleStatus.IDLE:
          await gameMessageService.send_idle_message(bot, game)
      previous_idle_statuses[game] = idle_status

def reset_idle_counter(game):
  if game in idle_trackers:
    idle_trackers[game].reset_count()

async def _register_game(game):
  rcon_client = await rconService.get_rcon_client(game)
  idle_trackers[game] = IdleTracker(rcon_client)

def _deregister_game(game):
  idle_trackers.pop(game, None)
  previous_idle_statuses.pop(game, None)


class IdleStatus(Enum):
  IN_USE = 1
  IDLE = 2
  WARNING = 3
  SHUTDOWN = 4


warning_count = 2
shutdown_count = 3

class IdleTracker():
  def __init__(self, rcon_client):
    self.rcon_client = rcon_client
    self.game_time = self.rcon_client.game_time()
    self.idle_count = 0

  def check_idle_status(self):
    latest_game_time = self.rcon_client.game_time()
    if (latest_game_time == self.game_time):
      self.idle_count += 1
      if self.idle_count >= shutdown_count:
        return IdleStatus.SHUTDOWN
      elif self.idle_count >= warning_count:
        return IdleStatus.WARNING
      else:
        return IdleStatus.IDLE
    else:
      self.game_time = latest_game_time
      self.idle_count = 0
      return IdleStatus.IN_USE
  
  def reset_count(self):
    self.idle_count = 0