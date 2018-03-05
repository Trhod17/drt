#!/usr/bin/env python3

import os
import sys
import logging
import logging.handlers
from drt.configfile import ConfigFile
from drt.filesystem import FileSystem

log = logging.getLogger(__name__)
# log.setLevel(logging.INFO)
log.setLevel(logging.DEBUG)
# syslog handler
syslog=logging.handlers.SysLogHandler(address = '/dev/log',
        facility=logging.handlers.SysLogHandler.LOG_DAEMON)
f = logging.Formatter('CopyDVD: %(message)s')
syslog.setFormatter(f)
# output to terminal
terminal = logging.StreamHandler()
log.addHandler(syslog)
log.addHandler(terminal)

def copydvd(dvdbackup, dvddevice, cpdir, dvdname):
    cmd = "{} -i {} -o {} -M -n {}".format(dvdbackup, dvddevice, cpdir, dvdname)
    log.debug(cmd)
    ecode = os.system(cmd)
    return ecode

def main(arg):
    exitcode = 1
    log.debug("arg: {}".format(arg))
    cn = len(arg)
    if cn != 2:
        log.debug("length of arg {}".format(cn))
        log.debug("arg: {}".format(arg))
        log.error("incorrect number of parameters supplied, exiting.")
    else:
        cfgfn = ConfigFile()
        cfg = cfgfn.getCfg()
        srcdev=cfg["device"]
        log.debug("src device: {}".format(srcdev))
        outputdir = os.path.expanduser(cfg["outputdir"])
        fs = FileSystem()
        if not fs.makePath(outputdir):
            log.error("failed to make output dir: '{}'".format(outputdir))
        else:
            tmpdir = os.path.expanduser(cfg["tmpdir"])
            if not fs.makePath(tmpdir):
                log.error("failed to make tmp dir: '{}'".format(tmpdir))
            else:
                dvdname = os.path.basename(arg[1]).replace(" ", "_")
                log.info("Copying dvd {} to {}".format(dvdname, tmpdir))
                exitcode = copydvd(cfg["dvdbackup"], cfg["device"], tmpdir, dvdname)
                if exitcode != 0:
                    log.error("error copying dvd, sorry")
                else:
                    tmpname = tmpdir + "/" + dvdname
                    newname = outputdir + "/" + dvdname
                    log.info("Moving dvd to output dir")
                    os.rename(tmpname, newname)
            log.info("CopyDVD: ejecting disc.")
            os.system("{} {}".format(cfg["eject"], cfg["device"]))
    return exitcode

if __name__=="__main__":
    sys.exit(main(sys.argv))