from empirebt.settings import *
import dj_database_url

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {'default':
                   dj_database_url.config(
                  default='postgres://kayethano:150891@localhost:5432/empirebt')
        }



