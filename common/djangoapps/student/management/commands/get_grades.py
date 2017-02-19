"""
Management command to generate a list of grades for
all students that are enrolled in a course.
"""
from courseware import grades, courses
from certificates.models import GeneratedCertificate
from django.test.client import RequestFactory
from django.core.management.base import BaseCommand, CommandError
import os
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from django.contrib.auth.models import User
from optparse import make_option
import datetime
from django.core.handlers.base import BaseHandler
import csv


class RequestMock(RequestFactory):
    def request(self, **request):
        "Construct a generic request object."
        request = RequestFactory.request(self, **request)
        handler = BaseHandler()
        handler.load_middleware()
        for middleware_method in handler._request_middleware:
            if middleware_method(request):
                raise Exception("Couldn't create request mock object - "
                                "request middleware returned a response")
        return request


class Command(BaseCommand):

    help = """
    Generate a list of grades for all students
    that are enrolled in a course.

    CSV will include the following:
      - username
      - email
      - grade in the certificate table if it exists
      - computed grade
      - grade breakdown

    Outputs grades to a csv file.

    Example:
      sudo -u www-data SERVICE_VARIANT=lms /opt/edx/bin/django-admin.py get_grades \
        -c MITx/Chi6.00intro/A_Taste_of_Python_Programming -o /tmp/20130813-6.00x.csv \
        --settings=lms.envs.aws --pythonpath=/opt/wwc/edx-platform
    """

    option_list = BaseCommand.option_list + (
        make_option('-c', '--course',
                    metavar='COURSE_ID',
                    dest='course',
                    default=False,
                    help='Course ID for grade distribution'),
        make_option('-o', '--output',
                    metavar='FILE',
                    dest='output',
                    default=False,
                    help='Filename for grade output'))

    def handle(self, *args, **options):
        if os.path.exists(options['output']):
            raise CommandError("File {0} already exists".format(
                options['output']))

        STATUS_INTERVAL = 100

        # parse out the course into a coursekey
        if options['course']:
            try:
                course_key = CourseKey.from_string(options['course'])
            # if it's not a new-style course key, parse it from an old-style
            # course key
            except InvalidKeyError:
                course_key = SlashSeparatedCourseKey.from_deprecated_string(options['course'])

        print "Fetching enrolled students for {0}".format(course_key)
        enrolled_students = User.objects.filter(
            courseenrollment__course_id=course_key
        )
        factory = RequestMock()
        request = factory.get('/')

        total = enrolled_students.count()
        print "Total enrolled: {0}".format(total)
        course = courses.get_course_by_id(course_key)
        total = enrolled_students.count()
        start = datetime.datetime.now()
        rows = []
        header = None
        print "Fetching certificate data"
        cert_grades = {
            cert.user.username: cert.grade
            for cert in list(
                GeneratedCertificate.objects.filter(  # pylint: disable=no-member
                    course_id=course_key
                ).prefetch_related('user')
            )
        }
        print "Grading students"
        for count, student in enumerate(enrolled_students):
            count += 1
            if count % STATUS_INTERVAL == 0:
                # Print a status update with an approximation of
                # how much time is left based on how long the last
                # interval took
                diff = datetime.datetime.now() - start
                timeleft = diff * (total - count) / STATUS_INTERVAL
                hours, remainder = divmod(timeleft.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                print "{0}/{1} completed ~{2:02}:{3:02}m remaining".format(
                    count, total, hours, minutes)
                start = datetime.datetime.now()
            request.user = student
            grade = grades.grade(student, request, course)
            if not header:
                header = [section['label'] for section in grade[u'section_breakdown']]
                rows.append(["email", "username", "certificate-grade", "grade"] + header)
            percents = {section['label']: section['percent'] for section in grade[u'section_breakdown']}
            row_percents = [percents[label] for label in header]
            if student.username in cert_grades:
                rows.append([student.email, student.username, cert_grades[student.username], grade['percent']] + row_percents)
            else:
                rows.append([student.email, student.username, "N/A", grade['percent']] + row_percents)
        with open(options['output'], 'wb') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
