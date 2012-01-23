import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

SITE_ID=1
PROJECT_APPS = ('django_any',)
INSTALLED_APPS = ( 'django.contrib.auth',
                   'django.contrib.contenttypes',
                   'django.contrib.sessions',
                   'django.contrib.sites',
                   'django.contrib.admin',
                   'django_jenkins',) + PROJECT_APPS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}
TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
)
ROOT_URLCONF = 'tests.test_runner'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

DJANGO_ANY_INSERT_NULL = False

DATABASES = {
    'default': {
        'NAME': 'dev_any.db', # The name of your database. If you're using SQLite, the database will be a file on your computer; in that case, NAME should be the full absolute path, including filename, of that file. If the file doesn't exist, it will automatically be created when you synchronize the database for the first time.
        'ENGINE': 'django.db.backends.sqlite3', # Either 'django.db.backends.postgresql_psycopg2', 'django.db.backends.mysql' or 'django.db.backends.sqlite3'.
        # 'USER': 'myusername', # Your database username (not used for SQLite).
        # 'PASSWORD': 's3krit', # Your database password (not used for SQLite).
    }
}


if __name__ == "__main__":
    import sys, test_runner as settings
    from django.core.management import execute_manager
    if len(sys.argv) == 1:
            sys.argv += ['test'] + list(PROJECT_APPS)
    execute_manager(settings)
