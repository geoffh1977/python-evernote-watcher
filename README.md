# Evernote Directory Watcher

Read Me Is A Work In Progress!

Example Application Configuration:

```python
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
    path: '/tmp/upload'
    recursive: False
    modifyLoop: 1

evernote:
  api:
    token: 'YOUR_EVERNOTE_TOKEN'
  notebook:
    destination: 'INBOX'
  note:
    title: Uploaded Document
    tags:
      - Tag1
      - Tag2
```

