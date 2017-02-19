"""
Run these tests @ Devstack:
    paver test_system -s lms --fasttest --verbose --test-id=lms/djangoapps/course_structure_api
"""
# pylint: disable=missing-docstring,invalid-name,maybe-no-member,attribute-defined-outside-init
from datetime import datetime
from mock import patch, Mock

from django.core.urlresolvers import reverse

from capa.tests.response_xml_factory import MultipleChoiceResponseXMLFactory
from edx_oauth2_provider.tests.factories import AccessTokenFactory, ClientFactory
from opaque_keys.edx.locator import CourseLocator
from xmodule.error_module import ErrorDescriptor
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.tests.django_utils import SharedModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from xmodule.modulestore.xml import CourseLocationManager
from xmodule.tests import get_test_system

from courseware.tests.factories import GlobalStaffFactory, StaffFactory
from openedx.core.djangoapps.content.course_structures.models import CourseStructure
from openedx.core.djangoapps.content.course_structures.tasks import update_course_structure


TEST_SERVER_HOST = 'http://testserver'


class CourseViewTestsMixin(object):
    """
    Mixin for course view tests.
    """
    view = None

    raw_grader = [
        {
            "min_count": 24,
            "weight": 0.2,
            "type": "Homework",
            "drop_count": 0,
            "short_label": "HW"
        },
        {
            "min_count": 4,
            "weight": 0.8,
            "type": "Exam",
            "drop_count": 0,
            "short_label": "Exam"
        }
    ]

    def setUp(self):
        super(CourseViewTestsMixin, self).setUp()
        self.create_user_and_access_token()

    def create_user(self):
        self.user = GlobalStaffFactory.create()

    def create_user_and_access_token(self):
        self.create_user()
        self.oauth_client = ClientFactory.create()
        self.access_token = AccessTokenFactory.create(user=self.user, client=self.oauth_client).token

    @classmethod
    def create_course_data(cls):
        cls.invalid_course_id = 'foo/bar/baz'
        cls.course = CourseFactory.create(display_name='An Introduction to API Testing', raw_grader=cls.raw_grader)
        cls.course_id = unicode(cls.course.id)
        with cls.store.bulk_operations(cls.course.id, emit_signals=False):
            cls.sequential = ItemFactory.create(
                category="sequential",
                parent_location=cls.course.location,
                display_name="Lesson 1",
                format="Homework",
                graded=True
            )

            factory = MultipleChoiceResponseXMLFactory()
            args = {'choices': [False, True, False]}
            problem_xml = factory.build_xml(**args)
            cls.problem = ItemFactory.create(
                category="problem",
                parent_location=cls.sequential.location,
                display_name="Problem 1",
                format="Homework",
                data=problem_xml,
            )

            cls.video = ItemFactory.create(
                category="video",
                parent_location=cls.sequential.location,
                display_name="Video 1",
            )

            cls.html = ItemFactory.create(
                category="html",
                parent_location=cls.sequential.location,
                display_name="HTML 1",
            )

        cls.empty_course = CourseFactory.create(
            start=datetime(2014, 6, 16, 14, 30),
            end=datetime(2015, 1, 16),
            org="MTD",
            # Use mongo so that we can get a test with a SlashSeparatedCourseKey
            default_store=ModuleStoreEnum.Type.mongo
        )

    def build_absolute_url(self, path=None):
        """ Build absolute URL pointing to test server.
        :param path: Path to append to the URL
        """
        url = TEST_SERVER_HOST

        if path:
            url += path

        return url

    def assertValidResponseCourse(self, data, course):
        """ Determines if the given response data (dict) matches the specified course. """

        course_key = course.id
        self.assertEqual(data['id'], unicode(course_key))
        self.assertEqual(data['name'], course.display_name)
        self.assertEqual(data['course'], course_key.course)
        self.assertEqual(data['org'], course_key.org)
        self.assertEqual(data['run'], course_key.run)

        uri = self.build_absolute_url(
            reverse('course_structure_api:v0:detail', kwargs={'course_id': unicode(course_key)}))
        self.assertEqual(data['uri'], uri)

    def http_get(self, uri, **headers):
        """Submit an HTTP GET request"""

        default_headers = {
            'HTTP_AUTHORIZATION': 'Bearer ' + self.access_token
        }
        default_headers.update(headers)

        response = self.client.get(uri, follow=True, **default_headers)
        return response

    def http_get_for_course(self, course_id=None, **headers):
        """Submit an HTTP GET request to the view for the given course"""

        return self.http_get(
            reverse(self.view, kwargs={'course_id': course_id or self.course_id}),
            **headers
        )

    def test_not_authenticated(self):
        """
        Verify that access is denied to non-authenticated users.
        """
        raise NotImplementedError

    def test_not_authorized(self):
        """
        Verify that access is denied to non-authorized users.
        """
        raise NotImplementedError


