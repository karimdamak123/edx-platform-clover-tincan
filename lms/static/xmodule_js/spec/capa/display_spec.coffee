describe 'Problem', ->
  problem_content_default = readFixtures('problem_content.html')

  beforeEach ->
    # Stub MathJax
    window.MathJax =
      Hub: jasmine.createSpyObj('MathJax.Hub', ['getAllJax', 'Queue'])
      Callback: jasmine.createSpyObj('MathJax.Callback', ['After'])
    @stubbedJax = root: jasmine.createSpyObj('jax.root', ['toMathML'])
    MathJax.Hub.getAllJax.and.returnValue [@stubbedJax]
    window.update_schematics = ->
    spyOn SR, 'readElts'
    spyOn SR, 'readText'

    # Load this function from spec/helper.coffee
    # Note that if your test fails with a message like:
    # 'External request attempted for blah, which is not defined.'
    # this msg is coming from the stubRequests function else clause.
    jasmine.stubRequests()

    loadFixtures 'problem.html'

    spyOn Logger, 'log'
    spyOn($.fn, 'load').and.callFake (url, callback) ->
      $(@).html readFixtures('problem_content.html')
      callback()

  describe 'constructor', ->

    it 'set the element from html', ->
      @problem999 = new Problem ("
        <section class='xblock xblock-student_view xmodule_display xmodule_CapaModule' data-type='Problem'>
          <section id='problem_999'
                   class='problems-wrapper'
                   data-problem-id='i4x://edX/999/problem/Quiz'
                   data-url='/problem/quiz/'>
          </section>
        </section>
        ")
      expect(@problem999.element_id).toBe 'problem_999'

    it 'set the element from loadFixtures', ->
      @problem1 = new Problem($('.xblock-student_view'))
      expect(@problem1.element_id).toBe 'problem_1'

  describe 'bind', ->
    beforeEach ->
      spyOn window, 'update_schematics'
      MathJax.Hub.getAllJax.and.returnValue [@stubbedJax]
      @problem = new Problem($('.xblock-student_view'))

    it 'set mathjax typeset', ->
      expect(MathJax.Hub.Queue).toHaveBeenCalled()

    it 'update schematics', ->
      expect(window.update_schematics).toHaveBeenCalled()

    it 'bind answer refresh on button click', ->
      expect($('div.action button')).toHandleWith 'click', @problem.refreshAnswers

    it 'bind the check button', ->
      expect($('div.action button.check')).toHandleWith 'click', @problem.check_fd

    it 'bind the reset button', ->
      expect($('div.action button.reset')).toHandleWith 'click', @problem.reset

    it 'bind the show button', ->
      expect($('div.action button.show')).toHandleWith 'click', @problem.show

    it 'bind the save button', ->
      expect($('div.action button.save')).toHandleWith 'click', @problem.save

    it 'bind the math input', ->
      expect($('input.math')).toHandleWith 'keyup', @problem.refreshMath

  describe 'bind_with_custom_input_id', ->
    beforeEach ->
      spyOn window, 'update_schematics'
      MathJax.Hub.getAllJax.and.returnValue [@stubbedJax]
      @problem = new Problem($('.xblock-student_view'))
      $(@).html readFixtures('problem_content_1240.html')

    it 'bind the check button', ->
      expect($('div.action button.check')).toHandleWith 'click', @problem.check_fd

    it 'bind the show button', ->
      expect($('div.action button.show')).toHandleWith 'click', @problem.show

  describe 'renderProgressState', ->
    beforeEach ->
      @problem = new Problem($('.xblock-student_view'))
      #@renderProgressState = @problem.renderProgressState

    describe 'with a status of "none"', ->
      it 'reports the number of points possible', ->
        @problem.el.data('progress_status', 'none')
        @problem.el.data('progress_detail', '0/1')
        @problem.renderProgressState()
        expect(@problem.$('.problem-progress').html()).toEqual "(1 point possible)"

      it 'displays the number of points possible when rendering happens with the content', ->
        @problem.el.data('progress_status', 'none')
        @problem.el.data('progress_detail', '0/2')
        expect(@problem.$('.problem-progress').html()).toEqual ""
        @problem.render(problem_content_default)
        expect(@problem.$('.problem-progress').html()).toEqual "(2 points possible)"

    describe 'with any other valid status', ->
      it 'reports the current score', ->
        @problem.el.data('progress_status', 'foo')
        @problem.el.data('progress_detail', '1/1')
        @problem.renderProgressState()
        expect(@problem.$('.problem-progress').html()).toEqual "(1/1 point)"

      it 'shows current score when rendering happens with the content', ->
        @problem.el.data('progress_status', 'test status')
        @problem.el.data('progress_detail', '2/2')
        expect(@problem.$('.problem-progress').html()).toEqual ""
        @problem.render(problem_content_default)
        expect(@problem.$('.problem-progress').html()).toEqual "(2/2 points)"

  describe 'render', ->
    beforeEach ->
      @problem = new Problem($('.xblock-student_view'))
      @bind = @problem.bind
      spyOn @problem, 'bind'

    describe 'with content given', ->
      beforeEach ->
        @problem.render 'Hello World'

      it 'render the content', ->
        expect(@problem.el.html()).toEqual 'Hello World'

      it 're-bind the content', ->
        expect(@problem.bind).toHaveBeenCalled()

    describe 'with no content given', ->
      beforeEach ->
        spyOn($, 'postWithPrefix').and.callFake (url, callback) ->
          callback html: "Hello World"
        @problem.render()

      it 'load the content via ajax', ->
        expect(@problem.el.html()).toEqual 'Hello World'

      it 're-bind the content', ->
        expect(@problem.bind).toHaveBeenCalled()

  describe 'check_fd', ->
    beforeEach ->
      # Insert an input of type file outside of the problem.
      $('.xblock-student_view').after('<input type="file" />')
      @problem = new Problem($('.xblock-student_view'))
      spyOn(@problem, 'check')

    it 'check method is called if input of type file is not in problem', ->
      @problem.check_fd()
      expect(@problem.check).toHaveBeenCalled()

  describe 'check', ->
    beforeEach ->
      @problem = new Problem($('.xblock-student_view'))
      @problem.answers = 'foo=1&bar=2'

    it 'log the problem_check event', ->
      spyOn($, 'postWithPrefix').and.callFake (url, answers, callback) ->
        promise =
          always: (callable) -> callable()
          done: (callable) -> callable()
      @problem.check()
      expect(Logger.log).toHaveBeenCalledWith 'problem_check', 'foo=1&bar=2'

    it 'log the problem_graded event, after the problem is done grading.', ->
      spyOn($, 'postWithPrefix').and.callFake (url, answers, callback) ->
        response =
          success: 'correct'
          contents: 'mock grader response'
        callback(response)
        promise =
          always: (callable) -> callable()
          done: (callable) -> callable()
      @problem.check()
      expect(Logger.log).toHaveBeenCalledWith 'problem_graded', ['foo=1&bar=2', 'mock grader response'], @problem.id

    it 'submit the answer for check', ->
      spyOn($, 'postWithPrefix').and.callFake (url, answers, callback) ->
        promise =
          always: (callable) -> callable()
          done: (callable) -> callable()
      @problem.check()
      expect($.postWithPrefix).toHaveBeenCalledWith '/problem/Problem1/problem_check',
          'foo=1&bar=2', jasmine.any(Function)

    describe 'when the response is correct', ->
      it 'call render with returned content', ->
        spyOn($, 'postWithPrefix').and.callFake (url, answers, callback) ->
          callback(success: 'correct', contents: 'Correct')
          promise =
            always: (callable) -> callable()
            done: (callable) -> callable()
        @problem.check()
        expect(@problem.el.html()).toEqual 'Correct'
        expect(window.SR.readElts).toHaveBeenCalled()

    describe 'when the response is incorrect', ->
      it 'call render with returned content', ->
        spyOn($, 'postWithPrefix').and.callFake (url, answers, callback) ->
          callback(success: 'incorrect', contents: 'Incorrect')
          promise =
            always: (callable) -> callable()
            done: (callable) -> callable()
        @problem.check()
        expect(@problem.el.html()).toEqual 'Incorrect'
        expect(window.SR.readElts).toHaveBeenCalled()

    it 'tests if all the capa buttons are disabled while checking', (done)->
      deferred = $.Deferred()
      self = this

      runs = ->
        spyOn($, 'postWithPrefix').and.callFake (url, answers, callback) ->
          promise = undefined
          callback
            success: 'incorrect'
            contents: 'Incorrect'
          promise =
            always: (callable) ->
              callable()
            done: (callable) ->
              callable()
        spyOn @problem, 'enableAllButtons'
        @problem.check()
        expect(@problem.enableAllButtons).toHaveBeenCalledWith false, true
        if jQuery.active == 0
          deferred.resolve()
        deferred.promise()

      runs.call(self).then(->
        expect(self.problem.enableAllButtons).toHaveBeenCalledWith true, true
        return
      ).always done

    it 'tests the expected change in text of check button', (done) ->
      deferred = $.Deferred()
      self = this

      runs = ->
        spyOn($, 'postWithPrefix').and.callFake (url, answers, callback) ->
          promise = undefined
          promise =
            always: (callable) ->
              callable()
            done: (callable) ->
              callable()
        spyOn @problem.checkButtonLabel, 'text'
        @problem.check()
        expect(@problem.checkButtonLabel.text).toHaveBeenCalledWith 'Checking...'
        if jQuery.active == 0
          deferred.resolve()
        deferred.promise()

      runs.call(self).then(->
        expect(self.problem.checkButtonLabel.text).toHaveBeenCalledWith 'Check'
        return
      ).always done

  describe 'check button on problems', ->
    beforeEach ->
      @problem = new Problem($('.xblock-student_view'))
      @checkDisabled = (v) -> expect(@problem.checkButton.hasClass('is-disabled')).toBe(v)

    describe 'some basic tests for check button', ->
      it 'should become enabled after a value is entered into the text box', ->
        $('#input_example_1').val('test').trigger('input')
        @checkDisabled false
        $('#input_example_1').val('').trigger('input')
        @checkDisabled true

    describe 'some advanced tests for check button', ->
      it 'should become enabled after a checkbox is checked', ->
        html = '''
        <div class="choicegroup">
        <label for="input_1_1_1"><input type="checkbox" name="input_1_1" id="input_1_1_1" value="1"> One</label>
        <label for="input_1_1_2"><input type="checkbox" name="input_1_1" id="input_1_1_2" value="2"> Two</label>
        <label for="input_1_1_3"><input type="checkbox" name="input_1_1" id="input_1_1_3" value="3"> Three</label>
        </div>
        '''
        $('#input_example_1').replaceWith(html)
        @problem.checkAnswersAndCheckButton true
        @checkDisabled true
        $('#input_1_1_1').click()
        @checkDisabled false
        $('#input_1_1_1').click()
        @checkDisabled true

      it 'should become enabled after a radiobutton is checked', ->
        html = '''
        <div class="choicegroup">
        <label for="input_1_1_1"><input type="radio" name="input_1_1" id="input_1_1_1" value="1"> One</label>
        <label for="input_1_1_2"><input type="radio" name="input_1_1" id="input_1_1_2" value="2"> Two</label>
        <label for="input_1_1_3"><input type="radio" name="input_1_1" id="input_1_1_3" value="3"> Three</label>
        </div>
        '''
        $('#input_example_1').replaceWith(html)
        @problem.checkAnswersAndCheckButton true
        @checkDisabled true
        $('#input_1_1_1').attr('checked', true).trigger('click')
        @checkDisabled false
        $('#input_1_1_1').attr('checked', false).trigger('click')
        @checkDisabled true

      it 'should become enabled after a value is selected in a selector', ->
        html = '''
        <div id="problem_sel">
        <select>
        <option value="val0"></option>
        <option value="val1">1</option>
        <option value="val2">2</option>
        </select>
        </div>
        '''
        $('#input_example_1').replaceWith(html)
        @problem.checkAnswersAndCheckButton true
        @checkDisabled true
        $("#problem_sel select").val("val2").trigger('change')
        @checkDisabled false
        $("#problem_sel select").val("val0").trigger('change')
        @checkDisabled true

      it 'should become enabled after a radiobutton is checked and a value is entered into the text box', ->
        html = '''
        <div class="choicegroup">
        <label for="input_1_1_1"><input type="radio" name="input_1_1" id="input_1_1_1" value="1"> One</label>
        <label for="input_1_1_2"><input type="radio" name="input_1_1" id="input_1_1_2" value="2"> Two</label>
        <label for="input_1_1_3"><input type="radio" name="input_1_1" id="input_1_1_3" value="3"> Three</label>
        </div>
        '''
        $(html).insertAfter('#input_example_1')
        @problem.checkAnswersAndCheckButton true
        @checkDisabled true
        $('#input_1_1_1').attr('checked', true).trigger('click')
        @checkDisabled true
        $('#input_example_1').val('111').trigger('input')
        @checkDisabled false
        $('#input_1_1_1').attr('checked', false).trigger('click')
        @checkDisabled true

      it 'should become enabled if there are only hidden input fields', ->
        html = '''
        <input type="text" name="test" id="test" aria-describedby="answer_test" value="" style="display:none;">
        '''
        $('#input_example_1').replaceWith(html)
        @problem.checkAnswersAndCheckButton true
        @checkDisabled false

  describe 'reset', ->
    beforeEach ->
      @problem = new Problem($('.xblock-student_view'))

    it 'log the problem_reset event', ->
      spyOn($, 'postWithPrefix').and.callFake (url, answers, callback) ->
        promise =
          always: (callable) -> callable()
      @problem.answers = 'foo=1&bar=2'
      @problem.reset()
      expect(Logger.log).toHaveBeenCalledWith 'problem_reset', 'foo=1&bar=2'

    it 'POST to the problem reset page', ->
      spyOn($, 'postWithPrefix').and.callFake (url, answers, callback) ->
        promise =
          always: (callable) -> callable()
      @problem.reset()
      expect($.postWithPrefix).toHaveBeenCalledWith '/problem/Problem1/problem_reset',
          { id: 'i4x://edX/101/problem/Problem1' }, jasmine.any(Function)

    it 'render the returned content', ->
      spyOn($, 'postWithPrefix').and.callFake (url, answers, callback) ->
        callback html: "Reset"
        promise =
            always: (callable) -> callable()
      @problem.reset()
      expect(@problem.el.html()).toEqual 'Reset'

    it 'tests if all the buttons are disabled and the text of check button remains same while resetting', (done) ->
      deferred = $.Deferred()
      self = this

      runs = ->
        spyOn($, 'postWithPrefix').and.callFake (url, answers, callback) ->
          promise = undefined
          promise = always: (callable) ->
            callable()
        spyOn @problem, 'enableAllButtons'
        @problem.reset()
        expect(@problem.enableAllButtons).toHaveBeenCalledWith false, false
        expect(@problem.checkButtonLabel).toHaveText 'Check'
        if jQuery.active == 0
          deferred.resolve()
        deferred.promise()

      runs.call(self).then(->
        expect(self.problem.enableAllButtons).toHaveBeenCalledWith true, false
        expect(self.problem.checkButtonLabel).toHaveText 'Check'
      ).always done

  describe 'show', ->
    beforeEach ->
      @problem = new Problem($('.xblock-student_view'))
      @problem.el.prepend '<div id="answer_1_1" /><div id="answer_1_2" />'

    describe 'when the answer has not yet shown', ->
      beforeEach ->
        @problem.el.removeClass 'showed'

      it 'log the problem_show event', ->
        @problem.show()
        expect(Logger.log).toHaveBeenCalledWith 'problem_show',
            problem: 'i4x://edX/101/problem/Problem1'

      it 'fetch the answers', ->
        spyOn $, 'postWithPrefix'
        @problem.show()
        expect($.postWithPrefix).toHaveBeenCalledWith '/problem/Problem1/problem_show',
            jasmine.any(Function)

      it 'show the answers', ->
        spyOn($, 'postWithPrefix').and.callFake (url, callback) ->
          callback answers: '1_1': 'One', '1_2': 'Two'
        @problem.show()
        expect($('#answer_1_1')).toHaveHtml 'One'
        expect($('#answer_1_2')).toHaveHtml 'Two'

      it 'toggle the show answer button', ->
        spyOn($, 'postWithPrefix').and.callFake (url, callback) -> callback(answers: {})
        @problem.show()
        expect($('.show .show-label')).toHaveText 'Hide Answer'
        expect(window.SR.readElts).toHaveBeenCalled()

      it 'toggle the show answer button, answers are strings', ->
        spyOn($, 'postWithPrefix').and.callFake (url, callback) -> callback(answers: '1_1': 'One', '1_2': 'Two')
        @problem.show()
        expect($('.show .show-label')).toHaveText 'Hide Answer'
        expect(window.SR.readElts).toHaveBeenCalledWith ['<p>Answer: One</p>', '<p>Answer: Two</p>']

      it 'toggle the show answer button, answers are elements', ->
        answer1 = '<div><span class="detailed-solution">one</span></div>'
        answer2 = '<div><span class="detailed-solution">two</span></div>'
        spyOn($, 'postWithPrefix').and.callFake (url, callback) -> callback(answers: '1_1': answer1, '1_2': answer2)
        @problem.show()
        expect($('.show .show-label')).toHaveText 'Hide Answer'
        expect(window.SR.readElts).toHaveBeenCalledWith [jasmine.any(jQuery), jasmine.any(jQuery)]

      it 'add the showed class to element', ->
        spyOn($, 'postWithPrefix').and.callFake (url, callback) -> callback(answers: {})
        @problem.show()
        expect(@problem.el).toHaveClass 'showed'

      it 'reads the answers', (done) ->
        deferred = $.Deferred()

        runs = ->
          spyOn($, 'postWithPrefix').and.callFake (url, callback) ->
            callback answers:
              '1_1': 'answers'
          @problem.show()
          if jQuery.active == 0
            deferred.resolve()
          deferred.promise()

        runs.call(this).then(->
          expect(window.SR.readElts).toHaveBeenCalled()
          return
        ).always done

      describe 'multiple choice question', ->
        beforeEach ->
          @problem.el.prepend '''
            <label for="input_1_1_1"><input type="checkbox" name="input_1_1" id="input_1_1_1" value="1"> One</label>
            <label for="input_1_1_2"><input type="checkbox" name="input_1_1" id="input_1_1_2" value="2"> Two</label>
            <label for="input_1_1_3"><input type="checkbox" name="input_1_1" id="input_1_1_3" value="3"> Three</label>
            <label for="input_1_2_1"><input type="radio" name="input_1_2" id="input_1_2_1" value="1"> Other</label>
          '''

        it 'set the correct_answer attribute on the choice', ->
          spyOn($, 'postWithPrefix').and.callFake (url, callback) ->
            callback answers: '1_1': [2, 3]
          @problem.show()
          expect($('label[for="input_1_1_1"]')).not.toHaveAttr 'correct_answer', 'true'
          expect($('label[for="input_1_1_2"]')).toHaveAttr 'correct_answer', 'true'
          expect($('label[for="input_1_1_3"]')).toHaveAttr 'correct_answer', 'true'
          expect($('label[for="input_1_2_1"]')).not.toHaveAttr 'correct_answer', 'true'

      describe 'radio text question', ->
        radio_text_xml='''
<section class="problem">
  <div><p></p><span><section id="choicetextinput_1_2_1" class="choicetextinput">

<form class="choicetextgroup capa_inputtype" id="inputtype_1_2_1">
  <div class="indicator-container">
    <span class="unanswered" style="display:inline-block;" id="status_1_2_1"></span>
  </div>
  <fieldset>
    <section id="forinput1_2_1_choiceinput_0bc">
      <input class="ctinput" type="radio" name="choiceinput_1_2_1" id="1_2_1_choiceinput_0bc" value="choiceinput_0"">
      <input class="ctinput" type="text" name="choiceinput_0_textinput_0" id="1_2_1_choiceinput_0_textinput_0" value=" ">
      <p id="answer_1_2_1_choiceinput_0bc" class="answer"></p>
    </>
    <section id="forinput1_2_1_choiceinput_1bc">
      <input class="ctinput" type="radio" name="choiceinput_1_2_1" id="1_2_1_choiceinput_1bc" value="choiceinput_1" >
      <input class="ctinput" type="text" name="choiceinput_1_textinput_0" id="1_2_1_choiceinput_1_textinput_0" value=" " >
      <p id="answer_1_2_1_choiceinput_1bc" class="answer"></p>
    </section>
    <section id="forinput1_2_1_choiceinput_2bc">
      <input class="ctinput" type="radio" name="choiceinput_1_2_1" id="1_2_1_choiceinput_2bc" value="choiceinput_2" >
      <input class="ctinput" type="text" name="choiceinput_2_textinput_0" id="1_2_1_choiceinput_2_textinput_0" value=" " >
      <p id="answer_1_2_1_choiceinput_2bc" class="answer"></p>
    </section></fieldset><input class="choicetextvalue" type="hidden" name="input_1_2_1" id="input_1_2_1"></form>
</section></span></div>
</section>
'''
        beforeEach ->
          # Append a radiotextresponse problem to the problem, so we can check it's javascript functionality
          @problem.el.prepend(radio_text_xml)

        it 'sets the correct class on the section for the correct choice', ->
          spyOn($, 'postWithPrefix').and.callFake (url, callback) ->
            callback answers: "1_2_1": ["1_2_1_choiceinput_0bc"], "1_2_1_choiceinput_0bc": "3"
          @problem.show()

          expect($('#forinput1_2_1_choiceinput_0bc').attr('class')).toEqual(
            'choicetextgroup_show_correct')
          expect($('#answer_1_2_1_choiceinput_0bc').text()).toEqual('3')
          expect($('#answer_1_2_1_choiceinput_1bc').text()).toEqual('')
          expect($('#answer_1_2_1_choiceinput_2bc').text()).toEqual('')

        it 'Should not disable input fields', ->
          spyOn($, 'postWithPrefix').and.callFake (url, callback) ->
            callback answers: "1_2_1": ["1_2_1_choiceinput_0bc"], "1_2_1_choiceinput_0bc": "3"
          @problem.show()
          expect($('input#1_2_1_choiceinput_0bc').attr('disabled')).not.toEqual('disabled')
          expect($('input#1_2_1_choiceinput_1bc').attr('disabled')).not.toEqual('disabled')
          expect($('input#1_2_1_choiceinput_2bc').attr('disabled')).not.toEqual('disabled')
          expect($('input#1_2_1').attr('disabled')).not.toEqual('disabled')

      describe 'imageinput', ->
        imageinput_html = readFixtures('imageinput.underscore')

        DEFAULTS =
          id: '12345'
          width: '300'
          height: '400'

        beforeEach ->
          @problem = new Problem($('.xblock-student_view'))
          @problem.el.prepend _.template(imageinput_html)(DEFAULTS)

        assertAnswer = (problem, data) =>
          stubRequest(data)
          problem.show()

          $.each data['answers'], (id, answer) =>
            img = getImage(answer)
            el = $('#inputtype_' + id)
            expect(img).toImageDiffEqual(el.find('canvas')[0])

        stubRequest = (data) =>
          spyOn($, 'postWithPrefix').and.callFake (url, callback) ->
            callback data

        getImage = (coords, c_width, c_height) =>
          types =
            rectangle: (coords) =>
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

            regions: (coords) =>
              parseCoords = (coords) =>
                reg = JSON.parse(coords)

                if typeof reg[0][0][0] == "undefined"
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

          canvas = document.createElement('canvas')
          canvas.width = c_width or 100
          canvas.height = c_height or 100

          if canvas.getContext
            ctx = canvas.getContext('2d')
          else
            return console.log 'Canvas is not supported.'

          ctx.fillStyle = 'rgba(255,255,255,.3)';
          ctx.strokeStyle = "#FF0000";
          ctx.lineWidth = "2";

          $.each coords, (key, value) =>
            types[key](value) if types[key]? and value

          return canvas

        it 'rectangle is drawn correctly', ->
          assertAnswer(@problem, {
            'answers':
              '12345':
                'rectangle': '(10,10)-(30,30)',
                'regions': null
          })

        it 'region is drawn correctly', ->
          assertAnswer(@problem, {
            'answers':
              '12345':
                'rectangle': null,
                'regions': '[[10,10],[30,30],[70,30],[20,30]]'
          })

        it 'mixed shapes are drawn correctly', ->
          assertAnswer(@problem, {
            'answers':'12345':
              'rectangle': '(10,10)-(30,30);(5,5)-(20,20)',
              'regions': '''[
                [[50,50],[40,40],[70,30],[50,70]],
                [[90,95],[95,95],[90,70],[70,70]]
              ]'''
          })

        it 'multiple image inputs draw answers on separate canvases', ->
          data =
            id: '67890'
            width: '400'
            height: '300'

          @problem.el.prepend _.template(imageinput_html)(data)
          assertAnswer(@problem, {
            'answers':
              '12345':
                'rectangle': null,
                'regions': '[[10,10],[30,30],[70,30],[20,30]]'
              '67890':
                'rectangle': '(10,10)-(30,30)',
                'regions': null
          })

        it 'dictionary with answers doesn\'t contain answer for current id', ->
          spyOn console, 'log'
          stubRequest({'answers':{}})
          @problem.show()
          el = $('#inputtype_12345')
          expect(el.find('canvas')).not.toExist()
          expect(console.log).toHaveBeenCalledWith('Answer is absent for image input with id=12345')

    describe 'when the answers are already shown', ->
      beforeEach ->
        @problem.el.addClass 'showed'
        @problem.el.prepend '''
          <label for="input_1_1_1" correct_answer="true">
            <input type="checkbox" name="input_1_1" id="input_1_1_1" value="1" />
            One
          </label>
        '''
        $('#answer_1_1').html('One')
        $('#answer_1_2').html('Two')

      it 'hide the answers', ->
        @problem.show()
        expect($('#answer_1_1')).toHaveHtml ''
        expect($('#answer_1_2')).toHaveHtml ''
        expect($('label[for="input_1_1_1"]')).not.toHaveAttr 'correct_answer'

      it 'toggle the show answer button', ->
        @problem.show()
        expect($('.show .show-label')).toHaveText 'Show Answer'

      it 'remove the showed class from element', ->
        @problem.show()
        expect(@problem.el).not.toHaveClass 'showed'

  describe 'save', ->
    beforeEach ->
      @problem = new Problem($('.xblock-student_view'))
      @problem.answers = 'foo=1&bar=2'

    it 'log the problem_save event', ->
      spyOn($, 'postWithPrefix').and.callFake (url, answers, callback) ->
        promise =
          always: (callable) -> callable()
      @problem.save()
      expect(Logger.log).toHaveBeenCalledWith 'problem_save', 'foo=1&bar=2'

    it 'POST to save problem', ->
      spyOn($, 'postWithPrefix').and.callFake (url, answers, callback) ->
        promise =
          always: (callable) -> callable()
      @problem.save()
      expect($.postWithPrefix).toHaveBeenCalledWith '/problem/Problem1/problem_save',
          'foo=1&bar=2', jasmine.any(Function)

    it 'reads the save message', (done) ->
      deferred = $.Deferred()

      runs = ->
        spyOn($, 'postWithPrefix').and.callFake (url, answers, callback) ->
          promise = undefined
          callback success: 'OK'
          promise = always: (callable) ->
            callable()
        @problem.save()
        if jQuery.active == 0
          deferred.resolve()
        deferred.promise()

      runs.call(this).then(->
        expect(window.SR.readElts).toHaveBeenCalled()
        return
      ).always done

    it 'tests if all the buttons are disabled and the text of check button does not change while saving.', (done) ->
      deferred = $.Deferred()
      self = this

      runs = ->
        spyOn($, 'postWithPrefix').and.callFake (url, answers, callback) ->
          promise = undefined
          callback success: 'OK'
          promise = always: (callable) ->
            callable()
        spyOn @problem, 'enableAllButtons'
        @problem.save()
        expect(@problem.enableAllButtons).toHaveBeenCalledWith false, false
        expect(@problem.checkButtonLabel).toHaveText 'Check'
        if jQuery.active == 0
          deferred.resolve()
        deferred.promise()

      runs.call(self).then(->
        expect(self.problem.enableAllButtons).toHaveBeenCalledWith true, false
        expect(self.problem.checkButtonLabel).toHaveText 'Check'
      ).always done

  describe 'refreshMath', ->
    beforeEach ->
      @problem = new Problem($('.xblock-student_view'))
      $('#input_example_1').val 'E=mc^2'
      @problem.refreshMath target: $('#input_example_1').get(0)

    it 'should queue the conversion and MathML element update', ->
      expect(MathJax.Hub.Queue).toHaveBeenCalledWith ['Text', @stubbedJax, 'E=mc^2'],
        [@problem.updateMathML, @stubbedJax, $('#input_example_1').get(0)]

  describe 'updateMathML', ->
    beforeEach ->
      @problem = new Problem($('.xblock-student_view'))
      @stubbedJax.root.toMathML.and.returnValue '<MathML>'

    describe 'when there is no exception', ->
      beforeEach ->
        @problem.updateMathML @stubbedJax, $('#input_example_1').get(0)

      it 'convert jax to MathML', ->
        expect($('#input_example_1_dynamath')).toHaveValue '<MathML>'

    describe 'when there is an exception', ->
      beforeEach ->
        error = new Error()
        error.restart = true
        @stubbedJax.root.toMathML.and.throwError error
        @problem.updateMathML @stubbedJax, $('#input_example_1').get(0)

      it 'should queue up the exception', ->
        expect(MathJax.Callback.After).toHaveBeenCalledWith [@problem.refreshMath, @stubbedJax], true

  describe 'refreshAnswers', ->
    beforeEach ->
      @problem = new Problem($('.xblock-student_view'))
      @problem.el.html '''
        <textarea class="CodeMirror" />
        <input id="input_1_1" name="input_1_1" class="schematic" value="one" />
        <input id="input_1_2" name="input_1_2" value="two" />
        <input id="input_bogus_3" name="input_bogus_3" value="three" />
        '''
      @stubSchematic = { update_value: jasmine.createSpy('schematic') }
      @stubCodeMirror = { save: jasmine.createSpy('CodeMirror') }
      $('input.schematic').get(0).schematic = @stubSchematic
      $('textarea.CodeMirror').get(0).CodeMirror = @stubCodeMirror

    it 'update each schematic', ->
      @problem.refreshAnswers()
      expect(@stubSchematic.update_value).toHaveBeenCalled()

    it 'update each code block', ->
      @problem.refreshAnswers()
      expect(@stubCodeMirror.save).toHaveBeenCalled()

  describe 'multiple JsInput in single problem', ->
    jsinput_html = readFixtures('jsinput_problem.html')

    beforeEach ->
      @problem = new Problem($('.xblock-student_view'))
      @problem.render(jsinput_html)

    it 'check_save_waitfor should return false', ->
      $(@problem.inputs[0]).data('waitfor', ->)
      expect(@problem.check_save_waitfor()).toEqual(false)

  describe 'Submitting an xqueue-graded problem', ->
    matlabinput_html = readFixtures('matlabinput_problem.html')

    beforeEach ->
      spyOn($, 'postWithPrefix').and.callFake (url, callback) ->
        callback html: matlabinput_html
      jasmine.clock().install()
      @problem = new Problem($('.xblock-student_view'))
      spyOn(@problem, 'poll').and.callThrough()
      @problem.render(matlabinput_html)

    afterEach ->
      jasmine.clock().uninstall()

    it 'check that we stop polling after a fixed amount of time', ->
      expect(@problem.poll).not.toHaveBeenCalled()
      jasmine.clock().tick(1)
      time_steps = [1000, 2000, 4000, 8000, 16000, 32000]
      num_calls = 1
      for time_step in time_steps
        do (time_step) =>
          jasmine.clock().tick(time_step)
          expect(@problem.poll.calls.count()).toEqual(num_calls)
          num_calls += 1

      # jump the next step and verify that we are not still continuing to poll
      jasmine.clock().tick(64000)
      expect(@problem.poll.calls.count()).toEqual(6)

      expect($('.capa_alert').text()).toEqual("The grading process is still running. Refresh the page to see updates.")
