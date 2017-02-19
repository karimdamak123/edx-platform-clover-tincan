/* global $$course_id, Content, Discussion, DiscussionRouter, DiscussionCourseSettings,
          DiscussionUser, DiscussionUserProfileView, DiscussionUtil */
(function() {
    'use strict';
    var DiscussionApp, DiscussionProfileApp;

    if (typeof Backbone !== "undefined" && Backbone !== null) {
        DiscussionApp = {
            start: function(elem) {
                var content_info, course_settings, discussion, element, sort_preference, thread_pages, threads,
                    user, user_info;
                DiscussionUtil.loadRolesFromContainer();
                element = $(elem);
                window.$$course_id = element.data("course-id");
                window.courseName = element.data("course-name");
                user_info = element.data("user-info");
                sort_preference = element.data("sort-preference");
                threads = element.data("threads");
                thread_pages = element.data("thread-pages");
                content_info = element.data("content-info");
                user = new DiscussionUser(user_info);
                DiscussionUtil.setUser(user);
                window.user = user;
                Content.loadContentInfos(content_info);
                discussion = new Discussion(threads, {
                    pages: thread_pages,
                    sort: sort_preference
                });
                course_settings = new DiscussionCourseSettings(element.data("course-settings"));
                // suppressing Do not use 'new' for side effects.
                /* jshint -W031*/
                new DiscussionRouter({
                    discussion: discussion,
                    course_settings: course_settings
                });
                /* jshint +W031*/
                return Backbone.history.start({
                    pushState: true,
                    root: "/courses/" + $$course_id + "/discussion/forum/"
                });
            }
        };
        DiscussionProfileApp = {
            start: function(elem) {
                var element, numPages, page, threads, user_info;
                DiscussionUtil.loadRoles({
                    "Moderator": [],
                    "Administrator": [],
                    "Community TA": []
                });
                element = $(elem);
                window.$$course_id = element.data("course-id");
                threads = element.data("threads");
                user_info = element.data("user-info");
                window.user = new DiscussionUser(user_info);
                page = element.data("page");
                numPages = element.data("num-pages");
                return new DiscussionUserProfileView({
                    el: element,
                    collection: threads,
                    page: page,
                    numPages: numPages
                });
            }
        };
        $(function() {
            $("section.discussion").each(function(index, elem) {
                return DiscussionApp.start(elem);
            });
            return $("section.discussion-user-threads").each(function(index, elem) {
                return DiscussionProfileApp.start(elem);
            });
        });
    }

}).call(window);
