#!/usr/bin/env python2
import time
import os
import sys
import logging
import logger
import config
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from evernote_upload import EvernoteUpload

logger = logging.getLogger(__name__)
logger.info("Evernote Directory Watcher - Starting Application...")
processed=[]
config = config.load_config()

# Detect New Files In Directory - Wait For Files To Complete Before Uploading
def new_file_detected(event):
    if event.src_path not in processed:
        processed.append(event.src_path)
        logger.info("File Creation Detected. Waiting For " + event.src_path + " To Be Closed.")
        old_size = -1
        current_size = 0
        while current_size != old_size:
            old_size = current_size
            time.sleep(config['watcher']['observer']['modifyLoop'] or 1)
            current_size = os.stat(event.src_path).st_size
        logger.info("The File " + event.src_path + " Has Been Closed. Completed File size: " + '{:,}'.format(current_size) + " bytes")

        metadata = {
            'title': config['evernote']['note']['title'],
            'tags': config['evernote']['note']['tags'],
            'notebook': config['evernote']['notebook']['destination'],
            'message': '<br/><b>Filename:</b> '+os.path.basename(event.src_path)+'<br/><b>File Size:</b>'+'{:,}'.format(current_size)+'<br/><br/>'
        }

        # Upload Note To Evernote
        note = EvernoteUpload(config['evernote']['api']['token'])
        note.upload_to_notebook(event.src_path, metadata)
        os.remove(event.src_path)

# Detect File Deletion Events
def delete_file(event):
    logger.info("The File " + event.src_path + " Has Been Deleted.")
    if event.src_path in processed:
        processed.remove(event.src_path)

# Main Function
def main():

    # Configure Directory Watchdog
    logger.info("Configuring Directory Handler...")
    handler = PatternMatchingEventHandler(
        config['watcher']['patternMatching']['extensions'],
        config['watcher']['patternMatching']['ignorePatterns'],
        config['watcher']['patternMatching']['ignoreDirectories'],
        config['watcher']['patternMatching']['caseSensitive']
        )
    handler.on_modified = new_file_detected
    handler.on_deleted = delete_file
    
    # Create Watch Path If It Doesn't Exist
    if not os.path.isdir(config['watcher']['observer']['path']):
        os.mkdir(config['watcher']['observer']['path'])

    # Configure Observer
    logger.info("Configuring Directory Observer...")
    observer = Observer()
    observer.schedule(
        handler,
        config['watcher']['observer']['path'],
        config['watcher']['observer']['recursive']
    )

    # Start Loop
    logger.info("Startup Complete. Waiting For Directory Events.")
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        logger.info("User Interrupt Detected - Shutting Down Evernote Directory Watcher.")


# Main Start
if __name__ == "__main__":
    main()
