#!/usr/bin/env python2

import time
import logging
import os
import subprocess
import sys

import serverutils


"""
Servermanager for fuzzing target

The main interaction with the fuzzing target process. This object
will start the server (target), stop it etc.
"""

GLOBAL_SLEEP = {
    # how long to wait after server start
    # can be high as it is not happening so often
    "sleep_after_server_start": 1,
}


class SimpleServerManager(object):
    """
        Manages all interaction with the server (the fuzzing target)
        This includes:
            - handling the process (start, stop)
            - network communication
    """

    def __init__(self, config, threadId, targetPort):
        self.config = config
        self.process = None
        self.targetPort = targetPort
        serverutils.setupEnvironment(self.config)


    def start(self):
        """Start the server"""
        if not os.path.isfile(self.config["target_bin"]):
            logging.error("Could not find target file: " + str(self.config["target_bin"]))
            sys.exit(1)
        self.process = self._runTarget()
        logging.info("Start server PID: " + str(self.process.pid))


    def stop(self):
        """Stop the server"""
        logging.info("Stop server PID: " + str(self.process.pid))
        self.process.terminate


    def restart(self):
        self.stop()
        time.sleep(GLOBAL_SLEEP["sleep_after_server_start"])
        self.start()
        time.sleep(GLOBAL_SLEEP["sleep_after_server_start"])


    def isStarted(self):
        """Return true if server is started"""


    def _waitForServer(self):
        """
        Blocks until server is alive
        Used to block until it really started
        """


    def _runTarget(self):
        """
        Start the server
        """
        global GLOBAL_SLEEP
        popenArg = serverutils.getInvokeTargetArgs(self.config, self.targetPort)
        logging.info("Starting server with args: " + str(popenArg))

        os.chdir( self.config["projdir"] + "/bin")
        # create devnull so we can us it to surpress output of the server (2.7 specific)
        DEVNULL = open(os.devnull, 'wb')
        p = subprocess.Popen(popenArg, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
        time.sleep( GLOBAL_SLEEP["sleep_after_server_start"] )  # wait a bit so we are sure server is really started
        logging.info("  Pid: " + str(p.pid) )

        return p


    def getCrashData(self):
        """
        Return the data of the crash
        or None if it has not crashed (should not happen)
        """

        if self.process.poll():
            logging.info("getCrashData(): get data, but server alive?!")
        else:
            logging.info("getCrashData(): ok, server is really crashed")

        crashData = {
            'asanOutput': serverutils.getAsanOutput(self.config, self.process.pid),
            'signum': 0,
            'exitcode': 0,
            'reallydead': self.process.poll(),
            'serverpid': self.process.pid,
        }

        return crashData
