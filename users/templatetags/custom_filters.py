from django import template
import os
from django.conf import settings

register = template.Library()

@register.filter
def image_exists(image_path):
    """
    Check if the image file exists in the static directory.
    """
    image_file_path = os.path.join(settings.BASE_DIR, 'static', image_path)
    return os.path.exists(image_file_path)
