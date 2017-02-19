/* globals DiscussionThreadListView, DiscussionThreadView, DiscussionUtil, NewPostView */
(function() {
    'use strict';
    var __hasProp = {}.hasOwnProperty,
        __extends = function(child, parent) {
            for (var key in parent) {
                if (__hasProp.call(parent, key)) {
                    child[key] = parent[key];
                }
            }
            function ctor() {
                this.constructor = child;
            }

            ctor.prototype = parent.prototype;
            child.prototype = new ctor();
            child.__super__ = parent.prototype;
            return child;
        };

    if (typeof Backbone !== "undefined" && Backbone !== null) {
        this.DiscussionRouter = (function(_super) {

            __extends(DiscussionRouter, _super);

            function DiscussionRouter() {
                var self = this;
                this.hideNewPost = function() {
                    return DiscussionRouter.prototype.hideNewPost.apply(self, arguments);
                };
                this.showNewPost = function() {
                    return DiscussionRouter.prototype.showNewPost.apply(self, arguments);
                };
                this.navigateToAllThreads = function() {
                    return DiscussionRouter.prototype.navigateToAllThreads.apply(self, arguments);
                };
                this.navigateToThread = function() {
                    return DiscussionRouter.prototype.navigateToThread.apply(self, arguments);
                };
                this.showMain = function() {
                    return DiscussionRouter.prototype.showMain.apply(self, arguments);
                };
                this.setActiveThread = function() {
                    return DiscussionRouter.prototype.setActiveThread.apply(self, arguments);
                };
                return DiscussionRouter.__super__.constructor.apply(this, arguments);
            }

            DiscussionRouter.prototype.routes = {
                "": "allThreads",
                ":forum_name/threads/:thread_id": "showThread"
            };

            DiscussionRouter.prototype.initialize = function(options) {
                var self = this;
                this.discussion = options.discussion;
                this.course_settings = options.course_settings;
                this.nav = new DiscussionThreadListView({
                    collection: this.discussion,
                    el: $(".forum-nav"),
                    courseSettings: this.course_settings
                });
                this.nav.on("thread:selected", this.navigateToThread);
                this.nav.on("thread:removed", this.navigateToAllThreads);
                this.nav.on("threads:rendered", this.setActiveThread);
                this.nav.on("thread:created", this.navigateToThread);
                this.nav.render();
                this.newPost = $('.new-post-article');
                this.newPostView = new NewPostView({
                    el: this.newPost,
                    collection: this.discussion,
                    course_settings: this.course_settings,
                    mode: "tab"
                });
                this.newPostView.render();
                this.listenTo(this.newPostView, 'newPost:cancel', this.hideNewPost);
                $('.new-post-btn').bind("click", this.showNewPost);
                return $('.new-post-btn').bind("keydown", function(event) {
                    return DiscussionUtil.activateOnSpace(event, self.showNewPost);
                });
            };

            DiscussionRouter.prototype.allThreads = function() {
                this.nav.updateSidebar();
                return this.nav.goHome();
            };

            DiscussionRouter.prototype.setActiveThread = function() {
                if (this.thread) {
                    return this.nav.setActiveThread(this.thread.get("id"));
                } else {
                    return this.nav.goHome;
                }
            };

            DiscussionRouter.prototype.showThread = function(forum_name, thread_id) {
                this.thread = this.discussion.get(thread_id);
                this.thread.set("unread_comments_count", 0);
                this.thread.set("read", true);
                this.setActiveThread();
                return this.showMain();
            };

            DiscussionRouter.prototype.showMain = function() {
                var self = this;
                if (this.main) {
                    this.main.cleanup();
                    this.main.undelegateEvents();
                }
                if (!($(".forum-content").is(":visible"))) {
                    $(".forum-content").fadeIn();
                }
                if (this.newPost.is(":visible")) {
                    this.newPost.fadeOut();
                }
                this.main = new DiscussionThreadView({
                    el: $(".forum-content"),
                    model: this.thread,
                    mode: "tab",
                    course_settings: this.course_settings
                });
                this.main.render();
                this.main.on("thread:responses:rendered", function() {
                    return self.nav.updateSidebar();
                });
                return this.thread.on("thread:thread_type_updated", this.showMain);
            };

            DiscussionRouter.prototype.navigateToThread = function(thread_id) {
                var thread;
                thread = this.discussion.get(thread_id);
                return this.navigate("" + (thread.get("commentable_id")) + "/threads/" + thread_id, {
                    trigger: true
                });
            };

            DiscussionRouter.prototype.navigateToAllThreads = function() {
                return this.navigate("", {
                    trigger: true
                });
            };

            DiscussionRouter.prototype.showNewPost = function() {
                var self = this;
                return $('.forum-content').fadeOut({
                    duration: 200,
                    complete: function() {
                        return self.newPost.fadeIn(200).focus();
                    }
                });
            };

            DiscussionRouter.prototype.hideNewPost = function() {
                return this.newPost.fadeOut({
                    duration: 200,
                    complete: function() {
                        return $('.forum-content').fadeIn(200).find('.thread-wrapper').focus();
                    }
                });
            };

            return DiscussionRouter;

        })(Backbone.Router);
    }

}).call(window);
