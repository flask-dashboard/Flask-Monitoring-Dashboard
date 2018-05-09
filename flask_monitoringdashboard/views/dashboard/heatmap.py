import datetime

import plotly.graph_objs as go
from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.forms import get_daterange_form
from flask_monitoringdashboard.core.plot import get_layout, get_figure, heatmap as plot_heatmap
from flask_monitoringdashboard.core.plot.util import get_information
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.endpoint import get_num_requests
import pytz

TITLE = 'Hourly load of the number of requests'

utc = pytz.timezone('UTC')

AXES_INFO = '''The X-axis presents a number of days. The Y-axis presents every hour of 
the day.'''

CONTENT_INFO = '''The color of the cell presents the number of requests that the application received 
in a single hour. The darker the cell, the more requests it has processed. This information can be used 
to validate on which moment of the day the Flask application processes to most requests.'''


@blueprint.route('/hourly_load', methods=['GET', 'POST'])
@secure
def hourly_load():
    form = get_daterange_form()
    return render_template('fmd_dashboard/graph.html', form=form, graph=hourly_load_graph(form), title=TITLE,
                           information=get_information(AXES_INFO, CONTENT_INFO))


def hourly_load_graph(form, end=None):
    """
    Return HTML string for generating a Heatmap.
    :param form: A SelectDateRangeForm, which is used to filter the selection
    :param end: optionally, filter the data on a specific endpoint
    :return: HTML code with the graph
    """
    # list of hours: 0:00 - 23:00
    hours = ['0{}:00'.format(h) for h in range(0, 10)] + ['{}:00'.format(h) for h in range(10, 24)]
    days = form.get_days()

    # create empty 2D-list: [hour][day]
    heatmap_data = []
    for i in range(len(hours)):
        heatmap_data.append([])
        [heatmap_data[i].append(0) for _ in days]

    # add data from database to heatmap_data
    with session_scope() as db_session:
        for d in get_num_requests(db_session, end, form.start_date.data, form.end_date.data):
            parsed_time = datetime.datetime.strptime(d[0], '%Y-%m-%d %H:%M:%S').\
                replace(tzinfo=utc).astimezone(pytz.timezone(form.timezone.data))
            day_index = (parsed_time - datetime.datetime.combine(form.start_date.data, datetime.time(0, 0, 0, 0)).
                         replace(tzinfo=utc)).days
            hour_index = int(parsed_time.strftime('%H'))
            heatmap_data[hour_index][day_index] = d[1]

    layout = get_layout(
        xaxis=go.XAxis(range=[(form.start_date.data - datetime.timedelta(days=1, hours=6)).
                       strftime('%Y-%m-%d 12:00:00'), form.end_date.data.strftime('%Y-%m-%d 12:00:00')]),
        yaxis={'autorange': 'reversed'}
    )
    return get_figure(layout, [plot_heatmap(x=days, y=hours, z=heatmap_data)])
