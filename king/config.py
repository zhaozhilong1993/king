# Server Specific Configurations
server = {
    'port': '8080',
    'host': '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'root': 'golden.api.controllers.root.RootController',
    'modules': ['golden.api'],
    'debug': True,
}
