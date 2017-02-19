// Karma config for xmodule suite.
// Docs and troubleshooting tips in common/static/common/js/karma.common.conf.js

/* jshint node: true */
/*jshint -W079 */

'use strict';
var path = require('path');
var configModule = require(path.join(__dirname, 'common_static/common/js/karma.common.conf.js'));

var options = {

    useRequireJs: false,

    normalizePathsForCoverageFunc: function(appRoot, pattern) {
        return pattern;
    },

    // Avoid adding files to this list. Use RequireJS.
    libraryFilesToInclude: [
        {pattern: 'common_static/js/vendor/requirejs/require.js', included: true},
        {pattern: 'RequireJS-namespace-undefine.js', included: true},

        {pattern: 'common_static/coffee/src/ajax_prefix.js', included: true},
        {pattern: 'common_static/common/js/vendor/underscore.js', included: true},
        {pattern: 'common_static/common/js/vendor/backbone.js', included: true},
        {pattern: 'common_static/js/vendor/CodeMirror/codemirror.js', included: true},
        {pattern: 'common_static/js/vendor/draggabilly.js'},
        {pattern: 'common_static/common/js/vendor/jquery.js', included: true},
        {pattern: 'common_static/common/js/vendor/jquery-migrate.js', included: true},
        {pattern: 'common_static/js/vendor/jquery.cookie.js', included: true},
        {pattern: 'common_static/js/vendor/jquery.leanModal.js', included: true},
        {pattern: 'common_static/js/vendor/jquery.timeago.js', included: true},
        {pattern: 'common_static/js/vendor/jquery-ui.min.js', included: true},
        {pattern: 'common_static/js/vendor/jquery.ui.draggable.js', included: true},
        {pattern: 'common_static/js/vendor/json2.js', included: true},
        {pattern: 'common_static/js/vendor/moment.min.js', included: true},
        {pattern: 'common_static/js/vendor/tinymce/js/tinymce/jquery.tinymce.min.js', included: true},
        {pattern: 'common_static/js/vendor/tinymce/js/tinymce/tinymce.full.min.js', included: true},
        {pattern: 'common_static/js/src/accessibility_tools.js', included: true},
        {pattern: 'common_static/js/src/logger.js', included: true},
        {pattern: 'common_static/js/src/utility.js', included: true},
        {pattern: 'common_static/js/test/add_ajax_prefix.js', included: true},
        {pattern: 'common_static/js/test/i18n.js', included: true},
        {pattern: 'public/js/split_test_staff.js', included: true},
        {pattern: 'src/word_cloud/d3.min.js', included: true},

        {pattern: 'common_static/js/vendor/jasmine-imagediff.js', included: true},
        {pattern: 'common_static/common/js/spec_helpers/jasmine-waituntil.js', included: true},
        {pattern: 'common_static/common/js/spec_helpers/jasmine-extensions.js', included: true},
        {pattern: 'common_static/js/vendor/sinon-1.17.0.js', included: true},

        {pattern: 'spec/main_requirejs.js', included: true},
    ],

    libraryFiles: [
        {pattern: 'common_static/edx-pattern-library/js/**/*.js'},
        {pattern: 'common_static/edx-ui-toolkit/js/**/*.js'}
    ],

    // Make sure the patterns in sourceFiles and specFiles do not match the same file.
    // Otherwise Istanbul which is used for coverage tracking will cause tests to not run.
    sourceFiles: [
        {pattern: 'src/xmodule.js', included: true, ignoreCoverage: true}, // To prevent getting instrumented twice.
        {pattern: 'src/**/*.js', included: true}
    ],

    specFiles: [
        {pattern: 'spec/helper.js', included: true, ignoreCoverage: true}, // Helper which depends on source files.
        {pattern: 'spec/**/*.js', included: true}
    ],

    fixtureFiles: [
        {pattern: 'fixtures/*.*'}
    ],

    runFiles: [
        {pattern: 'karma_runner.js', included: true}
    ]
};

module.exports = function (config) {
    configModule.configure(config, options);
};