class CourseDetailTestMixin(object):
    """
    Mixin for views utilizing only the course_id kwarg.
    """
    view_supports_debug_mode = True

    def test_get_invalid_course(self):
        """
        The view should return a 404 if the course ID is invalid.
        """
        response = self.http_get_for_course(self.invalid_course_id)
        self.assertEqual(response.status_code, 404)

    def test_get(self):
        """
        The view should return a 200 if the course ID is valid.
        """
        response = self.http_get_for_course()
        self.assertEqual(response.status_code, 200)

        # Return the response so child classes do not have to repeat the request.
        return response

    def test_not_authenticated(self):
        """ The view should return HTTP status 401 if no user is authenticated. """
        # HTTP 401 should be returned if the user is not authenticated.
        response = self.http_get_for_course(HTTP_AUTHORIZATION=None)
        self.assertEqual(response.status_code, 401)

    def test_not_authorized(self):
        user = StaffFactory(course_key=self.course.id)
        access_token = AccessTokenFactory.create(user=user, client=self.oauth_client).token
        auth_header = 'Bearer ' + access_token

        # Access should be granted if the proper access token is supplied.
        response = self.http_get_for_course(HTTP_AUTHORIZATION=auth_header)
        self.assertEqual(response.status_code, 200)

        # Access should be denied if the user is not course staff.
        response = self.http_get_for_course(course_id=unicode(self.empty_course.id), HTTP_AUTHORIZATION=auth_header)
        self.assertEqual(response.status_code, 404)


class CourseListTests(CourseViewTestsMixin, SharedModuleStoreTestCase):
    view = 'course_structure_api:v0:list'

    @classmethod
    def setUpClass(cls):
        super(CourseListTests, cls).setUpClass()
        cls.create_course_data()

    def test_get(self):
        """
        The view should return a list of all courses.
        """
        response = self.http_get(reverse(self.view))
        self.assertEqual(response.status_code, 200)
        data = response.data
        courses = data['results']
        self.assertEqual(len(courses), 2)
        self.assertEqual(data['count'], 2)
        self.assertEqual(data['num_pages'], 1)

        self.assertValidResponseCourse(courses[0], self.empty_course)
        self.assertValidResponseCourse(courses[1], self.course)

    def test_get_with_pagination(self):
        """
        The view should return a paginated list of courses.
        """
        url = "{}?page_size=1".format(reverse(self.view))
        response = self.http_get(url)
        self.assertEqual(response.status_code, 200)

        courses = response.data['results']
        self.assertEqual(len(courses), 1)
        self.assertValidResponseCourse(courses[0], self.empty_course)

    def test_get_filtering(self):
        """
        The view should return a list of details for the specified courses.
        """
        url = "{}?course_id={}".format(reverse(self.view), self.course_id)
        response = self.http_get(url)
        self.assertEqual(response.status_code, 200)

        courses = response.data['results']
        self.assertEqual(len(courses), 1)
        self.assertValidResponseCourse(courses[0], self.course)

    def test_not_authenticated(self):
        response = self.http_get(reverse(self.view), HTTP_AUTHORIZATION=None)
        self.assertEqual(response.status_code, 401)

    def test_not_authorized(self):
        """
        Unauthorized users should get an empty list.
        """
        user = StaffFactory(course_key=self.course.id)
        access_token = AccessTokenFactory.create(user=user, client=self.oauth_client).token
        auth_header = 'Bearer ' + access_token

        # Data should be returned if the user is authorized.
        response = self.http_get(reverse(self.view), HTTP_AUTHORIZATION=auth_header)
        self.assertEqual(response.status_code, 200)

        url = "{}?course_id={}".format(reverse(self.view), self.course_id)
        response = self.http_get(url, HTTP_AUTHORIZATION=auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.data['results']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], self.course.display_name)

        # The view should return an empty list if the user cannot access any courses.
        url = "{}?course_id={}".format(reverse(self.view), unicode(self.empty_course.id))
        response = self.http_get(url, HTTP_AUTHORIZATION=auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset({'count': 0, u'results': []}, response.data)

    def test_course_error(self):
        """
        Ensure the view still returns results even if get_courses() returns an ErrorDescriptor. The ErrorDescriptor
        should be filtered out.
        """

        error_descriptor = ErrorDescriptor.from_xml(
            '<course></course>',
            get_test_system(),
            CourseLocationManager(CourseLocator(org='org', course='course', run='run')),
            None
        )

        descriptors = [error_descriptor, self.empty_course, self.course]

        with patch('xmodule.modulestore.mixed.MixedModuleStore.get_courses', Mock(return_value=descriptors)):
            self.test_get()


class CourseDetailTests(CourseDetailTestMixin, CourseViewTestsMixin, SharedModuleStoreTestCase):
    view = 'course_structure_api:v0:detail'

    @classmethod
    def setUpClass(cls):
        super(CourseDetailTests, cls).setUpClass()
        cls.create_course_data()

    def test_get(self):
        response = super(CourseDetailTests, self).test_get()
        self.assertValidResponseCourse(response.data, self.course)


class CourseStructureTests(CourseDetailTestMixin, CourseViewTestsMixin, SharedModuleStoreTestCase):
    view = 'course_structure_api:v0:structure'

    @classmethod
    def setUpClass(cls):
        super(CourseStructureTests, cls).setUpClass()
        cls.create_course_data()

    def setUp(self):
        super(CourseStructureTests, self).setUp()

        # Ensure course structure exists for the course
        update_course_structure(unicode(self.course.id))

    def test_get(self):
        """
        If the course structure exists in the database, the view should return the data. Otherwise, the view should
        initiate an asynchronous course structure generation and return a 503.
        """

        # Attempt to retrieve data for a course without stored structure
        CourseStructure.objects.all().delete()
        self.assertFalse(CourseStructure.objects.filter(course_id=self.course.id).exists())
        response = self.http_get_for_course()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response['Retry-After'], '120')

        # Course structure generation shouldn't take long. Generate the data and try again.
        self.assertTrue(CourseStructure.objects.filter(course_id=self.course.id).exists())
        response = self.http_get_for_course()
        self.assertEqual(response.status_code, 200)

        blocks = {}

        def add_block(xblock):
            children = xblock.get_children()
            blocks[unicode(xblock.location)] = {
                u'id': unicode(xblock.location),
                u'type': xblock.category,
                u'parent': None,
                u'display_name': xblock.display_name,
                u'format': xblock.format,
                u'graded': xblock.graded,
                u'children': [unicode(child.location) for child in children]
            }

            for child in children:
                add_block(child)

        course = self.store.get_course(self.course.id, depth=None)
        add_block(course)

        expected = {
            u'root': unicode(self.course.location),
            u'blocks': blocks
        }

        self.maxDiff = None
        self.assertDictEqual(response.data, expected)


