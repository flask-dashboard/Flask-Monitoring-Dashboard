import threading

from flask_monitoringdashboard.core.get_ip import get_ip
from flask_monitoringdashboard.core.group_by import get_group_by
from flask_monitoringdashboard.core.profiler.base_profiler import BaseProfiler
from flask_monitoringdashboard.core.profiler.outlier_profiler import OutlierProfiler
from flask_monitoringdashboard.core.profiler.performance_profiler import PerformanceProfiler
from flask_monitoringdashboard.core.profiler.stacktrace_profiler import StacktraceProfiler


def start_thread_last_requested(endpoint):
    """
    Starts a thread that updates the last_requested time in the database.
    :param endpoint: Endpoint object
    """
    BaseProfiler(endpoint).start()


def start_performance_thread(endpoint, duration, status_code):
    """
    Starts a thread that updates performance, utilization and last_requested in the database.
    :param endpoint: Endpoint object
    :param duration: duration of the request
    :param status_code: HTTP status code of the request
    """
    group_by = get_group_by()
    PerformanceProfiler(endpoint, get_ip(), duration, group_by, status_code).start()


def start_profiler_thread(endpoint):
    """ Starts a thread that profiles the main thread. """
    current_thread = threading.current_thread().ident
    group_by = get_group_by()
    thread = StacktraceProfiler(current_thread, endpoint, get_ip(), group_by)
    thread.start()
    return thread


def start_outlier_thread(endpoint):
    """ Starts a thread that collects outliers."""
    current_thread = threading.current_thread().ident
    group_by = get_group_by()
    thread = OutlierProfiler(current_thread, endpoint, get_ip(), group_by)
    thread.start()
    return thread


def start_profiler_and_outlier_thread(endpoint):
    """ Starts two threads: PerformanceProfiler and StacktraceProfiler.  """
    current_thread = threading.current_thread().ident
    ip = get_ip()
    group_by = get_group_by()
    outlier = OutlierProfiler(current_thread, endpoint, ip, group_by)
    thread = StacktraceProfiler(current_thread, endpoint, ip, group_by, outlier)
    thread.start()
    outlier.start()
    return thread
