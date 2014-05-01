from app import app

class _DefaultSettings(object):
    USERNAME = 'world'
    DEBUG = True


def app_factory(global_config, **local_config):
    app.config.update(**global_config)
    app.config.update(**local_config)
    app.config.from_object(_DefaultSettings)
    return app.wsgi_app

