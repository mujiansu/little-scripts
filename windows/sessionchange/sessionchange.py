# -*- coding: utf-8 -*-
import win32serviceutil
import win32service
import win32event
import servicemanager
import os  
import inspect  
import logging 
from logging.handlers import RotatingFileHandler

WTS_SESSION_LOGON = (0x5)
WTS_SESSION_LOGOFF = (0x6)
WTS_SESSION_LOCK = (0x7)
WTS_SESSION_UNLOCK = (0x8)


class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "SessionChangeService"
    _svc_display_name_ = "SessionChange Service"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        
        logPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "./service-log.log"
        self._logger = logging.getLogger("SessionChangeService")
        self._logger.setLevel(logging.DEBUG)
        handler = RotatingFileHandler(logPath, maxBytes=4096, backupCount=10)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)


    def GetAcceptedControls(self):
        rc = win32serviceutil.ServiceFramework.GetAcceptedControls(self)
        rc |= win32service.SERVICE_ACCEPT_SESSIONCHANGE
        return rc

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.main()

    def SvcOtherEx(self, control, event_type, data):
        if control == win32service.SERVICE_CONTROL_SESSIONCHANGE:
            if event_type == WTS_SESSION_LOCK:
                self._logger.info("lock")
            if event_type == WTS_SESSION_UNLOCK:
                self._logger.info("unlock")
            if event_type == WTS_SESSION_LOGON:
                self._logger.info("logon")
            if event_type == WTS_SESSION_LOGOFF:
                self._logger.info("logoff")

    def main(self):
        rc = None
        while rc != win32event.WAIT_OBJECT_0:
            rc = win32event.WaitForSingleObject(self.hWaitStop, (1 * 60 * 1000))


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)