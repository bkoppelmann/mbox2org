This script extracts calendar entries out of a maildir and puts them into one org mode file.
This is based on [ical2org](https://github.com/asoroa/ical2org.py) and uses part of its source code.

# Setup
Right now it expects ical2org to be installed locally
```
$ pip3 install --user ical2org
$ git clone https://github.com/bkoppelmann/mbox2org.git
$ ln -s mbox2org/mbox2org.py ~/.local/bin/
```

# Usage
Give it a maildir folder with `--folder` and a path with `--output` where the org file should be created.
```
$ mbox2org --folder <maildir> --output <cal.org>
```
