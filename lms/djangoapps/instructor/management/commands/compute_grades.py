#!/usr/bin/python
"""
django management command: dump grades to csv files
for use by batch processes
"""
from instructor.offline_gradecalc import offline_grade_calculation
from courseware.courses import get_course_by_id
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locations import SlashSeparatedCourseKey

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Compute grades for all students in a course, and store result in DB.\n"
    help += "Usage: compute_grades course_id_or_dir \n"
    help += "   course_id_or_dir: either course_id or course_dir\n"
    help += 'Example course_id: MITx/8.01rq_MW/Classical_Mechanics_Reading_Questions_Fall_2012_MW_Section'

    def handle(self, *args, **options):

        print "args = ", args

        if len(args) > 0:
            course_id = args[0]
        else:
            print self.help
            return
        course_key = None
        # parse out the course id into a coursekey
        try:
            course_key = CourseKey.from_string(course_id)
        # if it's not a new-style course key, parse it from an old-style
        # course key
        except InvalidKeyError:
            course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
        try:
            _course = get_course_by_id(course_key)
        except Exception as err:
            print "-----------------------------------------------------------------------------"
            print "Sorry, cannot find course with id {}".format(course_id)
            print "Got exception {}".format(err)
            print "Please provide a course ID or course data directory name, eg content-mit-801rq"
            return

        print "-----------------------------------------------------------------------------"
        print "Computing grades for {}".format(course_id)

        offline_grade_calculation(course_key)
