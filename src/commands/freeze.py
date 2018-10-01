'''
  apkg
  ~~~~

  The Agda Package Manager.

'''

# ----------------------------------------------------------------------------

import click
import logging
import click_log

from pony.orm             import db_session, select

from ..service.database   import db
from ..service.database   import ( Library , LibraryVersion )


# ----------------------------------------------------------------------------

# -- Logger def.
logger = logging.getLogger(__name__)
click_log.basic_config(logger)

# -- Command def.
@click.group()
def freeze(): pass

@freeze.command()
@click_log.simple_verbosity_option(logger)
@db_session
def freeze():
  """List of installed packages."""

  for library in select(l for l in Library if l.installed):
    installedVersion = library.getInstalledVersion()    
    if installedVersion is not None:
      logger.info(installedVersion.freezeName)