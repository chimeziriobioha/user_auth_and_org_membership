from dotenv import load_dotenv

load_dotenv()

import os  # noqa
from flask_migrate import upgrade  # noqa


from maincode import create_app  # noqa
from maincode.appstrings import ucl, lcl  # noqa


if os.environ.get(ucl.PRODUCTION_ENV):
    app = create_app(config_type=lcl.production)
else:
    app = create_app()


with app.app_context():
    # Create/Update tables
    upgrade()


if __name__ == '__main__':
    # Run app
    # if app.config.get(ucl.PRODUCTION_ENV):
    #     # app.run(threaded=True)
    #     app.run(debug=True)  # TO check why endpoints are not running well
    # else:
    #     app.run(host='0.0.0.0', port=5000, threaded=True)
    app.run(debug=True)
