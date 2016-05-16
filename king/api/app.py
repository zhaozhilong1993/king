import pecan
from golden import config as api_config
from golden import hooks


def get_pecan_config():
    filename = api_config.__file__.replace('.pyc', '.py')
    return pecan.configuration.conf_from_file(filename)


def setup_app():
    config = get_pecan_config()

    app_conf = dict(config.app)
    app_hooks = [hooks.DBHook()]

    app = pecan.make_app(
        app_conf.pop('root'),
        hooks=app_hooks,
        **app_conf
    )
    return app
