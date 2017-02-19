"""Management command for backpopulating missing program credentials."""
from collections import namedtuple
import logging

from django.core.management import BaseCommand, CommandError
from django.db.models import Q
from opaque_keys.edx.keys import CourseKey
from provider.oauth2.models import Client

from certificates.models import GeneratedCertificate, CertificateStatuses  # pylint: disable=import-error
from openedx.core.djangoapps.programs.models import ProgramsApiConfig
from openedx.core.djangoapps.programs.tasks.v1.tasks import award_program_certificates
from openedx.core.djangoapps.programs.utils import get_programs


# TODO: Log to console, even with debug mode disabled?
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name
RunMode = namedtuple('RunMode', ['course_key', 'mode_slug'])


class Command(BaseCommand):
    """Management command for backpopulating missing program credentials.

    The command's goal is to pass a narrow subset of usernames to an idempotent
    Celery task for further (parallelized) processing.
    """
    help = 'Backpopulate missing program credentials.'
    client = None
    run_modes = None
    usernames = None

    def add_arguments(self, parser):
        parser.add_argument(
            '-c', '--commit',
            action='store_true',
            dest='commit',
            default=False,
            help='Submit tasks for processing.'
        )

    def handle(self, *args, **options):
        programs_config = ProgramsApiConfig.current()
        self.client = Client.objects.get(name=programs_config.OAUTH2_CLIENT_NAME)

        if self.client.user is None:
            msg = (
                'No user is associated with the {} OAuth2 client. '
                'A service user is necessary to make requests to the Programs API. '
                'No tasks have been enqueued. '
                'Associate a user with the client and try again.'
            ).format(programs_config.OAUTH2_CLIENT_NAME)

            raise CommandError(msg)

        self._load_run_modes()

        logger.info('Looking for users who may be eligible for a program certificate.')

        self._load_usernames()

        if options.get('commit'):
            logger.info('Enqueuing program certification tasks for %d candidates.', len(self.usernames))
        else:
            logger.info(
                'Found %d candidates. To enqueue program certification tasks, pass the -c or --commit flags.',
                len(self.usernames)
            )
            return

        succeeded, failed = 0, 0
        for username in self.usernames:
            try:
                award_program_certificates.delay(username)
            except:  # pylint: disable=bare-except
                failed += 1
                logger.exception('Failed to enqueue task for user [%s]', username)
            else:
                succeeded += 1
                logger.debug('Successfully enqueued task for user [%s]', username)

        logger.info(
            'Done. Successfully enqueued tasks for %d candidates. '
            'Failed to enqueue tasks for %d candidates.',
            succeeded,
            failed
        )

    def _load_run_modes(self):
        """Find all run modes which are part of a program."""
        programs = get_programs(self.client.user)
        self.run_modes = self._flatten(programs)

    def _flatten(self, programs):
        """Flatten program dicts into a set of run modes."""
        run_modes = set()
        for program in programs:
            for course_code in program['course_codes']:
                for run in course_code['run_modes']:
                    course_key = CourseKey.from_string(run['course_key'])
                    run_modes.add(
                        RunMode(course_key, run['mode_slug'])
                    )

        return run_modes

    def _load_usernames(self):
        """Identify a subset of users who may be eligible for a program certificate.

        This is done by finding users who have earned a certificate in at least one
        program course code's run mode.
        """
        status_query = Q(status__in=CertificateStatuses.PASSED_STATUSES)
        run_mode_query = reduce(
            lambda x, y: x | y,
            [Q(course_id=r.course_key, mode=r.mode_slug) for r in self.run_modes]
        )

        query = status_query & run_mode_query

        username_dicts = GeneratedCertificate.eligible_certificates.filter(query).values('user__username').distinct()
        self.usernames = [d['user__username'] for d in username_dicts]
