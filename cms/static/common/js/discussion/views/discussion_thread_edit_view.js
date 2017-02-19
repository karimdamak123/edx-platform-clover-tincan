/* globals DiscussionTopicMenuView, DiscussionUtil */
(function() {
    'use strict';
    if (Backbone) {
        this.DiscussionThreadEditView = Backbone.View.extend({
            tagName: 'form',
            events: {
                'submit': 'updateHandler',
                'click .post-cancel': 'cancelHandler'
            },

            attributes: {
                'class': 'discussion-post edit-post-form'
            },

            initialize: function(options) {
                this.container = options.container || $('.thread-content-wrapper');
                this.mode = options.mode || 'inline';
                this.course_settings = options.course_settings;
                this.threadType = this.model.get('thread_type');
                this.topicId = this.model.get('commentable_id');
                this.context = options.context || 'course';
                _.bindAll(this, 'updateHandler', 'cancelHandler');
                return this;
            },

            render: function() {
                var threadTypeTemplate,
                    formId = _.uniqueId("form-");
                this.template = _.template($('#thread-edit-template').html());
                this.$el.html(this.template(this.model.toJSON())).appendTo(this.container);
                this.submitBtn = this.$('.post-update');
                threadTypeTemplate = _.template($("#thread-type-template").html());
                this.addField(threadTypeTemplate({form_id: formId}));
                this.$("#" + formId + "-post-type-" + this.threadType).attr('checked', true);
                // Only allow the topic field for course threads, as standalone threads
                // cannot be moved.
                if (this.context === 'course') {
                    this.topicView = new DiscussionTopicMenuView({
                        topicId: this.topicId,
                        course_settings: this.course_settings
                    });
                    this.addField(this.topicView.render());
                }
                DiscussionUtil.makeWmdEditor(this.$el, $.proxy(this.$, this), 'edit-post-body');
                return this;
            },

            addField: function(fieldView) {
                this.$('.forum-edit-post-form-wrapper').append(fieldView);
                return this;
            },

            isTabMode: function() {
                return this.mode === 'tab';
            },

            save: function() {
                var title = this.$('.edit-post-title').val(),
                    threadType = this.$(".post-type-input:checked").val(),
                    body = this.$('.edit-post-body textarea').val(),
                    postData = {
                        title: title,
                        thread_type: threadType,
                        body: body
                    };
                if (this.topicView) {
                    postData.commentable_id = this.topicView.getCurrentTopicId();
                }

                return DiscussionUtil.safeAjax({
                    $elem: this.submitBtn,
                    $loading: this.submitBtn,
                    url: DiscussionUtil.urlFor('update_thread', this.model.id),
                    type: 'POST',
                    dataType: 'json',
                    data: postData,
                    error: DiscussionUtil.formErrorHandler(this.$('.post-errors')),
                    success: function() {
                        this.$('.edit-post-title').val('').attr('prev-text', '');
                        this.$('.edit-post-body textarea').val('').attr('prev-text', '');
                        this.$('.wmd-preview p').html('');
                        if (this.topicView) {
                            postData.courseware_title = this.topicView.getFullTopicName();
                        }
                        this.model.set(postData).unset('abbreviatedBody');
                        this.trigger('thread:updated');
                        if (this.threadType !== threadType) {
                            this.model.set("thread_type", threadType);
                            this.model.trigger('thread:thread_type_updated');
                            this.trigger('comment:endorse');
                        }
                    }.bind(this)
                });
            },

            updateHandler: function(event) {
                event.preventDefault();
                // this event is for the moment triggered and used nowhere.
                this.trigger('thread:update', event);
                this.save();
                return this;
            },

            cancelHandler: function(event) {
                event.preventDefault();
                this.trigger("thread:cancel_edit", event);
                this.remove();
                return this;
            }
        });
    }
}).call(window); // jshint ignore:line
