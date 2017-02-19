"""
Models for the custom course feature
"""
import json
import logging
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from pytz import utc

from lazy import lazy
from openedx.core.lib.time_zone_utils import get_time_zone_abbr
from xmodule_django.models import CourseKeyField, LocationKeyField
from xmodule.error_module import ErrorDescriptor
from xmodule.modulestore.django import modulestore


log = logging.getLogger("edx.ccx")


class CustomCourseForEdX(models.Model):
    """
    A Custom Course.
    """
    course_id = CourseKeyField(max_length=255, db_index=True)
    display_name = models.CharField(max_length=255)
    coach = models.ForeignKey(User, db_index=True)
    # if not empty, this field contains a json serialized list of
    # the master course modules
    structure_json = models.TextField(verbose_name='Structure JSON', blank=True, null=True)

    class Meta(object):
        app_label = 'ccx'

    @lazy
    def course(self):
        """Return the CourseDescriptor of the course related to this CCX"""
        store = modulestore()
        with store.bulk_operations(self.course_id):
            course = store.get_course(self.course_id)
            if not course or isinstance(course, ErrorDescriptor):
                log.error("CCX {0} from {2} course {1}".format(  # pylint: disable=logging-format-interpolation
                    self.display_name, self.course_id, "broken" if course else "non-existent"
                ))
            return course

    @lazy
    def start(self):
        """Get the value of the override of the 'start' datetime for this CCX
        """
        # avoid circular import problems
        from .overrides import get_override_for_ccx
        return get_override_for_ccx(self, self.course, 'start')

    @lazy
    def due(self):
        """Get the value of the override of the 'due' datetime for this CCX
        """
        # avoid circular import problems
        from .overrides import get_override_for_ccx
        return get_override_for_ccx(self, self.course, 'due')

    @lazy
    def max_student_enrollments_allowed(self):
        """
        Get the value of the override of the 'max_student_enrollments_allowed'
        datetime for this CCX
        """
        # avoid circular import problems
        from .overrides import get_override_for_ccx
        return get_override_for_ccx(self, self.course, 'max_student_enrollments_allowed')

    def has_started(self):
        """Return True if the CCX start date is in the past"""
        return datetime.now(utc) > self.start

    def has_ended(self):
        """Return True if the CCX due date is set and is in the past"""
        if self.due is None:
            return False

        return datetime.now(utc) > self.due

    def start_datetime_text(self, format_string="SHORT_DATE", time_zone=utc):
        """Returns the desired text representation of the CCX start datetime

        The returned value is in specified time zone, defaulted to UTC.
        """
        i18n = self.course.runtime.service(self.course, "i18n")
        strftime = i18n.strftime
        value = strftime(self.start.astimezone(time_zone), format_string)
        if format_string == 'DATE_TIME':
            value += ' ' + get_time_zone_abbr(time_zone, self.start)
        return value

    def end_datetime_text(self, format_string="SHORT_DATE", time_zone=utc):
        """Returns the desired text representation of the CCX due datetime

        If the due date for the CCX is not set, the value returned is the empty
        string.

        The returned value is in specified time zone, defaulted to UTC.
        """
        if self.due is None:
            return ''

        i18n = self.course.runtime.service(self.course, "i18n")
        strftime = i18n.strftime
        value = strftime(self.due.astimezone(time_zone), format_string)
        if format_string == 'DATE_TIME':
            value += ' ' + get_time_zone_abbr(time_zone, self.due)
        return value

    @property
    def structure(self):
        """
        Deserializes a course structure JSON object
        """
        if self.structure_json:
            return json.loads(self.structure_json)
        return None


class CcxFieldOverride(models.Model):
    """
    Field overrides for custom courses.
    """
    ccx = models.ForeignKey(CustomCourseForEdX, db_index=True)
    location = LocationKeyField(max_length=255, db_index=True)
    field = models.CharField(max_length=255)

    class Meta(object):
        app_label = 'ccx'
        unique_together = (('ccx', 'location', 'field'),)

    value = models.TextField(default='null')
