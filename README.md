# Evernote Directory Watcher

![Docker Cloud Automated build](https://img.shields.io/docker/cloud/automated/geoffh1977/evernote-watcher?style=plastic) ![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/geoffh1977/evernote-watcher?style=plastic) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/geoffh1977/evernote-watcher/latest?style=plastic) ![Docker Pulls](https://img.shields.io/docker/pulls/geoffh1977/evernote-watcher?style=plastic)

The Evernote Directory Watcher is a Python based application which monitors a single directory and uploads any files matching a set of file extensions as a new note in Evernote. The application is an improvement over my previous application _Evernote Monitor_ which had a number of issues.

## Issues and Improvements
A previous project name _Evernote Monitor_ provided the same function as the new _Evernote Watcher_, however, a number of issues have been addressed and improvements made to the base code and configuration:

|                Issue                | Issue With Evernote Monitor                                  | Fix In Evernote Watcher                                      |
| ----------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
|         **Script Language**         | Originally written in bash which only provided limited functionality | Python based re-write with opens up the application to new possibilities. |
|      **Document Transmission**      | Documents were sent to Evernote via SMTP (email). This was an insecure method for sending confidential documents. | Documents are now sent via the Evernote API directly to Evernote. Communications is encrypted from the application to the cloud service. |
|        **Files Not Closed**         | Files would always be sent every 60 seconds, even if the files being written to were incomplete. This resulted in damaged files in Evernote. | Files are now monitored for closure. Files will only be uploaded when the file is closed. |
|    **File Extension Monitoring**    | All files in the monitored path were sent to Evernote. File type didn't matter. | A list of extensions is provided to the application via a config file. Only matching file types are sent. |
| **Recursive Directory Monitoring**  | Directories under the top level monitoring directory were not monitored. | Recursive monitoring is now available as an option in the config file. |
| **Evernote Destination Hard Coded** | The Evernote target notebook and tags were hard coded into the script and required re-writing/re-compiling to change the details. | The Evernote target information is now stored in an external config file. |
|                                     |                                                              |                                                              |

Other issues exist in the previous version of the software, these are just the issues that were first detected and seem to cause the most problems.

## Running The Application

### Pre-requisites

In order to run the application, the following pre-requisites are required:

- **A version of Docker** - If you want to constantly monitor a directory path, this will need to be running on a 24/7 server where files are copied too.
- **An Evernote API key** - A Sandbox API key will work for testing purposes, but for sending documents to the _normal_ Evernote account, it will need to be a Production API key.
- **A configuration file** - A pre-created configuration file which is written for your purposes
- **Application Docker Image** - The docker image itself. Available on Docker Hub.

### Getting An Evernote API Key

As the main intention was to use the application for a small circle of users, OAuth functionality has not been included in the code. As such, an Evernote API key is required for the application to function. To get an API key:

1. Goto the [Development Evernote Website](https://dev.evernote.com/).
2. Apply for a new API key by selecting the "Get An API Key" from the top-right corner. Fill out the form and get your key.
3. Got the [API Token Link] (https://dev.evernote.com/get-token/). You can get a token for the Testing Sandbox straight away via this link.
4. To use the API key in _production_ evernote - Fill out the form on their [FAQ] (https://dev.evernote.com/support/faq.php) page. It is located under _"How do I copy my API key from Sandbox to www (production)?"_
5. Once activated - return to the [API Token Link] (https://dev.evernote.com/get-token/) and select the _production_ option when generating the key and linking your evernote account.

If enough users are interested, OAuth may be added in the future to skip all these steps.
### Application configuration

The application configuration is needed before running the docker image. Without the configuration file, an error will just be generated stating there is "no configuration file". Below is an example of a configuration file. Most fields should be self explanatory - simply copy and paste this config and adjust for your purposes.

_Example Application Configuration:_

```yaml
watcher:
  patternMatching:
    extensions:
      - '*.pdf'
      - '*.txt'
      - '*.doc'
    ignorePatterns: ''
    ignoreDirectories: True
    caseSensitive: True
  observer:
    path: '/watch'
    recursive: False
    modifyLoop: 1

evernote:
  api:
    token: 'YOUR_EVERNOTE_TOKEN'
    sandbox: True
    china: False
  notebook:
    destination: 'INBOX'
  note:
    title: Uploaded Document
    tags:
      - Tag1
      - Tag2
```


### Starting the application

Once the pre-requisites have been met, it is time to start the application itself. In order to start the latest copy of the application in interactive mode, simply run the following:

```bash
docker run -it --rm -v <CONFIG FILE LOCATION>:/app/config.yaml:ro -v <WATCH DIRECTORY>:/watch geoffh1977/evernote-watcher
```

The command contains a couple of parts that need filling in at runtime:

* **CONFIG FILE LOCATION** - This is the location of the YAML configuration file which is to be run with the application. For example, '/tmp/config.yaml' or something similar
* **WATCH DIRECTORY** - The directory on the host which is to be monitored. For example, '/tmp/watch' or something similar.

The above command will execute the application based on your configuration file and mount a host path into the running docker container for monitoring. There may be cases where a host path mount is not needed (e.g. Kubernetes NFS mounting, etc) but that is beyond the scope of the current document.

Other environment variables that can be passed to docker at startup to modify the application settings are also avilable:

| Environment Variable | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| **APP_CONFIG_FILE**  | Changes the location of the config.yaml file in the application container itself. |
| **APP_WATCH_DIR**    | Changes the location of the watch directory in the application container. |
| **EVERNOTE_API_KEY** | An override so the Evernote API Key can be passed as a variable at startup. |
| **EVERNOTE_API_SANDBOX** | An override to tell the API to use the sandbox or production servers. |
| **EVERNOTE_API_CHINA** | An override to use the international servers or servers in China. |

 Using these options, a more complex start-up of the application may look like this:

```bash
docker run -d -v /tmp/configs:/config:ro -v /tmp/watch:/monitor -e APP_CONFIG_FILE=/config/production.yaml -e APP_WATCH_DIR=/monitor -e EVERNOTE_API_KEY=abcdef12345678 geoffh1977/evernote-watcher
```

This command will place the docker container in the background, mount a config directory in the container, select a specific config file in the config path, change the watch directory in the container, and pass in an external Evernote API key to the application.



## Frequently Asked Questions

### Why write the application itself

This query has come up a couple of times, and I mainly write this software for my own benefit.

Originally, when paying for the premium Evernote account, I was being sent e-mail about scanners that had a _One Touch Scanning_ option to send files directly to Evernote. My home network has a Brother MFC9970CDW - a large multipurpose printer/scanner with a document feeder.

While wanting the functionality, replacing the MFC was not something I was willing to do. Even though the scanner did not have the Evernote options, it did have the ability to save files directly to an SMB/CIFS share. By watching this path from the docker container, any scanned files are uploaded to Evernote without the need for a new scanner or complex setup. This essentially gives me the _One Touch Scanning_ option for Evernote by simply using the scanner console.

### Why write it as a docker image

My entire home server setup is running on Docker, this includes services such as media, home automation, and even a Minecraft server for my kids. As such, putting the application in a docker image for my use case makes perfect sense.

### How does the application actually work

The Evernote Watcher application monitors the targeted path for iNotify events from the filesystem, specifically file modifications and deletions. Files which already exist in the directory before the application starts will not be uploaded unless they are modified after the application has started.

Once a file modification has been detected, the application ensures that the file size no longer changes over a period of time, set by the _modifyLoop_ config variable. If the file size is the same for both checks, the file is assumed to be closed.

The application then authenticates with the Evernote API using the provided API key and creates a new note with the file attached. The original file is then deleted from the watch path.

### I've found an issue or have an improvement idea, can I contact you

Of course, feel free. It might take me a little time to get back with my other obligations, but I'll definitely look into any improvement requests or new features as they benefit me as well.

