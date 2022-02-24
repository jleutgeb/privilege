from os import environ

SESSION_CONFIGS = [
    dict(
        name='privilege',
        display_name='Privilege',
        app_sequence=['instructions', 'privilege'],
        num_demo_participants=2,
        phiP=0.4,
        phiU=0.6,
        qH=0.75,
        qL_low=0.23,
        qL_high=0.69,
        pkP=1,
        pkU=0,
        completion_payoff=2,
        decision_payoff=1,
        beliefs_payoff=0.5,
        treatment='both', # qL_high, qL_low or both
        max_wait_time=600, # maximum time a player has to wait for a partner until the computer takes over
        #completion_link='https://app.prolific.co/submissions/complete?cc=000',
        completion_link='http://www.google.com',
    ),
]

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
        use_secure_urls=True
    ),
]

# add a participant field to store draws of correct boxes
PARTICIPANT_FIELDS = ['privilege', 'qL_high', 'wait_page_arrival']

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = '£'
USE_POINTS = False

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '2556126140943'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']
