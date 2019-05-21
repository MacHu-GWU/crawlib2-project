# -*- coding: utf-8 -*-

from crawlib2.tests.dummy_site.movie.app import create_app, PORT

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=PORT)
