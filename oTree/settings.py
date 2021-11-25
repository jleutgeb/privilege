from os import environ

SESSION_CONFIGS = [
    dict(
        name='privilege_public_choice',
        display_name="Privilege (Public, Choice)",
        app_sequence=['consent', 'subject_email', 'privilege', 'survey', 'payment_info'],
        num_demo_participants=2,
        public=True,
        follower_choice=True,
    ),
    dict(
        name='privilege_private_choice',
        display_name="Privilege (Private, Choice)",
        app_sequence=['consent', 'subject_email', 'privilege', 'survey', 'payment_info'],
        num_demo_participants=2,
        public=False,
        follower_choice=True,
    ),
    dict(
        name='privilege_public_no_choice',
        display_name="Privilege (Public, No Choice)",
        app_sequence=['consent', 'subject_email', 'privilege', 'survey', 'payment_info'],
        num_demo_participants=2,
        public=True,
        follower_choice=False,
    ),
    dict(
        name='privilege_private_no_choice',
        display_name="Privilege (Private, No Choice)",
        app_sequence=['consent', 'subject_email', 'privilege', 'survey', 'payment_info'],
        num_demo_participants=2,
        public=False,
        follower_choice=False,
    ),
    dict(
        name='privilege_public_choice_bots',
        display_name="Privilege (Public, Choice, Bots)",
        app_sequence=['consent', 'subject_email', 'privilege', 'survey', 'payment_info'],
        num_demo_participants=2,
        public=True,
        follower_choice=True,
        use_browser_bots=True,
    ),
    dict(
        name='privilege_private_choice_bots',
        display_name="Privilege (Private, Choice, Bots)",
        app_sequence=['consent', 'subject_email', 'privilege', 'survey', 'payment_info'],
        num_demo_participants=2,
        public=False,
        follower_choice=True,
        use_browser_bots=True,
    ),
    dict(
        name='privilege_public_no_choice_bots',
        display_name="Privilege (Public, No Choice, Bots)",
        app_sequence=['consent', 'subject_email', 'privilege', 'survey', 'payment_info'],
        num_demo_participants=2,
        public=True,
        follower_choice=False,
        use_browser_bots=True,
    ),
    dict(
        name='privilege_private_no_choice_bots',
        display_name="Privilege (Private, No Choice, Bots)",
        app_sequence=['consent', 'subject_email', 'privilege', 'survey', 'payment_info'],
        num_demo_participants=2,
        public=False,
        follower_choice=False,
        use_browser_bots=True,
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
PARTICIPANT_FIELDS = ['draw_correct', 'draw_leadership_correct']

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
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = False

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '2556126140943'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']