class CourseGradingPolicyTests(CourseDetailTestMixin, CourseViewTestsMixin, SharedModuleStoreTestCase):
    view = 'course_structure_api:v0:grading_policy'

    @classmethod
    def setUpClass(cls):
        super(CourseGradingPolicyTests, cls).setUpClass()
        cls.create_course_data()

    def test_get(self):
        """
        The view should return grading policy for a course.
        """
        response = super(CourseGradingPolicyTests, self).test_get()

        expected = [
            {
                "count": 24,
                "weight": 0.2,
                "assignment_type": "Homework",
                "dropped": 0
            },
            {
                "count": 4,
                "weight": 0.8,
                "assignment_type": "Exam",
                "dropped": 0
            }
        ]
        self.assertListEqual(response.data, expected)


class CourseGradingPolicyMissingFieldsTests(CourseDetailTestMixin, CourseViewTestsMixin, SharedModuleStoreTestCase):
    view = 'course_structure_api:v0:grading_policy'

    # Update the raw grader to have missing keys
    raw_grader = [
        {
            "min_count": 24,
            "weight": 0.2,
            "type": "Homework",
            "drop_count": 0,
            "short_label": "HW"
        },
        {
            # Deleted "min_count" key
            "weight": 0.8,
            "type": "Exam",
            "drop_count": 0,
            "short_label": "Exam"
        }
    ]

    @classmethod
    def setUpClass(cls):
        super(CourseGradingPolicyMissingFieldsTests, cls).setUpClass()
        cls.create_course_data()

    def test_get(self):
        """
        The view should return grading policy for a course.
        """
        response = super(CourseGradingPolicyMissingFieldsTests, self).test_get()

        expected = [
            {
                "count": 24,
                "weight": 0.2,
                "assignment_type": "Homework",
                "dropped": 0
            },
            {
                "count": None,
                "weight": 0.8,
                "assignment_type": "Exam",
                "dropped": 0
            }
        ]
        self.assertListEqual(response.data, expected)
