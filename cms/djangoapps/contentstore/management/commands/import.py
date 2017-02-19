"""
Script for importing courseware from XML format
"""
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django_comment_common.utils import (seed_permissions_roles,
                                         are_permissions_roles_seeded)
from xmodule.modulestore.xml_importer import import_course_from_xml
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.django import modulestore
from xmodule.contentstore.django import contentstore


class Command(BaseCommand):
    """
    Import the specified data directory into the default ModuleStore
    """
    help = 'Import the specified data directory into the default ModuleStore'

    option_list = BaseCommand.option_list + (
        make_option('--nostatic',
                    action='store_true',
                    help='Skip import of static content'),
    )

    def handle(self, *args, **options):
        "Execute the command"
        if len(args) == 0:
            raise CommandError("import requires at least one argument: <data directory> [--nostatic] [<course dir>...]")

        data_dir = args[0]
        do_import_static = not options.get('nostatic', False)
        if len(args) > 1:
            source_dirs = args[1:]
        else:
            source_dirs = None
        self.stdout.write("Importing.  Data_dir={data}, source_dirs={courses}\n".format(
            data=data_dir,
            courses=source_dirs,
        ))
        mstore = modulestore()

        course_items = import_course_from_xml(
            mstore, ModuleStoreEnum.UserID.mgmt_command, data_dir, source_dirs, load_error_modules=False,
            static_content_store=contentstore(), verbose=True,
            do_import_static=do_import_static,
            create_if_not_present=True,
        )

        for course in course_items:
            course_id = course.id
            if not are_permissions_roles_seeded(course_id):
                self.stdout.write('Seeding forum roles for course {0}\n'.format(course_id))
                seed_permissions_roles(course_id)
