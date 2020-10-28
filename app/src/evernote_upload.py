#!/usr/bin/env python2
import os
import hashlib
import sys
import logging
import logger
from evernote.api.client import EvernoteClient
import evernote.edam.type.ttypes as Types
import evernote.edam.userstore.constants as UserStoreConstants
from evernote.edam.error.ttypes import EDAMUserException
from evernote.edam.error.ttypes import EDAMSystemException
from evernote.edam.error.ttypes import EDAMNotFoundException
from evernote.edam.error.ttypes import EDAMErrorCode

logger = logging.getLogger(__name__)

class EvernoteUpload(object):
    def __init__(self, dev_token):
        self._connect_to_evernote(dev_token)

    def _connect_to_evernote(self, dev_token):
        user = None
        try:
            self.client = EvernoteClient(token=dev_token)
            self.user_store = self.client.get_user_store()
            user = self.user_store.getUser()
        except EDAMUserException as e:
            err = e.errorCode
            logger.error("Error attempting to authenticate to Evernote: %s - %s" % (EDAMErrorCode._VALUES_TO_NAMES[err], e.parameter))
            return False
        except EDAMSystemException as e:
            err = e.errorCode
            logger.error("Error attempting to authenticate to Evernote: %s - %s" % (EDAMErrorCode._VALUES_TO_NAMES[err], e.message))
            sys.exit(-1)

        if user:
            logger.info("Authenticated to evernote as user %s" % user.username)
            return True
        else:
            return False

    def _get_notebooks(self):
        note_store = self.client.get_note_store()
        notebooks = note_store.listNotebooks()
        return {n.name:n for n in notebooks}

    def _create_notebook(self, notebook):
        note_store = self.client.get_note_store()
        return note_store.createNotebook(notebook)

    def _update_notebook(self, notebook):
        note_store = self.client.get_note_store()
        note_store.updateNotebook(notebook)
        return

    def _check_and_make_notebook(self, notebook_name, stack=None):
        notebooks = self._get_notebooks()
        if notebook_name in notebooks:
            # Existing notebook, so just update the stack if needed
            notebook = notebooks[notebook_name]
            if stack:
                notebook.stack = stack
                self._update_notebook(notebook)
            return notebook
        else:
            # Need to create a new notebook
            notebook = Types.Notebook()
            notebook.name = notebook_name
            if stack:
                notebook.stack = stack
            notebook = self._create_notebook(notebook)
            return notebook

    def _create_evernote_note(self, notebook, filename, noteMetadata):
        # Create the new note
        note = Types.Note()
        note.title = noteMetadata['title']
        note.notebookGuid = notebook.guid
        note.content = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
        note.content += '<en-note>' + noteMetadata['message']
        note.tagNames = noteMetadata['tags']
       
        # Calculate the md5 hash of the pdf
        md5 = hashlib.md5()
        with open(filename,'rb') as f: 
            pdf_bytes = f.read()
        md5.update(pdf_bytes)
        md5hash = md5.hexdigest()

        # Create the Data type for evernote that goes into a resource
        pdf_data = Types.Data()
        pdf_data.bodyHash = md5hash
        pdf_data.size = len(pdf_bytes) 
        pdf_data.body = pdf_bytes

        # Add a link in the evernote boy for this content
        link = '<en-media type="application/pdf" hash="%s"/>' % md5hash
        note.content += link
        note.content += '</en-note>'
        
        # Create a resource for the note that contains the pdf
        pdf_resource = Types.Resource()
        pdf_resource.data = pdf_data
        pdf_resource.mime = "application/pdf"
        
        # Create a resource list to hold the pdf resource
        resource_list = []
        resource_list.append(pdf_resource)

        # Set the note's resource list
        note.resources = resource_list

        return note

        
    def upload_to_notebook(self, filename, noteMetadata):
        # Check if the evernote notebook exists
        logger.info("Checking for notebook named %s" % noteMetadata['notebook'])
        notebook = self._check_and_make_notebook(noteMetadata['notebook'])

        logger.info("Uploading %s to %s" % (filename, noteMetadata['notebook']))
        
        note = self._create_evernote_note(notebook, filename, noteMetadata)

        # Store the note in evernote
        note_store = self.client.get_note_store()
        note = note_store.createNote(note)
