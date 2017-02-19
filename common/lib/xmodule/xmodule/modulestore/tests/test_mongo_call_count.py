"""
Tests to verify correct number of MongoDB calls during course import/export and traversal
when using the Split modulestore.
"""

from tempfile import mkdtemp
from shutil import rmtree
from unittest import TestCase, skip
import ddt

from xmodule.modulestore.xml_importer import import_course_from_xml
from xmodule.modulestore.xml_exporter import export_course_to_xml
from xmodule.modulestore.tests.factories import check_mongo_calls
from xmodule.modulestore.tests.utils import (
    MixedModulestoreBuilder, VersioningModulestoreBuilder,
    MongoModulestoreBuilder, TEST_DATA_DIR
)

MIXED_OLD_MONGO_MODULESTORE_BUILDER = MixedModulestoreBuilder([('draft', MongoModulestoreBuilder())])
MIXED_SPLIT_MODULESTORE_BUILDER = MixedModulestoreBuilder([('split', VersioningModulestoreBuilder())])


@ddt.ddt
@skip("Fix call counts below - sometimes the counts are off by 1.")
class CountMongoCallsXMLRoundtrip(TestCase):
    """
    This class exists to test XML import and export to/from Split.
    """

    def setUp(self):
        super(CountMongoCallsXMLRoundtrip, self).setUp()
        self.export_dir = mkdtemp()
        self.addCleanup(rmtree, self.export_dir, ignore_errors=True)

    @ddt.data(
        (MIXED_OLD_MONGO_MODULESTORE_BUILDER, 287, 779, 702, 702),
        (MIXED_SPLIT_MODULESTORE_BUILDER, 37, 16, 190, 189),
    )
    @ddt.unpack
    def test_import_export(self, store_builder, export_reads, import_reads, first_import_writes, second_import_writes):
        with store_builder.build() as (source_content, source_store):
            with store_builder.build() as (dest_content, dest_store):
                source_course_key = source_store.make_course_key('a', 'course', 'course')
                dest_course_key = dest_store.make_course_key('a', 'course', 'course')

                # An extra import write occurs in the first Split import due to the mismatch between
                # the course id and the wiki_slug in the test XML course. The course must be updated
                # with the correct wiki_slug during import.
                with check_mongo_calls(import_reads, first_import_writes):
                    import_course_from_xml(
                        source_store,
                        'test_user',
                        TEST_DATA_DIR,
                        source_dirs=['manual-testing-complete'],
                        static_content_store=source_content,
                        target_id=source_course_key,
                        create_if_not_present=True,
                        raise_on_failure=True,
                    )

                with check_mongo_calls(export_reads):
                    export_course_to_xml(
                        source_store,
                        source_content,
                        source_course_key,
                        self.export_dir,
                        'exported_source_course',
                    )

                with check_mongo_calls(import_reads, second_import_writes):
                    import_course_from_xml(
                        dest_store,
                        'test_user',
                        self.export_dir,
                        source_dirs=['exported_source_course'],
                        static_content_store=dest_content,
                        target_id=dest_course_key,
                        create_if_not_present=True,
                        raise_on_failure=True,
                    )


@ddt.ddt
class CountMongoCallsCourseTraversal(TestCase):
    """
    Tests the number of Mongo calls made when traversing a course tree from the top course root
    to the leaf nodes.
    """

    # Suppose you want to traverse a course - maybe accessing the fields of each XBlock in the course,
    # maybe not. What parameters should one use for get_course() in order to minimize the number of
    # mongo calls? The tests below both ensure that code changes don't increase the number of mongo calls
    # during traversal -and- demonstrate how to minimize the number of calls.
    @ddt.data(
        # These two lines show the way this traversal *should* be done
        # (if you'll eventually access all the fields and load all the definitions anyway).
        # 'lazy' does not matter in old Mongo.
        (MIXED_OLD_MONGO_MODULESTORE_BUILDER, None, False, True, 175),
        (MIXED_OLD_MONGO_MODULESTORE_BUILDER, None, True, True, 175),
        (MIXED_OLD_MONGO_MODULESTORE_BUILDER, 0, False, True, 359),
        (MIXED_OLD_MONGO_MODULESTORE_BUILDER, 0, True, True, 359),
        # As shown in these two lines: whether or not the XBlock fields are accessed,
        # the same number of mongo calls are made in old Mongo for depth=None.
        (MIXED_OLD_MONGO_MODULESTORE_BUILDER, None, False, False, 175),
        (MIXED_OLD_MONGO_MODULESTORE_BUILDER, None, True, False, 175),
        (MIXED_OLD_MONGO_MODULESTORE_BUILDER, 0, False, False, 359),
        (MIXED_OLD_MONGO_MODULESTORE_BUILDER, 0, True, False, 359),
        # The line below shows the way this traversal *should* be done
        # (if you'll eventually access all the fields and load all the definitions anyway).
        (MIXED_SPLIT_MODULESTORE_BUILDER, None, False, True, 4),
        (MIXED_SPLIT_MODULESTORE_BUILDER, None, True, True, 38),
        (MIXED_SPLIT_MODULESTORE_BUILDER, 0, False, True, 131),
        (MIXED_SPLIT_MODULESTORE_BUILDER, 0, True, True, 38),
        (MIXED_SPLIT_MODULESTORE_BUILDER, None, False, False, 4),
        (MIXED_SPLIT_MODULESTORE_BUILDER, None, True, False, 4),
        # TODO: The call count below seems like a bug - should be 4?
        # Seems to be related to using self.lazy in CachingDescriptorSystem.get_module_data().
        (MIXED_SPLIT_MODULESTORE_BUILDER, 0, False, False, 131),
        (MIXED_SPLIT_MODULESTORE_BUILDER, 0, True, False, 4)
    )
    @ddt.unpack
    def test_number_mongo_calls(self, store, depth, lazy, access_all_block_fields, num_mongo_calls):
        with store.build() as (source_content, source_store):

            source_course_key = source_store.make_course_key('a', 'course', 'course')

            # First, import a course.
            import_course_from_xml(
                source_store,
                'test_user',
                TEST_DATA_DIR,
                source_dirs=['manual-testing-complete'],
                static_content_store=source_content,
                target_id=source_course_key,
                create_if_not_present=True,
                raise_on_failure=True,
            )

            # Course traversal modeled after the traversal done here:
            # lms/djangoapps/mobile_api/video_outlines/serializers.py:BlockOutline
            # Starting at the root course block, do a breadth-first traversal using
            # get_children() to retrieve each block's children.
            with check_mongo_calls(num_mongo_calls):
                with source_store.bulk_operations(source_course_key):
                    start_block = source_store.get_course(source_course_key, depth=depth, lazy=lazy)
                    all_blocks = []
                    stack = [start_block]
                    while stack:
                        curr_block = stack.pop()
                        all_blocks.append(curr_block)
                        if curr_block.has_children:
                            for block in reversed(curr_block.get_children()):
                                stack.append(block)

                    if access_all_block_fields:
                        # Read the fields on each block in order to ensure each block and its definition is loaded.
                        for xblock in all_blocks:
                            for __, field in xblock.fields.iteritems():
                                if field.is_set_on(xblock):
                                    __ = field.read_from(xblock)
