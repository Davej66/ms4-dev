from django.db import models
from timezone_field import TimeZoneField
from django.db.models.base import ModelState
from django.db.models.fields import related
from django.utils import tree
from users.models import MyAccount

import pytz


def get_header_image_filepath(self, filename):
    return f'header_images/event_id_{self.event_id}/header_img.png'

# Image from Pixabay Image by 
# https://pixabay.com/users/wanderercreative-855399/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=973460">Stephanie Edwards</a> from <a href="https://pixabay.com/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=973460
def get_default_header_image():
    return 'profile_imgs/default_avatar.png'

class Event(models.Model):
    event_id = models.AutoField(primary_key=True, default=1)
    title = models.CharField(max_length=100, blank=False, default="")
    description = models.TextField(max_length=1000, blank=False, default="")
    header_image = models.ImageField(upload_to=get_header_image_filepath, null=True, blank=True, default=get_default_header_image)
    industry = models.CharField(max_length=255, blank=False, default="")
    location = models.CharField(max_length=100, blank=False, default="Online")
    start_datetime = models.DateTimeField(verbose_name='start_date', blank=False, default="")
    end_datetime = models.DateTimeField(verbose_name='end_date', blank=False, default="")
    timezone = TimeZoneField(choices_display='WITH_GMT_OFFSET', default='Europe/London')
    registrants = models.ManyToManyField(MyAccount, related_name='attendees', blank=True)
    max_reg = models.IntegerField(blank=False, default=100)

    def __str__(self):
        return self.title
