# https://gist.github.com/dorneanu/cce1cd6711969d581873a88e0257e312

from typing import Any
import plugins
from cubedpandas.cube import Cube
from cubedpandas.measure import Measure

class PluginA(plugins.Base):

    def __init__(self):
        pass

    def start(self):
        print("Plugin A")

    def resolve(self, cube: Cube, address: Any, measure: str | Measure | None = None):
        print("Plugin A")
        return cube