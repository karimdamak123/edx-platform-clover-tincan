"""Helper functions for working with Credentials."""
from __future__ import unicode_literals
import logging

from openedx.core.djangoapps.credentials.models import CredentialsApiConfig
from openedx.core.djangoapps.programs.utils import get_programs_for_credentials
from openedx.core.lib.edx_api_utils import get_edx_api_data


log = logging.getLogger(__name__)


def get_user_credentials(user):
    """Given a user, get credentials earned from the Credentials service.
    Arguments:
        user (User): The user to authenticate as when requesting credentials.
    Returns:
        list of dict, representing credentials returned by the Credentials
        service.
    """
    credential_configuration = CredentialsApiConfig.current()
    user_query = {'username': user.username}
    # Bypass caching for staff users, who may be generating credentials and
    # want to see them displayed immediately.
    use_cache = credential_configuration.is_cache_enabled and not user.is_staff
    cache_key = credential_configuration.CACHE_KEY + '.' + user.username if use_cache else None

    credentials = get_edx_api_data(
        credential_configuration, user, 'user_credentials', querystring=user_query, cache_key=cache_key
    )
    return credentials


def get_user_program_credentials(user):
    """Given a user, get the list of all program credentials earned and returns
    list of dictionaries containing related programs data.

    Arguments:
        user (User): The user object for getting programs credentials.

    Returns:
        list, containing programs dictionaries.
    """
    programs_credentials_data = []
    credential_configuration = CredentialsApiConfig.current()
    if not credential_configuration.is_learner_issuance_enabled:
        log.debug('Display of certificates for programs is disabled.')
        return programs_credentials_data

    credentials = get_user_credentials(user)
    if not credentials:
        log.info('No credential earned by the given user.')
        return programs_credentials_data

    programs_credentials = []
    for credential in credentials:
        try:
            if 'program_id' in credential['credential'] and credential['status'] == 'awarded':
                programs_credentials.append(credential)
        except KeyError:
            log.exception('Invalid credential structure: %r', credential)

    if programs_credentials:
        programs_credentials_data = get_programs_for_credentials(user, programs_credentials)

    return programs_credentials_data


def get_programs_credentials(user, category=None):
    """Return program credentials data required for display.

    Given a user, find all programs for which certificates have been earned
    and return list of dictionaries of required program data.

    Arguments:
        user (User): user object for getting programs credentials.
        category(str) : program category for getting credentials.

    Returns:
        list of dict, containing data corresponding to the programs for which
        the user has been awarded a credential.
    """
    programs_credentials = get_user_program_credentials(user)
    credentials_data = []
    for program in programs_credentials:
        is_included = (category is None) or (program.get('category') == category)
        if is_included:
            try:
                program_data = {
                    'display_name': program['name'],
                    'subtitle': program['subtitle'],
                    'credential_url': program['credential_url'],
                }
                credentials_data.append(program_data)
            except KeyError:
                log.warning('Program structure is invalid: %r', program)

    return credentials_data
