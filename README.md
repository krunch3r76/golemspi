# golemspi
overlay for summary of live golem provider console output. this is a work in progress and besides having a terribly ugly view it will probably break.

# video demonstration
to be continued...

# downloading
```bash
$ git clone https://github.com/krunch3r76/golemspi.git
$ cd golemspi
(./golemspi) $
```
# checking for updates
```bash
(./golemspi) $ git pull
```

# example usage
```bash
(./golemspi) $ golemsp run 2>&1 | ./golemspi.py
```

## notes / issues
scrolling is enabled if you use a log file intermediate. enabling scrolling while piping (as in the example usage) may not be feasible.
```bash
$ golemsp run 2>&1 | tee -a /tmp/golemsp.log
(./golemspi) $ ./golemspi.py /tmp/golemsp.log
```
