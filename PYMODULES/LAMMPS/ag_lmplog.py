#!/usr/bin/env python
from __future__ import print_function, division
import collections
import log_universe as logu

__version__ = "2018-02-07"


class LmpLog(logu.LogUniverse):
    """
    Class for reading log.lammps file(s).
    """
    def __init__(self):
        logu.LogUniverse.__init__(self)

    def read_lmplog(self, *lmplogs):
        """
        Read a log.lammps file with one or more thermo entries.
        """
        for lmplog in lmplogs:
            with open(lmplog, "r") as log_in:
                line = log_in.readline()
                #eof = False  # end of file

                while line != '':
                    # starting point of thermo-output
                    if (line.startswith("Memory usage per processor") or
                       line.startswith("Per MPI rank memory allocation")):

                        # deploy containers for the data to come
                        thermo_line = log_in.readline()
                        keys = thermo_line.split()

                        # prepare current container
                        cdata = collections.OrderedDict(
                            zip(keys, [[] for i in xrange(len(keys))])
                        )

                        # read further lines until end of run is reached
                        line = log_in.readline()

                        while line.startswith("Loop time of") is False and line.startswith("WARNING: Wall time limit reached") is False and line != '':
                            values = [float(i) for i in line.split()]

                            for key, value in zip(keys, values):
                                cdata[key].append(value)

                            line = log_in.readline()

                        self.data.append(cdata)

                    line = log_in.readline()

        self._int_values()

    def add_log(self, log_to_add):
        """
        Add data from another log-file to current log-file.
        """
        log = LmpLog()
        log.read_lmplog(log_to_add)
        self.data.extend(log.data)