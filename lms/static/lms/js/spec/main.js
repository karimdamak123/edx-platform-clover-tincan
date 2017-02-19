(function(requirejs) {
    'use strict';

    // TODO: how can we share the vast majority of this config that is in common with CMS?
    requirejs.config({
        baseUrl: '/base/',

        paths: {
            'gettext': 'xmodule_js/common_static/js/test/i18n',
            'codemirror': 'xmodule_js/common_static/js/vendor/CodeMirror/codemirror',
            'jquery': 'xmodule_js/common_static/common/js/vendor/jquery',
            'jquery-migrate': 'xmodule_js/common_static/common/js/vendor/jquery-migrate',
            'jquery.ui': 'xmodule_js/common_static/js/vendor/jquery-ui.min',
            'jquery.eventDrag': 'xmodule_js/common_static/js/vendor/jquery.event.drag-2.2',
            'jquery.flot': 'xmodule_js/common_static/js/vendor/flot/jquery.flot.min',
            'jquery.form': 'xmodule_js/common_static/js/vendor/jquery.form',
            'jquery.markitup': 'xmodule_js/common_static/js/vendor/markitup/jquery.markitup',
            'jquery.leanModal': 'xmodule_js/common_static/js/vendor/jquery.leanModal',
            'jquery.ajaxQueue': 'xmodule_js/common_static/js/vendor/jquery.ajaxQueue',
            'jquery.ajax-retry': 'js/vendor/jquery.ajax-retry',
            'jquery.smoothScroll': 'xmodule_js/common_static/js/vendor/jquery.smooth-scroll.min',
            'jquery.scrollTo': 'common/js/vendor/jquery.scrollTo',
            'jquery.timepicker': 'xmodule_js/common_static/js/vendor/timepicker/jquery.timepicker',
            'jquery.cookie': 'xmodule_js/common_static/js/vendor/jquery.cookie',
            'jquery.qtip': 'xmodule_js/common_static/js/vendor/jquery.qtip.min',
            'jquery.fileupload': 'xmodule_js/common_static/js/vendor/jQuery-File-Upload/js/jquery.fileupload',
            'jquery.iframe-transport': 'xmodule_js/common_static/js/vendor/jQuery-File-Upload/js/jquery.iframe-transport',
            'jquery.inputnumber': 'xmodule_js/common_static/js/vendor/html5-input-polyfills/number-polyfill',
            'jquery.immediateDescendents': 'xmodule_js/common_static/coffee/src/jquery.immediateDescendents',
            'jquery.simulate': 'xmodule_js/common_static/js/vendor/jquery.simulate',
            'jquery.timeago': 'xmodule_js/common_static/js/vendor/jquery.timeago',
            'jquery.url': 'xmodule_js/common_static/js/vendor/url.min',
            'datepair': 'xmodule_js/common_static/js/vendor/timepicker/datepair',
            'date': 'xmodule_js/common_static/js/vendor/date',
            'moment': 'xmodule_js/common_static/js/vendor/moment.min',
            'moment-with-locales': 'xmodule_js/common_static/js/vendor/moment-with-locales.min',
            'text': 'xmodule_js/common_static/js/vendor/requirejs/text',
            'underscore': 'common/js/vendor/underscore',
            'underscore.string': 'common/js/vendor/underscore.string',
            'backbone': 'common/js/vendor/backbone',
            'backbone.associations': 'xmodule_js/common_static/js/vendor/backbone-associations-min',
            'backbone.paginator': 'common/js/vendor/backbone.paginator',
            'backbone-super': 'js/vendor/backbone-super',
            'URI': 'xmodule_js/common_static/js/vendor/URI.min',
            'tinymce': 'xmodule_js/common_static/js/vendor/tinymce/js/tinymce/tinymce.full.min',
            'jquery.tinymce': 'xmodule_js/common_static/js/vendor/tinymce/js/tinymce/jquery.tinymce',
            'xmodule': 'xmodule_js/src/xmodule',
            'utility': 'xmodule_js/common_static/js/src/utility',
            'accessibility': 'xmodule_js/common_static/js/src/accessibility_tools',
            'sinon': 'xmodule_js/common_static/js/vendor/sinon-1.17.0',
            'squire': 'xmodule_js/common_static/js/vendor/Squire',
            'jasmine-imagediff': 'xmodule_js/common_static/js/vendor/jasmine-imagediff',
            'domReady': 'xmodule_js/common_static/js/vendor/domReady',
            'mathjax': '//cdn.mathjax.org/mathjax/2.6-latest/MathJax.js?config=TeX-MML-AM_SVG&delayStartupUntil=configured', // jshint ignore:line
            'youtube': '//www.youtube.com/player_api?noext',
            'coffee/src/ajax_prefix': 'xmodule_js/common_static/coffee/src/ajax_prefix',
            'coffee/src/instructor_dashboard/student_admin': 'coffee/src/instructor_dashboard/student_admin',
            'xmodule_js/common_static/js/test/add_ajax_prefix': 'xmodule_js/common_static/js/test/add_ajax_prefix',
            'xblock/lms.runtime.v1': 'lms/js/xblock/lms.runtime.v1',
            'xblock': 'common/js/xblock',
            'capa/display': 'xmodule_js/src/capa/display',
            'string_utils': 'xmodule_js/common_static/js/src/string_utils',
            'logger': 'xmodule_js/common_static/js/src/logger',
            'Markdown.Converter': 'js/Markdown.Converter',
            'Markdown.Editor': 'js/Markdown.Editor',
            'Markdown.Sanitizer': 'js/Markdown.Sanitizer',
            '_split': 'js/split',
            'mathjax_delay_renderer': 'coffee/src/mathjax_delay_renderer',
            'MathJaxProcessor': 'coffee/src/customwmd',
            'picturefill': 'common/js/vendor/picturefill',
            'draggabilly': 'xmodule_js/common_static/js/vendor/draggabilly',
            'modernizr': 'edx-pattern-library/js/modernizr-custom',
            'afontgarde': 'edx-pattern-library/js/afontgarde',
            'edxicons': 'edx-pattern-library/js/edx-icons',

            // Manually specify LMS files that are not converted to RequireJS
            'history': 'js/vendor/history',
            'js/commerce/views/receipt_view': 'js/commerce/views/receipt_view',
            'js/staff_debug_actions': 'js/staff_debug_actions',
            'js/vendor/jquery.qubit': 'js/vendor/jquery.qubit',
            'js/utils/navigation': 'js/utils/navigation',

            // Backbone classes loaded explicitly until they are converted to use RequireJS
            'js/models/notification': 'js/models/notification',
            'js/views/file_uploader': 'js/views/file_uploader',
            'js/views/notification': 'js/views/notification',
            'js/student_account/account': 'js/student_account/account',
            'js/student_profile/views/learner_profile_fields': 'js/student_profile/views/learner_profile_fields',
            'js/student_profile/views/learner_profile_factory': 'js/student_profile/views/learner_profile_factory',
            'js/student_profile/views/learner_profile_view': 'js/student_profile/views/learner_profile_view',
            'js/ccx/schedule': 'js/ccx/schedule',

            // Discussion classes loaded explicitly until they are converted to use RequireJS
            'DiscussionModuleView': 'xmodule_js/common_static/common/js/discussion/discussion_module_view',

            'js/bookmarks/collections/bookmarks': 'js/bookmarks/collections/bookmarks',
            'js/bookmarks/models/bookmark': 'js/bookmarks/models/bookmark',
            'js/bookmarks/views/bookmarks_list_button': 'js/bookmarks/views/bookmarks_list_button',
            'js/bookmarks/views/bookmarks_list': 'js/bookmarks/views/bookmarks_list',
            'js/bookmarks/views/bookmark_button': 'js/bookmarks/views/bookmark_button',
            'js/views/message_banner': 'js/views/message_banner',

            // edxnotes
            'annotator_1.2.9': 'xmodule_js/common_static/js/vendor/edxnotes/annotator-full.min',

            // Common edx utils
            'common/js/utils/edx.utils.validate': 'common/js/utils/edx.utils.validate',
            'slick.core': 'xmodule_js/common_static/js/vendor/slick.core',
            'slick.grid': 'xmodule_js/common_static/js/vendor/slick.grid'
        },
        shim: {
            'gettext': {
                exports: 'gettext'
            },
            'string_utils': {
                deps: ['underscore'],
                exports: 'interpolate_text'
            },
            'date': {
                exports: 'Date'
            },
            'jquery-migrate': ['jquery'],
            'jquery.ui': {
                deps: ['jquery'],
                exports: 'jQuery.ui'
            },
            'jquery.flot': {
                deps: ['jquery'],
                exports: 'jQuery.flot'
            },
            'jquery.form': {
                deps: ['jquery'],
                exports: 'jQuery.fn.ajaxForm'
            },
            'jquery.markitup': {
                deps: ['jquery'],
                exports: 'jQuery.fn.markitup'
            },
            'jquery.leanModal': {
                deps: ['jquery'],
                exports: 'jQuery.fn.leanModal'
            },
            'jquery.smoothScroll': {
                deps: ['jquery'],
                exports: 'jQuery.fn.smoothScroll'
            },
            'jquery.ajaxQueue': {
                deps: ['jquery'],
                exports: 'jQuery.fn.ajaxQueue'
            },
            'jquery.scrollTo': {
                deps: ['jquery'],
                exports: 'jQuery.fn.scrollTo'
            },
            'jquery.cookie': {
                deps: ['jquery'],
                exports: 'jQuery.fn.cookie'
            },
            'jquery.qtip': {
                deps: ['jquery'],
                exports: 'jQuery.fn.qtip'
            },
            'jquery.fileupload': {
                deps: ['jquery.iframe-transport'],
                exports: 'jQuery.fn.fileupload'
            },
            'jquery.inputnumber': {
                deps: ['jquery'],
                exports: 'jQuery.fn.inputNumber'
            },
            'jquery.simulate': {
                deps: ['jquery'],
                exports: 'jQuery.fn.simulate'
            },
            'jquery.timeago': {
                deps: ['jquery'],
                exports: 'jQuery.timeago'
            },
            'jquery.tinymce': {
                deps: ['jquery', 'tinymce'],
                exports: 'jQuery.fn.tinymce'
            },
            'jquery.url': {
                deps: ['jquery'],
                exports: 'jQuery.fn.url'
            },
            'datepair': {
                deps: ['jquery.ui', 'jquery.timepicker']
            },
            'underscore': {
                deps: ['underscore.string'],
                exports: '_'
            },
            'backbone': {
                deps: ['underscore', 'jquery'],
                exports: 'Backbone'
            },
            'backbone.associations': {
                deps: ['backbone'],
                exports: 'Backbone.Associations'
            },
            'backbone.paginator': {
                deps: ['backbone'],
                exports: 'Backbone.PageableCollection'
            },
            'backbone-super': {
                deps: ['backbone']
            },
            'paging-collection': {
                deps: ['jquery', 'underscore', 'backbone.paginator']
            },
            'youtube': {
                exports: 'YT'
            },
            'Markdown.Converter': {
                deps: ['mathjax'],
                exports: 'Markdown.Converter'
            },
            'Markdown.Editor': {
                deps: ['Markdown.Converter', 'gettext', 'underscore'],
                exports: 'Markdown.Editor'
            },
            'Markdown.Sanitizer': {
                deps: ['Markdown.Converter'],
                exports: 'Markdown.Sanitizer'
            },
            '_split': {
                exports: '_split'
            },
            'MathJaxProcessor': {
                deps: [
                    'Markdown.Converter', 'Markdown.Sanitizer', 'Markdown.Editor', '_split', 'mathjax_delay_renderer'
                ],
                exports: 'MathJaxProcessor'
            },
            'codemirror': {
                exports: 'CodeMirror'
            },
            'tinymce': {
                exports: 'tinymce'
            },
            'mathjax': {
                exports: 'MathJax',
                init: function() {
                    MathJax.Hub.Config({
                        tex2jax: {
                            inlineMath: [['\\(', '\\)'], ['[mathjaxinline]', '[/mathjaxinline]']],
                            displayMath: [['\\[', '\\]'], ['[mathjax]', '[/mathjax]']]
                        }
                    });
                    return MathJax.Hub.Configured();
                }
            },
            'URI': {
                exports: 'URI'
            },
            'xmodule': {
                exports: 'XModule'
            },
            'logger': {
                exports: 'Logger'
            },
            'sinon': {
                exports: 'sinon'
            },
            'jasmine-imagediff': {},
            'common/js/spec_helpers/jasmine-extensions': {
                deps: ['jquery']
            },
            'common/js/spec_helpers/jasmine-stealth': {
                deps: ['underscore', 'underscore.string']
            },
            'common/js/spec_helpers/jasmine-waituntil': {
                deps: ['jquery']
            },
            'xblock/core': {
                exports: 'XBlock',
                deps: ['jquery', 'jquery.immediateDescendents']
            },
            'xblock/runtime.v1': {
                exports: 'XBlock.Runtime.v1',
                deps: ['xblock/core']
            },
            'xblock/lms.runtime.v1': {
                exports: 'LmsRuntime.v1',
                deps: ['xblock/runtime.v1']
            },
            'xmodule_js/common_static/js/test/add_ajax_prefix': {
                exports: 'AjaxPrefix',
                deps: ['coffee/src/ajax_prefix']
            },
            'coffee/src/instructor_dashboard/util': {
                exports: 'coffee/src/instructor_dashboard/util',
                deps: ['jquery', 'underscore', 'slick.core', 'slick.grid'],
                init: function() {
                    // Set global variables that the util code is expecting to be defined
                    require([
                        'edx-ui-toolkit/js/utils/html-utils',
                        'edx-ui-toolkit/js/utils/string-utils'
                    ], function(HtmlUtils, StringUtils) {
                        window.edx = edx || {};
                        window.edx.HtmlUtils = HtmlUtils;
                        window.edx.StringUtils = StringUtils;
                    });
                }
            },
            'coffee/src/instructor_dashboard/student_admin': {
                exports: 'coffee/src/instructor_dashboard/student_admin',
                deps: ['jquery', 'underscore', 'coffee/src/instructor_dashboard/util', 'string_utils']
            },
            'js/instructor_dashboard/certificates': {
                exports: 'js/instructor_dashboard/certificates',
                deps: ['jquery', 'gettext', 'underscore']
            },
            // LMS class loaded explicitly until they are converted to use RequireJS
            'js/student_account/account': {
                exports: 'js/student_account/account',
                deps: ['jquery', 'underscore', 'backbone', 'gettext', 'jquery.cookie']
            },
            'js/staff_debug_actions': {
                exports: 'js/staff_debug_actions',
                deps: ['gettext']
            },
            'js/dashboard/donation.js': {
                exports: 'js/dashboard/donation',
                deps: ['jquery', 'underscore', 'gettext']
            },
            'js/dashboard/dropdown.js': {
                exports: 'js/dashboard/dropdown',
                deps: ['jquery']
            },
            'js/shoppingcart/shoppingcart.js': {
                exports: 'js/shoppingcart/shoppingcart',
                deps: ['jquery', 'underscore', 'gettext']
            },
            'js/ccx/schedule': {
                exports: 'js/ccx/schedule',
                deps: ['jquery', 'underscore', 'backbone', 'gettext', 'moment']
            },
            'js/commerce/views/receipt_view': {
                exports: 'edx.commerce.ReceiptView',
                deps: ['jquery', 'jquery.url', 'backbone', 'underscore', 'string_utils']
            },

            // Backbone classes loaded explicitly until they are converted to use RequireJS
            'js/instructor_dashboard/ecommerce': {
                exports: 'edx.instructor_dashboard.ecommerce.ExpiryCouponView',
                deps: ['backbone', 'jquery', 'underscore']
            },
            'js/models/notification': {
                exports: 'NotificationModel',
                deps: ['backbone']
            },
            'js/views/notification': {
                exports: 'NotificationView',
                deps: ['backbone', 'jquery', 'underscore']
            },
            'js/views/file_uploader': {
                exports: 'FileUploaderView',
                deps: [
                    'backbone', 'jquery', 'underscore', 'gettext', 'string_utils', 'js/views/notification',
                    'js/models/notification', 'jquery.fileupload'
                ]
            },
            'js/verify_student/models/verification_model': {
                exports: 'edx.verify_student.VerificationModel',
                deps: ['jquery', 'underscore', 'backbone', 'jquery.cookie']
            },
            'js/verify_student/views/error_view': {
                exports: 'edx.verify_student.ErrorView',
                deps: ['jquery', 'underscore', 'backbone']
            },
            'js/verify_student/views/webcam_photo_view': {
                exports: 'edx.verify_student.WebcamPhotoView',
                deps: [
                    'jquery',
                    'underscore',
                    'backbone',
                    'gettext',
                    'js/verify_student/views/image_input_view'
                ]
            },
            'js/verify_student/views/image_input_view': {
                exports: 'edx.verify_student.ImageInputView',
                deps: ['jquery', 'underscore', 'backbone', 'gettext']
            },
            'js/verify_student/views/step_view': {
                exports: 'edx.verify_student.StepView',
                deps: ['jquery', 'underscore', 'underscore.string', 'backbone', 'gettext'],
                init: function() {
                    // Set global variables that the payment code is expecting to be defined
                    require([
                        'underscore',
                        'underscore.string',
                        'edx-ui-toolkit/js/utils/html-utils',
                        'edx-ui-toolkit/js/utils/string-utils'
                    ], function (_, str, HtmlUtils, StringUtils) {
                        window._ = _;
                        window._.str = str;
                        window.edx = edx || {};
                        window.edx.HtmlUtils = HtmlUtils;
                        window.edx.StringUtils = StringUtils;
                    });
                }
            },
            'js/verify_student/views/intro_step_view': {
                exports: 'edx.verify_student.IntroStepView',
                deps: [
                    'jquery',
                    'js/verify_student/views/step_view'
                ]
            },
            'js/verify_student/views/make_payment_step_view': {
                exports: 'edx.verify_student.MakePaymentStepView',
                deps: [
                    'jquery',
                    'underscore',
                    'gettext',
                    'jquery.cookie',
                    'jquery.url',
                    'string_utils',
                    'js/verify_student/views/step_view'
                ]
            },
            'js/verify_student/views/payment_confirmation_step_view': {
                exports: 'edx.verify_student.PaymentConfirmationStepView',
                deps: [
                    'jquery',
                    'underscore',
                    'gettext',
                    'js/verify_student/views/step_view'
                ]
            },
            'js/verify_student/views/face_photo_step_view': {
                exports: 'edx.verify_student.FacePhotoStepView',
                deps: [
                    'jquery',
                    'underscore',
                    'gettext',
                    'js/verify_student/views/step_view',
                    'js/verify_student/views/webcam_photo_view'
                ]
            },
            'js/verify_student/views/id_photo_step_view': {
                exports: 'edx.verify_student.IDPhotoStepView',
                deps: [
                    'jquery',
                    'underscore',
                    'gettext',
                    'js/verify_student/views/step_view',
                    'js/verify_student/views/webcam_photo_view'
                ]
            },
            'js/verify_student/views/review_photos_step_view': {
                exports: 'edx.verify_student.ReviewPhotosStepView',
                deps: [
                    'jquery',
                    'underscore',
                    'gettext',
                    'js/verify_student/views/step_view',
                    'js/verify_student/views/webcam_photo_view'
                ]
            },
            'js/verify_student/views/enrollment_confirmation_step_view': {
                exports: 'edx.verify_student.EnrollmentConfirmationStepView',
                deps: [
                    'jquery',
                    'js/verify_student/views/step_view'
                ]
            },
            'js/verify_student/views/reverify_success_step_view': {
                exports: 'edx.verify_student.ReverifySuccessStepView',
                deps: [
                    'jquery',
                    'js/verify_student/views/step_view'
                ]
            },
            'js/verify_student/views/pay_and_verify_view': {
                exports: 'edx.verify_student.PayAndVerifyView',
                deps: [
                    'jquery',
                    'underscore',
                    'backbone',
                    'gettext',
                    'js/verify_student/models/verification_model',
                    'js/verify_student/views/intro_step_view',
                    'js/verify_student/views/make_payment_step_view',
                    'js/verify_student/views/payment_confirmation_step_view',
                    'js/verify_student/views/face_photo_step_view',
                    'js/verify_student/views/id_photo_step_view',
                    'js/verify_student/views/review_photos_step_view',
                    'js/verify_student/views/enrollment_confirmation_step_view'
                ]
            },
            'js/verify_student/views/reverify_view': {
                exports: 'edx.verify_student.ReverifyView',
                deps: [
                    'jquery',
                    'underscore',
                    'backbone',
                    'gettext',
                    'js/verify_student/models/verification_model',
                    'js/verify_student/views/face_photo_step_view',
                    'js/verify_student/views/id_photo_step_view',
                    'js/verify_student/views/enrollment_confirmation_step_view',
                    'js/verify_student/views/reverify_success_step_view'
                ]
            },
            // Student Notes
            'annotator_1.2.9': {
                exports: 'Annotator',
                deps: ['jquery']
            },
            'slick.core': {
                deps: ['jquery'],
                exports: 'Slick'
            },
            'slick.grid': {
                deps: ['jquery', 'jquery.eventDrag', 'slick.core'],
                exports: 'Slick'
            },
            // Discussions
            'xmodule_js/common_static/common/js/discussion/utils': {
                deps: [
                    'jquery',
                    'jquery.timeago',
                    'underscore',
                    'backbone',
                    'gettext',
                    'MathJaxProcessor',
                    'URI'
                ],
                exports: 'DiscussionUtil',
                init: function() {
                    // Set global variables that the discussion code is expecting to be defined
                    require(['backbone', 'URI'], function(Backbone, URI) {
                        window.Backbone = Backbone;
                        window.URI = URI;
                    });
                }
            },
            'xmodule_js/common_static/common/js/discussion/content': {
                deps: [
                    'xmodule_js/common_static/common/js/discussion/utils'
                ],
                exports: 'Content'
            },
            'xmodule_js/common_static/common/js/discussion/discussion': {
                deps: [
                    'xmodule_js/common_static/common/js/discussion/utils',
                    'xmodule_js/common_static/common/js/discussion/content'
                ],
                exports: 'Discussion'
            },
            'xmodule_js/common_static/common/js/discussion/models/discussion_course_settings': {
                deps: [
                    'xmodule_js/common_static/common/js/discussion/utils'
                ],
                exports: 'DiscussionCourseSettings'
            },
            'xmodule_js/common_static/common/js/discussion/models/discussion_user': {
                deps: [
                    'xmodule_js/common_static/common/js/discussion/utils'
                ],
                exports: 'DiscussionUser'
            },
            'xmodule_js/common_static/common/js/discussion/views/discussion_content_view': {
                deps: [
                    'xmodule_js/common_static/common/js/discussion/utils'
                ],
                exports: 'DiscussionContentView'
            },
            'xmodule_js/common_static/common/js/discussion/views/discussion_thread_edit_view': {
                deps: [
                    'xmodule_js/common_static/common/js/discussion/utils'
                ],
                exports: 'DiscussionThreadEditView'
            },
            'xmodule_js/common_static/common/js/discussion/views/discussion_thread_list_view': {
                deps: [
                    'xmodule_js/common_static/common/js/discussion/utils'
                ],
                exports: 'DiscussionThreadListView'
            },
            'xmodule_js/common_static/common/js/discussion/views/discussion_thread_profile_view': {
                deps: [
                    'xmodule_js/common_static/common/js/discussion/utils'
                ],
                exports: 'DiscussionThreadProfileView'
            },
            'xmodule_js/common_static/common/js/discussion/views/discussion_thread_show_view': {
                deps: [
                    'xmodule_js/common_static/common/js/discussion/utils',
                    'xmodule_js/common_static/common/js/discussion/views/discussion_content_view'
                ],
                exports: 'DiscussionThreadShowView'
            },
            'xmodule_js/common_static/common/js/discussion/views/discussion_thread_view': {
                deps: [
                    'xmodule_js/common_static/common/js/discussion/utils',
                    'xmodule_js/common_static/common/js/discussion/views/discussion_content_view'
                ],
                exports: 'DiscussionThreadView'
            },
            'xmodule_js/common_static/common/js/discussion/views/discussion_topic_menu_view': {
                deps: [
                    'xmodule_js/common_static/common/js/discussion/utils'
                ],
                exports: 'DiscussionTopicMenuView'
            },
            'xmodule_js/common_static/common/js/discussion/views/discussion_user_profile_view': {
                deps: [
                    'xmodule_js/common_static/common/js/discussion/utils'
                ],
                exports: 'DiscussionUserProfileView'
            },
            'xmodule_js/common_static/common/js/discussion/views/new_post_view': {
                deps: [
                    'xmodule_js/common_static/common/js/discussion/utils'
                ],
                exports: 'NewPostView'
            },
            'xmodule_js/common_static/common/js/discussion/views/thread_response_edit_view': {
                deps: [
                    'xmodule_js/common_static/common/js/discussion/utils'
                ],
                exports: 'ThreadResponseEditView'
            },
            'xmodule_js/common_static/common/js/discussion/views/thread_response_show_view': {
                deps: [
                    'xmodule_js/common_static/common/js/discussion/utils'
                ],
                exports: 'ThreadResponseShowView'
            },
            'xmodule_js/common_static/common/js/discussion/views/thread_response_view': {
                deps: [
                    'xmodule_js/common_static/common/js/discussion/utils'
                ],
                exports: 'ThreadResponseView'
            },
            'DiscussionModuleView': {
                deps: [
                    'jquery',
                    'underscore',
                    'backbone',
                    'gettext',
                    'URI',
                    'xmodule_js/common_static/common/js/discussion/content',
                    'xmodule_js/common_static/common/js/discussion/discussion',
                    'xmodule_js/common_static/common/js/discussion/utils',
                    'xmodule_js/common_static/common/js/discussion/models/discussion_course_settings',
                    'xmodule_js/common_static/common/js/discussion/models/discussion_user',
                    'xmodule_js/common_static/common/js/discussion/views/discussion_content_view',
                    'xmodule_js/common_static/common/js/discussion/views/discussion_thread_edit_view',
                    'xmodule_js/common_static/common/js/discussion/views/discussion_thread_list_view',
                    'xmodule_js/common_static/common/js/discussion/views/discussion_thread_profile_view',
                    'xmodule_js/common_static/common/js/discussion/views/discussion_thread_show_view',
                    'xmodule_js/common_static/common/js/discussion/views/discussion_thread_view',
                    'xmodule_js/common_static/common/js/discussion/views/discussion_topic_menu_view',
                    'xmodule_js/common_static/common/js/discussion/views/discussion_user_profile_view',
                    'xmodule_js/common_static/common/js/discussion/views/new_post_view',
                    'xmodule_js/common_static/common/js/discussion/views/thread_response_edit_view',
                    'xmodule_js/common_static/common/js/discussion/views/thread_response_show_view',
                    'xmodule_js/common_static/common/js/discussion/views/thread_response_view'
                ],
                exports: 'DiscussionModuleView'
            },
            'xmodule_js/common_static/common/js/spec_helpers/discussion_spec_helper': {
                deps: [
                    'xmodule_js/common_static/common/js/discussion/utils'
                ],
                exports: 'DiscussionSpecHelper'
            },
            'modernizr': {
                exports: 'Modernizr'
            },
            'afontgarde': {
                exports: 'AFontGarde'
            }
        }
    });

    var testFiles = [
        'lms/js/spec/preview/preview_factory_spec.js',
        'js/spec/api_admin/catalog_preview_spec.js',
        'js/spec/courseware/bookmark_button_view_spec.js',
        'js/spec/courseware/bookmarks_list_view_spec.js',
        'js/spec/ccx/schedule_spec.js',
        'js/spec/commerce/receipt_view_spec.js',
        'js/spec/components/card/card_spec.js',
        'js/spec/components/header/header_spec.js',
        'js/spec/courseware/course_home_events_spec.js',
        'js/spec/courseware/link_clicked_events_spec.js',
        'js/spec/courseware/updates_visibility_spec.js',
        'js/spec/dashboard/donation.js',
        'js/spec/dashboard/dropdown_spec.js',
        'js/spec/dashboard/track_events_spec.js',
        'js/spec/discovery/collections/filters_spec.js',
        'js/spec/discovery/discovery_factory_spec.js',
        'js/spec/discovery/models/course_card_spec.js',
        'js/spec/discovery/models/course_directory_spec.js',
        'js/spec/discovery/models/facet_option_spec.js',
        'js/spec/discovery/models/filter_spec.js',
        'js/spec/discovery/models/search_state_spec.js',
        'js/spec/discovery/views/course_card_spec.js',
        'js/spec/discovery/views/courses_listing_spec.js',
        'js/spec/discovery/views/filter_bar_spec.js',
        'js/spec/discovery/views/refine_sidebar_spec.js',
        'js/spec/discovery/views/search_form_spec.js',
        'js/spec/edxnotes/collections/notes_spec.js',
        'js/spec/edxnotes/models/note_spec.js',
        'js/spec/edxnotes/models/tab_spec.js',
        'js/spec/edxnotes/plugins/accessibility_spec.js',
        'js/spec/edxnotes/plugins/caret_navigation_spec.js',
        'js/spec/edxnotes/plugins/events_spec.js',
        'js/spec/edxnotes/plugins/scroller_spec.js',
        'js/spec/edxnotes/plugins/store_error_handler_spec.js',
        'js/spec/edxnotes/utils/logger_spec.js',
        'js/spec/edxnotes/views/note_item_spec.js',
        'js/spec/edxnotes/views/notes_factory_spec.js',
        'js/spec/edxnotes/views/notes_page_spec.js',
        'js/spec/edxnotes/views/notes_visibility_factory_spec.js',
        'js/spec/edxnotes/views/search_box_spec.js',
        'js/spec/edxnotes/views/shim_spec.js',
        'js/spec/edxnotes/views/tab_item_spec.js',
        'js/spec/edxnotes/views/tab_view_spec.js',
        'js/spec/edxnotes/views/tabs/course_structure_spec.js',
        'js/spec/edxnotes/views/tabs/recent_activity_spec.js',
        'js/spec/edxnotes/views/tabs/search_results_spec.js',
        'js/spec/edxnotes/views/tabs/tags_spec.js',
        'js/spec/edxnotes/views/tabs_list_spec.js',
        'js/spec/edxnotes/views/visibility_decorator_spec.js',
        'js/spec/financial-assistance/financial_assistance_form_view_spec.js',
        'js/spec/groups/views/cohorts_spec.js',
        'js/spec/instructor_dashboard/certificates_bulk_exception_spec.js',
        'js/spec/instructor_dashboard/certificates_exception_spec.js',
        'js/spec/instructor_dashboard/certificates_invalidation_spec.js',
        'js/spec/instructor_dashboard/certificates_spec.js',
        'js/spec/instructor_dashboard/ecommerce_spec.js',
        'js/spec/instructor_dashboard/student_admin_spec.js',
        'js/spec/learner_dashboard/certificate_view_spec.js',
        'js/spec/learner_dashboard/collection_list_view_spec.js',
        'js/spec/learner_dashboard/program_card_view_spec.js',
        'js/spec/learner_dashboard/sidebar_view_spec.js',
        'js/spec/learner_dashboard/program_details_header_spec.js',
        'js/spec/learner_dashboard/course_card_view_spec.js',
        'js/spec/learner_dashboard/course_enroll_view_spec.js',
        'js/spec/markdown_editor_spec.js',
        'js/spec/navigation_spec.js',
        'js/spec/search/search_spec.js',
        'js/spec/shoppingcart/shoppingcart_spec.js',
        'js/spec/staff_debug_actions_spec.js',
        'js/spec/student_account/access_spec.js',
        'js/spec/student_account/account_settings_factory_spec.js',
        'js/spec/student_account/account_settings_fields_spec.js',
        'js/spec/student_account/account_settings_view_spec.js',
        'js/spec/student_account/account_spec.js',
        'js/spec/student_account/emailoptin_spec.js',
        'js/spec/student_account/enrollment_spec.js',
        'js/spec/student_account/finish_auth_spec.js',
        'js/spec/student_account/hinted_login_spec.js',
        'js/spec/student_account/institution_login_spec.js',
        'js/spec/student_account/login_spec.js',
        'js/spec/student_account/logistration_factory_spec.js',
        'js/spec/student_account/password_reset_spec.js',
        'js/spec/student_account/register_spec.js',
        'js/spec/student_account/shoppingcart_spec.js',
        'js/spec/student_profile/badge_list_container_spec.js',
        'js/spec/student_profile/badge_list_view_spec.js',
        'js/spec/student_profile/badge_view_spec.js',
        'js/spec/student_profile/learner_profile_factory_spec.js',
        'js/spec/student_profile/learner_profile_fields_spec.js',
        'js/spec/student_profile/learner_profile_view_spec.js',
        'js/spec/student_profile/section_two_tab_spec.js',
        'js/spec/student_profile/share_modal_view_spec.js',
        'js/spec/verify_student/image_input_spec.js',
        'js/spec/verify_student/make_payment_step_view_ab_testing_spec.js',
        'js/spec/verify_student/make_payment_step_view_spec.js',
        'js/spec/verify_student/pay_and_verify_view_spec.js',
        'js/spec/verify_student/reverify_view_spec.js',
        'js/spec/verify_student/review_photos_step_view_spec.js',
        'js/spec/verify_student/webcam_photo_view_spec.js',
        'js/spec/views/fields_spec.js',
        'js/spec/views/file_uploader_spec.js',
        'js/spec/views/message_banner_spec.js',
        'js/spec/views/notification_spec.js',
        'support/js/spec/collections/enrollment_spec.js',
        'support/js/spec/models/enrollment_spec.js',
        'support/js/spec/views/certificates_spec.js',
        'support/js/spec/views/enrollment_modal_spec.js',
        'support/js/spec/views/enrollment_spec.js',
        'teams/js/spec/collections/topic_collection_spec.js',
        'teams/js/spec/teams_tab_factory_spec.js',
        'teams/js/spec/views/edit_team_members_spec.js',
        'teams/js/spec/views/edit_team_spec.js',
        'teams/js/spec/views/instructor_tools_spec.js',
        'teams/js/spec/views/my_teams_spec.js',
        'teams/js/spec/views/team_card_spec.js',
        'teams/js/spec/views/team_discussion_spec.js',
        'teams/js/spec/views/team_profile_header_actions_spec.js',
        'teams/js/spec/views/team_profile_spec.js',
        'teams/js/spec/views/teams_spec.js',
        'teams/js/spec/views/teams_tab_spec.js',
        'teams/js/spec/views/topic_card_spec.js',
        'teams/js/spec/views/topic_teams_spec.js',
        'teams/js/spec/views/topics_spec.js'
    ];

    for (var i = 0; i < testFiles.length; i++) {
        testFiles[i] = '/base/' + testFiles[i];
    }

    var specHelpers = [
        'common/js/spec_helpers/jasmine-extensions',
        'common/js/spec_helpers/jasmine-stealth',
        'common/js/spec_helpers/jasmine-waituntil'
    ];

    // Jasmine has a global stack for creating a tree of specs. We need to load
    // spec files one by one, otherwise some end up getting nested under others.
    window.requireSerial(specHelpers.concat(testFiles), function() {
        // start test run, once Require.js is done
        window.__karma__.start();
    });
}).call(this, requirejs);
