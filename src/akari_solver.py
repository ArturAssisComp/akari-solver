import logging
import logger_config


basic_logger = logging.getLogger('basic_logger')

class AkariSolver(object):
    def __init__(self):
        pass

    def hello_world(self):
        basic_logger.info("Hello World")



if __name__=='__main__':
    my_client = AkariSolver()
    my_client.hello_world()
