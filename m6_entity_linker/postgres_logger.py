import time

import psycopg2
from psycopg2.extras import LoggingConnection, LoggingCursor

class LinkerLoggingCursor(LoggingCursor):
    def execute(self, query, vars=None):
        self.timestamp = time.time()
        return super(LinkerLoggingCursor, self).execute(query, vars)

    def callproc(self, procname, vars=None):
        self.timestamp = time.time()
        return super(LinkerLoggingCursor, self).callproc(procname, vars)

class LinkerLoggingConnection(LoggingConnection):
    def filter(self, msg, curs):
        return msg.decode(psycopg2.extensions.encodings[self.encoding], 'replace') + "   %d ms" % int((time.time() - curs.timestamp) * 1000)

    def cursor(self, *args, **kwargs):
        kwargs.setdefault('cursor_factory', LinkerLoggingCursor)
        return LoggingConnection.cursor(self, *args, **kwargs)
