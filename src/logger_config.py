import logging
import logging.config
import yaml
import os

#Configure the loggers:
#OBS: When a module is imported multiple times, its code is executed only the first time.
script_dir    = os.path.dirname(__file__)
rel_path      = "../conf/logger_config.yaml"
abs_file_path = os.path.join(script_dir, rel_path)
with open(abs_file_path, 'r') as f:
    logger_config_dict = yaml.safe_load(f)
    logging.config.dictConfig(logger_config_dict)



