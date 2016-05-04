# TODO Find a common location for debug tools used by all python AI, and engine
#      Meanwhile this is a copy-hack-paste of AI/freeorion_debug/timers

import os
from time import time
# from option_tools import get_option_dict, check_bool, DEFAULT_SUB_DIR
# from option_tools import TIMERS_TO_FILE, TIMERS_USE_TIMERS, TIMERS_DUMP_FOLDER
import sys

import freeorion as fo

# setup module
# options = get_option_dict()

USE_TIMERS = True #check_bool(options[TIMERS_USE_TIMERS])
DUMP_TO_FILE = False #check_bool(options[TIMERS_TO_FILE])
# TIMERS_DIR = os.path.join(fo.getUserDataDir(), DEFAULT_SUB_DIR, options[TIMERS_DUMP_FOLDER])


def make_header(*args):
    return ['%-8s ' % x for x in args]


# def _get_timers_dir():
#     try:
#         if os.path.isdir(fo.getUserDataDir()) and not os.path.isdir(TIMERS_DIR):
#             os.makedirs(TIMERS_DIR)
#     except OSError:
#         sys.stderr.write("AI Config Error: could not create path %s\n" % TIMERS_DIR)
#         return False

#     return TIMERS_DIR


class DummyTimer(object):
    """
    Dummy timer to be called if no need any logging.
    """
    def __init__(self, *args, **kwargs):
        pass

    def stop(self, *args, **kwargs):
        pass

    def start(self, *args, **kwargs):
        pass

    def end(self):
        pass


class LogTimer(object):
    def __init__(self, timer_name, write_log=False):
        """
        Creates timer. Timer name is name that will be in logs header and part of filename if write_log=True
        If write_log true and timers logging enabled (DUMP_TO_FILE=True) save timer info to file.

        """
        self.timer_name = timer_name
        self.start_time = None
        self.section_name = None
        self.timers = []
        self.write_log = False # write_log
        self.headers = None
        self.log_name = None

    def stop(self, section_name=''):
        """
        Stop timer if running. Specify section_name if want to override its name.
        """
        if self.start_time:
            self.end_time = time()
            section_name = section_name or self.section_name
            self.timers.append((section_name, (self.end_time - self.start_time) * 1000.0))
        self.start_time = None
        self.section_name = None

    def start(self, section_name):
        """
        Stop prev timer if present and starts new.
        """
        self.stop()
        self.section_name = section_name
        self.start_time = time()

    def _write(self, text):
        if not _get_timers_dir():
            return
        if not self.log_name:
            self.log_name = os.path.join(_get_timers_dir(), '%s.txt' % (self.timer_name))
            mode = 'w'  # empty file
        else:
            mode = 'a'
        with open(self.log_name, mode) as f:
            f.write(text)
            f.write('\n')

    def print_flat(self):
        """
        Output result.
        """
        if not self.timers:
            return
        max_header = max(len(x[0]) for x in self.timers)
        line_max_size = max_header + 14
        print
        print ('Timing for %s:' % self.timer_name)
        print '=' * line_max_size
        for name, val in self.timers:
            print "%-*s %8d msec" % (max_header, name, val)
        print '-' * line_max_size
        print ("Total: %8d msec" % sum(x[1] for x in self.timers)).rjust(line_max_size)


    def print_aggregate(self):
        """
        Print aggregated results for each section
        """
        if not self.timers:
            return
        max_header = max(len(x[0]) for x in self.timers)
        line_max_size = max_header + 14
        print
        print ('Timing for %s:' % self.timer_name)
        print '=' * line_max_size

        accumulated_times = {}
        ordered_names = []
        for name, val in self.timers:
            if not accumulated_times.has_key(name):
                ordered_names.append(name)
                accumulated_times[name] = 0
            accumulated_times[name] += val
        for name in ordered_names:            
            print "%-*s %8d msec" % (max_header, name, accumulated_times[name])
        print '-' * line_max_size
        print ("Total: %8d msec" % sum(x[1] for x in self.timers)).rjust(line_max_size)

    def end(self):
        """
        Stop timer, output result, clear checks.
        If dumping to file, if headers are not match to prev, new header line will be added.
        """
        self.stop()
        self.print_flat()
        self.timers = []  # clear times
        
Timer = LogTimer if True else DummyTimer
