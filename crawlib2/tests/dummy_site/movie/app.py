# -*- coding: utf-8 -*-

from flask import Flask
from .controller.view import PORT


def create_app():
    from .controller import bp

    app = Flask("app")
    bp_list = [
        bp,
    ]
    for bp in bp_list:
        app.register_blueprint(bp)

    return app
