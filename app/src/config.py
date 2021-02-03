#!/usr/bin/env python2
import sys
import os
import yaml
import logger, logging

logger = logging.getLogger(__name__)

# Load Configuration File
def load_config(configFile=os.environ.get('APP_CONFIG_FILE') or "config.yaml"):
    
    # Load The Config File If it Exists
    if os.path.isfile(configFile):
        with open(configFile, 'r') as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logging.error(exc)
                sys.exit(1)
        logger.info("Configuration Successfully Loaded.")

        # Config Override With OS Environment Variables
        config['watcher']['observer']['path'] = os.environ.get('APP_WATCH_DIR') or config['watcher']['observer']['path']
        config['evernote']['api']['token'] = os.environ.get('APP_EVERNOTE_TOKEN') or config['evernote']['api']['token']
        config['evernote']['api']['sandbox'] = os.environ.get('APP_EVERNOTE_SANDBOX') or config['evernote']['api']['sandbox']
        config['evernote']['api']['china'] = os.environ.get('APP_EVERNOTE_CHINA') or config['evernote']['api']['china']

        # Output Final Config
        logger.debug("Loaded Configuration: " + yaml.dump(config))
        return config
    else:
        logger.error("Config File " + configFile + " Does Not Exist!")
        sys.exit(1)
