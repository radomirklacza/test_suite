import setup.environment
import setup.analyze
import config
import test.user
import test.page
import test.piuser
import test.institution
import test.project
from config import piuser
import test.error as error

class instance:
    def __init__(self, config, scenario):
        self.config = config
        self.scenario = scenario


