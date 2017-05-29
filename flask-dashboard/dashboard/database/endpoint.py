"""
Contains all functions that access a single endpoint
"""
from sqlalchemy import func, text
from sqlalchemy.orm.exc import NoResultFound
import datetime

from dashboard import config
from dashboard.database import session_scope, FunctionCall, MonitorRule


def get_line_results(endpoint):
    with session_scope() as db_session:
        query = text("""select
                datetime(CAST(strftime('%s', time)/3600 AS INT)*3600, 'unixepoch') AS newTime, 
                avg(execution_time) AS avg,
                min(execution_time) as min,
                max(execution_time) as max,
                count(execution_time) as count
            from functioncalls 
            where endpoint=:val group by newTime""")
        result = db_session.execute(query, {'val': endpoint})
        data = result.fetchall()
        return data


def get_endpoint_column(endpoint, column):
    """ Returns a list of entries from column in which the endpoint is involved. """
    with session_scope() as db_session:
        result = db_session.query(column). \
            filter(FunctionCall.endpoint == endpoint). \
            group_by(column).all()
        db_session.expunge_all()
        return result


def get_endpoint_results(endpoint, column):
    """ Returns a list of entries with measurements in which the endpoint is involved.
    The entries are grouped by their version and the given column. """
    with session_scope() as db_session:
        result = db_session.query(FunctionCall.version,
                                  column,
                                  func.count(FunctionCall.execution_time).label('count'),
                                  func.avg(FunctionCall.execution_time).label('average')
                                  ).filter(FunctionCall.endpoint == endpoint). \
            group_by(FunctionCall.version, column).all()
        db_session.expunge_all()
        return result


def get_monitor_rule(endpoint):
    """ Get the MonitorRule from a given endpoint. If no value is found, a new value 
    is added to the database and the function is called again (recursively). """
    try:
        with session_scope() as db_session:
            result = db_session.query(MonitorRule). \
                filter(MonitorRule.endpoint == endpoint).one()
            # for using the result when the session is closed, use expunge
            db_session.expunge(result)
            return result
    except NoResultFound:
        with session_scope() as db_session:
            db_session.add(MonitorRule(endpoint=endpoint, version_added=config.version, time_added=datetime.datetime.now()))

        # return new added row
        return get_monitor_rule(endpoint)


def update_monitor_rule(endpoint, value):
    """ Update the value of a specific monitor rule. """
    with session_scope() as db_session:
        db_session.query(MonitorRule).filter(MonitorRule.endpoint == endpoint). \
            update({MonitorRule.monitor: value})


def get_all_measurement(endpoint):
    """Return all entries with measurements from a given endpoint. Uses for creating a histogram. """
    with session_scope() as db_session:
        result = db_session.query(FunctionCall).filter(FunctionCall.endpoint == endpoint).all()
        db_session.expunge_all()
        return result


def get_last_accessed_times():
    """ Returns a list of all endpoints and their last accessed time. """
    with session_scope() as db_session:
        result = db_session.query(MonitorRule.endpoint, MonitorRule.last_accessed).all()
        db_session.expunge_all()
        return result


def update_last_accessed(endpoint, value):
    """ Updates the timestamp of last access of the endpoint. """
    with session_scope() as db_session:
        db_session.query(MonitorRule).filter(MonitorRule.endpoint == endpoint). \
            update({MonitorRule.last_accessed: value})
