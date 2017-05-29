# flask-dashboard
Dashboard for automatic monitoring of python web services

This is a flask extension that can be added to your existing flask application.

It measures which python functions are heavily used and which aren't. Moreover, you can see the execution time per function.

Installation
============
To install from source, download the source code, then run this:

    python setup.py install

If you don't have permission, than consider using a virtual environment.
For more info about virtualenvs, see this link: http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/
    
Setup
=====
Adding the extension is simple:

    from flask import Flask
    import dashboard

    app = Flask(__name__)
    dashboard.bind(app)
    
Usage
=====
Once the setup is done, you can view the dashboard at: 

    localhost:5000/dashboard
