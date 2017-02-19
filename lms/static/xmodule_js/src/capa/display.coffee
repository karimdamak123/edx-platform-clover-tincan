class @Problem

  constructor: (element) ->
    @el = $(element).find('.problems-wrapper')
    @id = @el.data('problem-id')
    @element_id = @el.attr('id')
    @url = @el.data('url')
    @content = @el.data('content')

    # has_timed_out and has_response are used to ensure that are used to
    # ensure that we wait a minimum of ~ 1s before transitioning the check
    # button from disabled to enabled
    @has_timed_out = false
    @has_response = false

    @render(@content)

  $: (selector) ->
    $(selector, @el)

  bind: =>
    if MathJax?
      @el.find('.problem > div').each (index, element) =>
        MathJax.Hub.Queue ["Typeset", MathJax.Hub, element]

    window.update_schematics()

    problem_prefix = @element_id.replace(/problem_/,'')
    @inputs = @$("[id^='input_#{problem_prefix}_']")
    @$('div.action button').click @refreshAnswers
    @checkButton = @$('div.action button.check')
    @checkButtonLabel = @$('div.action button.check span.check-label')
    @checkButtonCheckText = @checkButtonLabel.text()
    @checkButtonCheckingText = @checkButton.data('checking')
    @checkButton.click @check_fd
    @hintButton = @$('div.action button.hint-button')
    @hintButton.click @hint_button
    @resetButton = @$('div.action button.reset')
    @resetButton.click @reset
    @showButton = @$('div.action button.show')
    @showButton.click @show
    @saveButton = @$('div.action button.save')
    @saveButton.click @save

    # Accessibility helper for sighted keyboard users to show <clarification> tooltips on focus:
    @$('.clarification').focus (ev) =>
      icon = $(ev.target).children "i"
      window.globalTooltipManager.openTooltip icon
    @$('.clarification').blur (ev) =>
      window.globalTooltipManager.hide()

    @bindResetCorrectness()
    if @checkButton.length
      @checkAnswersAndCheckButton true

    # Collapsibles
    Collapsible.setCollapsibles(@el)

    # Dynamath
    @$('input.math').keyup(@refreshMath)
    if MathJax?
      @$('input.math').each (index, element) =>
        MathJax.Hub.Queue [@refreshMath, null, element]

  renderProgressState: =>
    detail = @el.data('progress_detail')
    status = @el.data('progress_status')

    # Render 'x/y point(s)' if student has attempted question
    if status != 'none' and detail? and detail.indexOf('/') > 0
        a = detail.split('/')
        earned = parseFloat(a[0])
        possible = parseFloat(a[1])
        # This comment needs to be on one line to be properly scraped for the translators. Sry for length.
        `// Translators: %(earned)s is the number of points earned. %(total)s is the total number of points (examples: 0/1, 1/1, 2/3, 5/10). The total number of points will always be at least 1. We pluralize based on the total number of points (example: 0/1 point; 1/2 points)`
        progress_template = ngettext('(%(earned)s/%(possible)s point)', '(%(earned)s/%(possible)s points)', possible)
        progress = interpolate(progress_template, {'earned': earned, 'possible': possible}, true)

    # Render 'x point(s) possible' if student has not yet attempted question
    if status == 'none' and detail? and detail.indexOf('/') > 0
        a = detail.split('/')
        possible = parseFloat(a[1])
        `// Translators: %(num_points)s is the number of points possible (examples: 1, 3, 10). There will always be at least 1 point possible.`
        progress_template = ngettext("(%(num_points)s point possible)", "(%(num_points)s points possible)", possible)
        progress = interpolate(progress_template, {'num_points': possible}, true)

    @$('.problem-progress').html(progress)

  updateProgress: (response) =>
    if response.progress_changed
        @el.data('progress_status', response.progress_status)
        @el.data('progress_detail', response.progress_detail)
        @el.trigger('progressChanged')
    @renderProgressState()

  forceUpdate: (response) =>
    @el.data('progress_status', response.progress_status)
    @el.data('progress_detail', response.progress_detail)
    @el.trigger('progressChanged')
    @renderProgressState()

  queueing: =>
    @queued_items = @$(".xqueue")
    @num_queued_items = @queued_items.length
    if @num_queued_items > 0
      if window.queuePollerID # Only one poller 'thread' per Problem
        window.clearTimeout(window.queuePollerID)
      window.queuePollerID = window.setTimeout(
        => @poll(1000),
        1000)

  poll: (prev_timeout) =>
    $.postWithPrefix "#{@url}/problem_get", (response) =>
      # If queueing status changed, then render
      @new_queued_items = $(response.html).find(".xqueue")
      if @new_queued_items.length isnt @num_queued_items
        @el.html(response.html)
        JavascriptLoader.executeModuleScripts @el, () =>
          @setupInputTypes()
          @bind()

      @num_queued_items = @new_queued_items.length
      if @num_queued_items == 0
        @forceUpdate response
        delete window.queuePollerID
      else
        new_timeout = prev_timeout * 2
        # if the timeout is greather than 1 minute
        if new_timeout >= 60000
          delete window.queuePollerID
          @gentle_alert gettext("The grading process is still running. Refresh the page to see updates.")
        else
          window.queuePollerID = window.setTimeout(
            => @poll(new_timeout),
            new_timeout
          )


  # Use this if you want to make an ajax call on the input type object
  # static method so you don't have to instantiate a Problem in order to use it
  # Input:
  #   url: the AJAX url of the problem
  #   input_id: the input_id of the input you would like to make the call on
  #     NOTE: the id is the ${id} part of "input_${id}" during rendering
  #           If this function is passed the entire prefixed id, the backend may have trouble
  #           finding the correct input
  #   dispatch: string that indicates how this data should be handled by the inputtype
  #   callback: the function that will be called once the AJAX call has been completed.
  #             It will be passed a response object
  @inputAjax: (url, input_id, dispatch, data, callback) ->
    data['dispatch'] = dispatch
    data['input_id'] = input_id
    $.postWithPrefix "#{url}/input_ajax", data, callback


  render: (content) ->
    if content
      @el.attr({'aria-busy': 'true', 'aria-live': 'off', 'aria-atomic': 'false'})
      @el.html(content)
      JavascriptLoader.executeModuleScripts @el, () =>
        @setupInputTypes()
        @bind()
        @queueing()
        @renderProgressState()
      @el.attr('aria-busy', 'false')
    else
      $.postWithPrefix "#{@url}/problem_get", (response) =>
        @el.html(response.html)
        JavascriptLoader.executeModuleScripts @el, () =>
          @setupInputTypes()
          @bind()
          @queueing()
          @forceUpdate response

  # TODO add hooks for problem types here by inspecting response.html and doing
  # stuff if a div w a class is found

  setupInputTypes: =>
    @inputtypeDisplays = {}
    @el.find(".capa_inputtype").each (index, inputtype) =>
      classes = $(inputtype).attr('class').split(' ')
      id = $(inputtype).attr('id')
      for cls in classes
        setupMethod = @inputtypeSetupMethods[cls]
        if setupMethod?
          @inputtypeDisplays[id] = setupMethod(inputtype)

  # If some function wants to be called before sending the answer to the
  # server, give it a chance to do so.
  #
  # check_save_waitfor allows the callee to send alerts if the user's input is
  # invalid. To do so, the callee must throw an exception named "Waitfor
  # Exception". This and any other errors or exceptions that arise from the
  # callee are rethrown and abort the submission.
  #
  # In order to use this feature, add a 'data-waitfor' attribute to the input,
  # and specify the function to be called by the check button before sending
  # off @answers
  check_save_waitfor: (callback) =>
    flag = false
    for inp in @inputs
      if ($(inp).is("input[waitfor]"))
        try
          $(inp).data("waitfor")(() =>
            @refreshAnswers()
            callback()
          )
        catch e
          if e.name == "Waitfor Exception"
            alert e.message
          else
            alert "Could not grade your answer. The submission was aborted."
          throw e
        flag = true
      else
        flag = false
    return flag


  ###
  # 'check_fd' uses FormData to allow file submissions in the 'problem_check' dispatch,
  #      in addition to simple querystring-based answers
  #
  # NOTE: The dispatch 'problem_check' is being singled out for the use of FormData;
  #       maybe preferable to consolidate all dispatches to use FormData
  ###
  check_fd: =>
    # If there are no file inputs in the problem, we can fall back on @check
    if @el.find('input:file').length == 0
      @check()
      return

    @enableCheckButton false

    if not window.FormData
      alert "Submission aborted! Sorry, your browser does not support file uploads. If you can, please use Chrome or Safari which have been verified to support file uploads."
      @enableCheckButton true
      return

    timeout_id = @enableCheckButtonAfterTimeout()

    fd = new FormData()

    # Sanity checks on submission
    max_filesize = 4*1000*1000 # 4 MB
    file_too_large = false
    file_not_selected = false
    required_files_not_submitted = false
    unallowed_file_submitted = false

    errors = []

    @inputs.each (index, element) ->
      if element.type is 'file'
        required_files = $(element).data("required_files")
        allowed_files  = $(element).data("allowed_files")
        for file in element.files
          if allowed_files.length != 0 and file.name not in allowed_files
            unallowed_file_submitted = true
            errors.push "You submitted #{file.name}; only #{allowed_files} are allowed."
          if file.name in required_files
            required_files.splice(required_files.indexOf(file.name), 1)
          if file.size > max_filesize
            file_too_large = true
            max_size = max_filesize / (1000*1000)
            errors.push "Your file #{file.name} is too large (max size: {max_size}MB)"
          fd.append(element.id, file)
        if element.files.length == 0
          file_not_selected = true
          fd.append(element.id, '') # In case we want to allow submissions with no file
        if required_files.length != 0
          required_files_not_submitted = true
          errors.push "You did not submit the required files: #{required_files}."
      else
        fd.append(element.id, element.value)


    if file_not_selected
      errors.push 'You did not select any files to submit'

    error_html = '<ul>\n'
    for error in errors
      error_html += '<li>' + error + '</li>\n'
    error_html += '</ul>'
    @gentle_alert error_html

    abort_submission = file_too_large or file_not_selected or unallowed_file_submitted or required_files_not_submitted
    if abort_submission
      window.clearTimeout(timeout_id)
      @enableCheckButton true
      return

    settings =
      type: "POST"
      data: fd
      processData: false
      contentType: false
      complete: @enableCheckButtonAfterResponse
      success: (response) =>
        switch response.success
          when 'incorrect', 'correct'
            @render(response.contents)
            @updateProgress response
          else
            @gentle_alert response.success
        Logger.log 'problem_graded', [@answers, response.contents], @id

    $.ajaxWithPrefix("#{@url}/problem_check", settings)

  check: =>
    if not @check_save_waitfor(@check_internal)
      @disableAllButtonsWhileRunning @check_internal, true

  check_internal: =>
    Logger.log 'problem_check', @answers
    $.postWithPrefix "#{@url}/problem_check", @answers, (response) =>
      switch response.success
        when 'incorrect', 'correct'
          window.SR.readElts($(response.contents).find('.status'))
          @el.trigger('contentChanged', [@id, response.contents])
          @render(response.contents)
          @updateProgress response
          if @el.hasClass 'showed'
            @el.removeClass 'showed'
          @$('div.action button.check').focus()
        else
          @gentle_alert response.success
      Logger.log 'problem_graded', [@answers, response.contents], @id

  reset: =>
    @disableAllButtonsWhileRunning @reset_internal, false

  reset_internal: =>
    Logger.log 'problem_reset', @answers
    $.postWithPrefix "#{@url}/problem_reset", id: @id, (response) =>
        @el.trigger('contentChanged', [@id, response.html])
        @render(response.html)
        @updateProgress response

  # TODO this needs modification to deal with javascript responses; perhaps we
  # need something where responsetypes can define their own behavior when show
  # is called.
  show: =>
    if !@el.hasClass 'showed'
      Logger.log 'problem_show', problem: @id
      answer_text = []
      $.postWithPrefix "#{@url}/problem_show", (response) =>
        answers = response.answers
        $.each answers, (key, value) =>
          if $.isArray(value)
            for choice in value
              @$("label[for='input_#{key}_#{choice}']").attr correct_answer: 'true'
              answer_text.push('<p>' + gettext('Answer:') + ' ' + value + '</p>')
          else
            answer = @$("#answer_#{key}, #solution_#{key}")
            answer.html(value)
            Collapsible.setCollapsibles(answer)

            # Sometimes, `value` is just a string containing a MathJax formula.
            # If this is the case, jQuery will throw an error in some corner cases
            # because of an incorrect selector. We setup a try..catch so that
            # the script doesn't break in such cases.
            #
            # We will fallback to the second `if statement` below, if an
            # error is thrown by jQuery.
            try
                solution = $(value).find('.detailed-solution')
            catch e
                solution = {}
            if solution.length
              answer_text.push(solution)
            else
              answer_text.push('<p>' + gettext('Answer:') + ' ' + value + '</p>')

        # TODO remove the above once everything is extracted into its own
        # inputtype functions.

        @el.find(".capa_inputtype").each (index, inputtype) =>
          classes = $(inputtype).attr('class').split(' ')
          for cls in classes
            display = @inputtypeDisplays[$(inputtype).attr('id')]
            showMethod = @inputtypeShowAnswerMethods[cls]
            showMethod(inputtype, display, answers) if showMethod?

        if MathJax?
          @el.find('.problem > div').each (index, element) =>
            MathJax.Hub.Queue ["Typeset", MathJax.Hub, element]

        `// Translators: the word Answer here refers to the answer to a problem the student must solve.`
        @$('.show-label').text gettext('Hide Answer')
        @el.addClass 'showed'
        @updateProgress response
        window.SR.readElts(answer_text)
    else
      @$('[id^=answer_], [id^=solution_]').text ''
      @$('[correct_answer]').attr correct_answer: null
      @el.removeClass 'showed'
      `// Translators: the word Answer here refers to the answer to a problem the student must solve.`
      @$('.show-label').text gettext('Show Answer')
      window.SR.readText(gettext('Answer hidden'))

      @el.find(".capa_inputtype").each (index, inputtype) =>
        display = @inputtypeDisplays[$(inputtype).attr('id')]
        classes = $(inputtype).attr('class').split(' ')
        for cls in classes
          hideMethod = @inputtypeHideAnswerMethods[cls]
          hideMethod(inputtype, display) if hideMethod?

  gentle_alert: (msg) =>
    if @el.find('.capa_alert').length
      @el.find('.capa_alert').remove()
    alert_elem = "<div class='capa_alert'>" + msg + "</div>"
    @el.find('.action').after(alert_elem)
    @el.find('.capa_alert').css(opacity: 0).animate(opacity: 1, 700)
    window.SR.readElts @el.find('.capa_alert')

  save: =>
    if not @check_save_waitfor(@save_internal)
      @disableAllButtonsWhileRunning @save_internal, false

  save_internal: =>
    Logger.log 'problem_save', @answers
    $.postWithPrefix "#{@url}/problem_save", @answers, (response) =>
      saveMessage = response.msg
      if response.success
        @el.trigger('contentChanged', [@id, response.html])
      @gentle_alert saveMessage
      @updateProgress response

  refreshMath: (event, element) =>
    element = event.target unless element
    elid = element.id.replace(/^input_/,'')
    target = "display_" + elid

    # MathJax preprocessor is loaded by 'setupInputTypes'
    preprocessor_tag = "inputtype_" + elid
    mathjax_preprocessor = @inputtypeDisplays[preprocessor_tag]

    if MathJax? and jax = MathJax.Hub.getAllJax(target)[0]
      eqn = $(element).val()
      if mathjax_preprocessor
        eqn = mathjax_preprocessor(eqn)
      MathJax.Hub.Queue(['Text', jax, eqn], [@updateMathML, jax, element])

    return # Explicit return for CoffeeScript

  updateMathML: (jax, element) =>
    try
      $("##{element.id}_dynamath").val(jax.root.toMathML '')
    catch exception
      throw exception unless exception.restart
      if MathJax?
        MathJax.Callback.After [@refreshMath, jax], exception.restart

  refreshAnswers: =>
    @$('input.schematic').each (index, element) ->
      element.schematic.update_value()
    @$(".CodeMirror").each (index, element) ->
      element.CodeMirror.save() if element.CodeMirror.save
    @answers = @inputs.serialize()

  checkAnswersAndCheckButton: (bind=false) =>
    # Used to check available answers and if something is checked (or the answer is set in some textbox)
    # "Check"/"Final check" button becomes enabled. Otherwise it is disabled by default.
    # params:
    #   'bind' used on the first check to attach event handlers to input fields
    #     to change "Check"/"Final check" enable status in case of some manipulations with answers
    answered = true

    at_least_one_text_input_found = false
    one_text_input_filled = false
    @el.find("input:text").each (i, text_field) =>
      if $(text_field).is(':visible')
        at_least_one_text_input_found = true
        if $(text_field).val() isnt ''
          one_text_input_filled = true
        if bind
          $(text_field).on 'input', (e) =>
            @checkAnswersAndCheckButton()
            return
          return
    if at_least_one_text_input_found and not one_text_input_filled
      answered = false

    @el.find(".choicegroup").each (i, choicegroup_block) =>
      checked = false
      $(choicegroup_block).find("input[type=checkbox], input[type=radio]").each (j, checkbox_or_radio) =>
        if $(checkbox_or_radio).is(':checked')
          checked = true
        if bind
          $(checkbox_or_radio).on 'click', (e) =>
            @checkAnswersAndCheckButton()
            return
          return
      if not checked
        answered = false
        return

    @el.find("select").each (i, select_field) =>
      selected_option = $(select_field).find("option:selected").text().trim()
      if selected_option is ''
        answered = false
      if bind
        $(select_field).on 'change', (e) =>
          @checkAnswersAndCheckButton()
          return
        return

    if answered
      @enableCheckButton true
    else
      @enableCheckButton false, false

  bindResetCorrectness: ->
    # Loop through all input types
    # Bind the reset functions at that scope.
    $inputtypes = @el.find(".capa_inputtype").add(@el.find(".inputtype"))
    $inputtypes.each (index, inputtype) =>
      classes = $(inputtype).attr('class').split(' ')
      for cls in classes
        bindMethod = @bindResetCorrectnessByInputtype[cls]
        if bindMethod?
          bindMethod(inputtype)

  # Find all places where each input type displays its correct-ness
  # Replace them with their original state--'unanswered'.
  bindResetCorrectnessByInputtype:
    # These are run at the scope of the capa inputtype
    # They should set handlers on each <input> to reset the whole.
    formulaequationinput: (element) ->
      $(element).find('input').on 'input', ->
        $p = $(element).find('span.status')
        `// Translators: the word unanswered here is about answering a problem the student must solve.`
        $p.parent().removeClass().addClass "unsubmitted"

    choicegroup: (element) ->
      $element = $(element)
      id = ($element.attr('id').match /^inputtype_(.*)$/)[1]
      $element.find('input').on 'change', ->
        $status = $("#status_#{id}")
        if $status[0]  # We found a status icon.
          $status.removeClass().addClass "unanswered"
          $status.empty().css 'display', 'inline-block'
        else
          # Recreate the unanswered dot on left.
          $("<span>", {"class": "unanswered", "style": "display: inline-block;", "id": "status_#{id}"})

        $element.find("label").removeClass()

    'option-input': (element) ->
      $select = $(element).find('select')
      id = ($select.attr('id').match /^input_(.*)$/)[1]
      $select.on 'change', ->
        $status = $("#status_#{id}")
          .removeClass().addClass("unanswered")
          .find('span').text(gettext('Status: unsubmitted'))

    textline: (element) ->
      $(element).find('input').on 'input', ->
        $p = $(element).find('span.status')
        `// Translators: the word unanswered here is about answering a problem the student must solve.`
        $p.parent().removeClass("correct incorrect").addClass "unsubmitted"

  inputtypeSetupMethods:

    'text-input-dynamath': (element) =>
      ###
      Return: function (eqn) -> eqn that preprocesses the user formula input before
                it is fed into MathJax. Return 'false' if no preprocessor specified
      ###
      data = $(element).find('.text-input-dynamath_data')

      preprocessorClassName = data.data('preprocessor')
      preprocessorClass = window[preprocessorClassName]
      if not preprocessorClass?
        return false
      else
        preprocessor = new preprocessorClass()
        return preprocessor.fn

    javascriptinput: (element) =>

      data = $(element).find(".javascriptinput_data")

      params        = data.data("params")
      submission    = data.data("submission")
      evaluation    = data.data("evaluation")
      problemState  = data.data("problem_state")
      displayClass  = window[data.data('display_class')]

      if evaluation == ''
          evaluation = null

      container = $(element).find(".javascriptinput_container")
      submissionField = $(element).find(".javascriptinput_input")

      display = new displayClass(problemState, submission, evaluation, container, submissionField, params)
      display.render()

      return display

    cminput: (container) =>
      element = $(container).find("textarea")
      tabsize = element.data("tabsize")
      mode = element.data("mode")
      linenumbers = element.data("linenums")
      spaces = Array(parseInt(tabsize) + 1).join(" ")
      CodeMirror.fromTextArea element[0], {
          lineNumbers: linenumbers
          indentUnit: tabsize
          tabSize: tabsize
          mode: mode
          matchBrackets: true
          lineWrapping: true
          indentWithTabs: false
          smartIndent: false
          extraKeys: {
            "Esc": (cm) ->
              $(".grader-status").focus()
              return false
            "Tab": (cm) ->
              cm.replaceSelection(spaces, "end")
              return false
          }
        }

  inputtypeShowAnswerMethods:
    choicegroup: (element, display, answers) =>
      element = $(element)

      input_id = element.attr('id').replace(/inputtype_/,'')
      answer = answers[input_id]
      for choice in answer
        element.find("label[for='input_#{input_id}_#{choice}']").addClass 'choicegroup_correct'

    javascriptinput: (element, display, answers) =>
      answer_id = $(element).attr('id').split("_")[1...].join("_")
      answer = JSON.parse(answers[answer_id])
      display.showAnswer(answer)

    choicetextgroup: (element, display, answers) =>
      element = $(element)

      input_id = element.attr('id').replace(/inputtype_/,'')
      answer = answers[input_id]
      for choice in answer
        element.find("section#forinput#{choice}").addClass 'choicetextgroup_show_correct'

    imageinput: (element, display, answers) =>
      # answers is a dict of (answer_id, answer_text) for each answer for this
      # question.
      # @Examples:
      # {'anwser_id': {
      #   'rectangle': '(10,10)-(20,30);(12,12)-(40,60)',
      #   'regions': '[[10,10], [30,30], [10, 30], [30, 10]]'
      # } }
      types =
        rectangle: (ctx, coords) =>
          reg = /^\(([0-9]+),([0-9]+)\)-\(([0-9]+),([0-9]+)\)$/
          rects = coords.replace(/\s*/g, '').split(/;/)

          $.each rects, (index, rect) =>
            abs = Math.abs
            points = reg.exec(rect)
            if points
              width = abs(points[3] - points[1])
              height = abs(points[4] - points[2])

              ctx.rect(points[1], points[2], width, height)

          ctx.stroke()
          ctx.fill()

        regions: (ctx, coords) =>
          parseCoords = (coords) =>
            reg = JSON.parse(coords)

            # Regions is list of lists [region1, region2, region3, ...] where regionN
            # is disordered list of points: [[1,1], [100,100], [50,50], [20, 70]].
            # If there is only one region in the list, simpler notation can be used:
            # regions="[[10,10], [30,30], [10, 30], [30, 10]]" (without explicitly
            # setting outer list)
            if typeof reg[0][0][0] == "undefined"
              # we have [[1,2],[3,4],[5,6]] - single region
              # instead of [[[1,2],[3,4],[5,6], [[1,2],[3,4],[5,6]]]
              # or [[[1,2],[3,4],[5,6]]] - multiple regions syntax
              reg = [reg]

            return reg

          $.each parseCoords(coords), (index, region) =>
            ctx.beginPath()
            $.each region, (index, point) =>
              if index is 0
                ctx.moveTo(point[0], point[1])
              else
                ctx.lineTo(point[0], point[1]);

            ctx.closePath()
            ctx.stroke()
            ctx.fill()

      element = $(element)
      id = element.attr('id').replace(/inputtype_/,'')
      container = element.find("#answer_#{id}")
      canvas = document.createElement('canvas')
      canvas.width = container.data('width')
      canvas.height = container.data('height')

      if canvas.getContext
        ctx = canvas.getContext('2d')
      else
        return console.log 'Canvas is not supported.'

      ctx.fillStyle = 'rgba(255,255,255,.3)';
      ctx.strokeStyle = "#FF0000";
      ctx.lineWidth = "2";

      if answers[id]
        $.each answers[id], (key, value) =>
          types[key](ctx, value) if types[key]? and value
        container.html(canvas)
      else
        console.log "Answer is absent for image input with id=#{id}"

  inputtypeHideAnswerMethods:
    choicegroup: (element, display) =>
      element = $(element)
      element.find('label').removeClass('choicegroup_correct')

    javascriptinput: (element, display) =>
      display.hideAnswer()

    choicetextgroup: (element, display) =>
      element = $(element)
      element.find("section[id^='forinput']").removeClass('choicetextgroup_show_correct')

  disableAllButtonsWhileRunning: (operationCallback, isFromCheckOperation) =>
    # Used to keep the buttons disabled while operationCallback is running.
    # params:
    #   'operationCallback' is an operation to be run.
    #   'isFromCheckOperation' is a boolean to keep track if 'operationCallback' was
    #    @check, if so then text of check button will be changed as well.
    @enableAllButtons false, isFromCheckOperation
    operationCallback().always =>
      @enableAllButtons true, isFromCheckOperation

  enableAllButtons: (enable, isFromCheckOperation) =>
    # Used to enable/disable all buttons in problem.
    # params:
    #   'enable' is a boolean to determine enabling/disabling of buttons.
    #   'isFromCheckOperation' is a boolean to keep track if operation was initiated
    #    from @check so that text of check button will also be changed while disabling/enabling
    #    the check button.
    if enable
      @resetButton
        .add(@saveButton)
        .add(@hintButton)
        .add(@showButton)
        .removeClass('is-disabled')
        .attr({'aria-disabled': 'false'})
    else
      @resetButton
        .add(@saveButton)
        .add(@hintButton)
        .add(@showButton)
        .addClass('is-disabled')
        .attr({'aria-disabled': 'true'})

    @enableCheckButton enable, isFromCheckOperation

  enableCheckButton: (enable, changeText = true) =>
    # Used to disable check button to reduce chance of accidental double-submissions.
    # params:
    #   'enable' is a boolean to determine enabling/disabling of check button.
    #   'changeText' is a boolean to determine if there is need to change the
    #    text of check button as well.
    if enable
      @checkButton.removeClass 'is-disabled'
      @checkButton.attr({'aria-disabled': 'false'})
      if changeText
        @checkButtonLabel.text(@checkButtonCheckText)
    else
      @checkButton.addClass 'is-disabled'
      @checkButton.attr({'aria-disabled': 'true'})
      if changeText
        @checkButtonLabel.text(@checkButtonCheckingText)

  enableCheckButtonAfterResponse: =>
    @has_response = true
    if not @has_timed_out
      # Server has returned response before our timeout
      @enableCheckButton false
    else
      @enableCheckButton true

  enableCheckButtonAfterTimeout: =>
    @has_timed_out = false
    @has_response = false
    enableCheckButton = () =>
      @has_timed_out = true
      if @has_response
        @enableCheckButton true
    window.setTimeout(enableCheckButton, 750)

  hint_button: =>
    # Store the index of the currently shown hint as an attribute.
    # Use that to compute the next hint number when the button is clicked.
    hint_index = @$('.problem-hint').attr('hint_index')
    if hint_index == undefined
      next_index = 0
    else
      next_index = parseInt(hint_index) + 1
    $.postWithPrefix "#{@url}/hint_button", hint_index: next_index, input_id: @id, (response) =>
      hint_container = @.$('.problem-hint')
      hint_container.html(response.contents)
      MathJax.Hub.Queue [
        'Typeset'
        MathJax.Hub
        hint_container[0]
      ]
      hint_container.attr('hint_index', response.hint_index)
      @$('.hint-button').focus()  # a11y focus on click, like the Check button

