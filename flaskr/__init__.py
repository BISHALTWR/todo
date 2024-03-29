import os

from flask import Flask

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True) # Creates flask instance
    app.config.from_mapping(
        SECRET_KEY='dev', # Used to keep data safe # override with random value before deployment
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'), # Path for database
    )

    if test_config is None:
        # Load the instance config, it it exists, when not testing
        app.config.from_pyfile('config.py', silent=True) # Overrides congiguration with values taken form config.py
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello') # Creates a simple route to test the application
    def hello():
        return 'Hello, World'

    from .import db
    db.init_app(app)
    
    from . import auth
    app.register_blueprint(auth.bp)

    from . import tasks
    app.register_blueprint(tasks.bp)
    app.add_url_rule('/', endpoint='index')

    
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db}
    
    return app