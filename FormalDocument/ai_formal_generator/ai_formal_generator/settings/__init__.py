"""Settings package entry point.

Imports the correct environment settings based on DJANGO_SETTINGS_MODULE.
When DJANGO_SETTINGS_MODULE points to this package (ai_formal_generator.settings),
it defaults to the development configuration.
"""

from .development import *  # noqa: F401,F403

