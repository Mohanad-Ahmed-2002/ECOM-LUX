from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # قاعدة بيانات في RAM فقط
    }
}

# تعطيل cloudinary في الاختبارات لو بتستخدمه
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'