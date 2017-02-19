"""
Bok choy acceptance and a11y tests for problem types in the LMS

See also lettuce tests in lms/djangoapps/courseware/features/problems.feature
"""
import random
import textwrap

from nose import SkipTest
from abc import ABCMeta, abstractmethod
from nose.plugins.attrib import attr
from selenium.webdriver import ActionChains

from capa.tests.response_xml_factory import (
    AnnotationResponseXMLFactory,
    ChoiceResponseXMLFactory,
    ChoiceTextResponseXMLFactory,
    CodeResponseXMLFactory,
    CustomResponseXMLFactory,
    FormulaResponseXMLFactory,
    ImageResponseXMLFactory,
    MultipleChoiceResponseXMLFactory,
    NumericalResponseXMLFactory,
    OptionResponseXMLFactory,
    StringResponseXMLFactory,
    SymbolicResponseXMLFactory,
)

from common.test.acceptance.fixtures.course import XBlockFixtureDesc
from common.test.acceptance.pages.lms.problem import ProblemPage
from common.test.acceptance.tests.helpers import select_option_by_text
from common.test.acceptance.tests.lms.test_lms_problems import ProblemsTest
from common.test.acceptance.tests.helpers import EventsTestMixin


class ProblemTypeTestBaseMeta(ABCMeta):
    """
    MetaClass for ProblemTypeTestBase to ensure that the required attributes
    are defined in the inheriting classes.
    """
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)

        required_attrs = [
            'problem_name',
            'problem_type',
            'factory',
            'factory_kwargs',
            'status_indicators',
        ]

        for required_attr in required_attrs:
            msg = ('{} is a required attribute for {}').format(
                required_attr, str(cls)
            )

            try:
                if obj.__getattribute__(required_attr) is None:
                    raise NotImplementedError(msg)
            except AttributeError:
                raise NotImplementedError(msg)

        return obj


class ProblemTypeTestBase(ProblemsTest, EventsTestMixin):
    """
    Base class for testing assesment problem types in bok choy.

    This inherits from ProblemsTest, which has capabilities for testing problem
    features that are not problem type specific (checking, hinting, etc.).

    The following attributes must be explicitly defined when inheriting from
    this class:
        problem_name (str)
        problem_type (str)
        factory (ResponseXMLFactory subclass instance)

    Additionally, the default values for factory_kwargs and status_indicators
    may need to be overridden for some problem types.
    """
    __metaclass__ = ProblemTypeTestBaseMeta

    problem_name = None
    problem_type = None
    factory = None
    factory_kwargs = {}
    status_indicators = {
        'correct': ['span.correct'],
        'incorrect': ['span.incorrect'],
        'unanswered': ['span.unanswered'],
    }

    def setUp(self):
        """
        Visits courseware_page and defines self.problem_page.
        """
        super(ProblemTypeTestBase, self).setUp()
        self.courseware_page.visit()
        self.problem_page = ProblemPage(self.browser)

    def get_problem(self):
        """
        Creates a {problem_type} problem
        """
        # Generate the problem XML using capa.tests.response_xml_factory
        return XBlockFixtureDesc(
            'problem',
            self.problem_name,
            data=self.factory.build_xml(**self.factory_kwargs),
            metadata={'rerandomize': 'always'}
        )

    def wait_for_status(self, status):
        """
        Waits for the expected status indicator.

        Args:
            status: one of ("correct", "incorrect", "unanswered)
        """
        msg = "Wait for status to be {}".format(status)
        selector = ', '.join(self.status_indicators[status])
        self.problem_page.wait_for_element_visibility(selector, msg)

    @abstractmethod
    def answer_problem(self, correct):
        """
        Args:
            `correct` (bool): Inputs correct answer if True, else inputs
                incorrect answer.
        """
        raise NotImplementedError()


class ProblemTypeTestMixin(object):
    """
    Test cases shared amongst problem types.
    """
    can_submit_blank = False

    @attr('shard_7')
    def test_answer_correctly(self):
        """
        Scenario: I can answer a problem correctly
        Given External graders respond "correct"
        And I am viewing a "<ProblemType>" problem
        When I answer a "<ProblemType>" problem "correctly"
        Then my "<ProblemType>" answer is marked "correct"
        And The "<ProblemType>" problem displays a "correct" answer
        And a "problem_check" server event is emitted
        And a "problem_check" browser event is emitted
        """
        # Make sure we're looking at the right problem
        self.assertEqual(self.problem_page.problem_name, self.problem_name)

        # Answer the problem correctly
        self.answer_problem(correct=True)
        self.problem_page.click_check()
        self.wait_for_status('correct')

        # Check for corresponding tracking event
        expected_events = [
            {
                'event_source': 'server',
                'event_type': 'problem_check',
                'username': self.username,
            }, {
                'event_source': 'browser',
                'event_type': 'problem_check',
                'username': self.username,
            },
        ]

        for event in expected_events:
            self.wait_for_events(event_filter=event, number_of_matches=1)

    @attr('shard_7')
    def test_answer_incorrectly(self):
        """
        Scenario: I can answer a problem incorrectly
        Given External graders respond "incorrect"
        And I am viewing a "<ProblemType>" problem
        When I answer a "<ProblemType>" problem "incorrectly"
        Then my "<ProblemType>" answer is marked "incorrect"
        And The "<ProblemType>" problem displays a "incorrect" answer
        """
        self.problem_page.wait_for(
            lambda: self.problem_page.problem_name == self.problem_name,
            "Make sure the correct problem is on the page"
        )

        # Answer the problem incorrectly
        self.answer_problem(correct=False)
        self.problem_page.click_check()
        self.wait_for_status('incorrect')

    @attr('shard_7')
    def test_submit_blank_answer(self):
        """
        Scenario: I can submit a blank answer
        Given I am viewing a "<ProblemType>" problem
        When I check a problem
        Then my "<ProblemType>" answer is marked "incorrect"
        And The "<ProblemType>" problem displays a "blank" answer
        """
        if not self.can_submit_blank:
            raise SkipTest("Test incompatible with the current problem type")

        self.problem_page.wait_for(
            lambda: self.problem_page.problem_name == self.problem_name,
            "Make sure the correct problem is on the page"
        )
        # Leave the problem unchanged and click check.
        self.assertNotIn('is-disabled', self.problem_page.q(css='div.problem button.check').attrs('class')[0])
        self.problem_page.click_check()
        self.wait_for_status('incorrect')

    @attr('shard_7')
    def test_cant_submit_blank_answer(self):
        """
        Scenario: I can't submit a blank answer
        When I try to submit blank answer
        Then I can't check a problem
        """
        if self.can_submit_blank:
            raise SkipTest("Test incompatible with the current problem type")

        self.problem_page.wait_for(
            lambda: self.problem_page.problem_name == self.problem_name,
            "Make sure the correct problem is on the page"
        )
        self.assertIn('is-disabled', self.problem_page.q(css='div.problem button.check').attrs('class')[0])

    @attr('a11y')
    def test_problem_type_a11y(self):
        """
        Run accessibility audit for the problem type.
        """
        self.problem_page.wait_for(
            lambda: self.problem_page.problem_name == self.problem_name,
            "Make sure the correct problem is on the page"
        )

        # Set the scope to the problem container
        self.problem_page.a11y_audit.config.set_scope(
            include=['div#seq_content'])

        self.problem_page.a11y_audit.config.set_rules({
            "ignore": [
                'aria-allowed-attr',  # TODO: AC-491
                'aria-valid-attr',  # TODO: AC-491
                'aria-roles',  # TODO: AC-491
                'checkboxgroup',  # TODO: AC-491
                'radiogroup',  # TODO: AC-491
                'color-contrast',  # TODO: AC-491
                'section',  # TODO: AC-491
                'label',  # TODO: AC-491
            ]
        })

        # Run the accessibility audit.
        self.problem_page.a11y_audit.check_for_accessibility_errors()


class AnnotationProblemTypeTest(ProblemTypeTestBase, ProblemTypeTestMixin):
    """
    TestCase Class for Annotation Problem Type
    """
    problem_name = 'ANNOTATION TEST PROBLEM'
    problem_type = 'annotationresponse'

    factory = AnnotationResponseXMLFactory()

    can_submit_blank = True

    factory_kwargs = {
        'title': 'Annotation Problem',
        'text': 'The text being annotated',
        'comment': 'What do you think the about this text?',
        'comment_prompt': 'Type your answer below.',
        'tag_prompt': 'Which of these items most applies to the text?',
        'options': [
            ('dog', 'correct'),
            ('cat', 'incorrect'),
            ('fish', 'partially-correct'),
        ]
    }

    status_indicators = {
        'correct': ['span.correct'],
        'incorrect': ['span.incorrect'],
        'partially-correct': ['span.partially-correct'],
        'unanswered': ['span.unanswered'],
    }

    def setUp(self, *args, **kwargs):
        """
        Additional setup for AnnotationProblemTypeTest
        """
        super(AnnotationProblemTypeTest, self).setUp(*args, **kwargs)

    def answer_problem(self, correct):
        """
        Answer annotation problem.
        """
        choice = 0 if correct else 1
        answer = 'Student comment'

        self.problem_page.q(css='div.problem textarea.comment').fill(answer)
        self.problem_page.q(
            css='div.problem span.tag'.format(choice=choice)
        ).nth(choice).click()


class CheckboxProblemTypeTest(ProblemTypeTestBase, ProblemTypeTestMixin):
    """
    TestCase Class for Checkbox Problem Type
    """
    problem_name = 'CHECKBOX TEST PROBLEM'
    problem_type = 'checkbox'

    factory = ChoiceResponseXMLFactory()

    factory_kwargs = {
        'question_text': 'The correct answer is Choice 0 and Choice 2',
        'choice_type': 'checkbox',
        'choices': [True, False, True, False],
        'choice_names': ['Choice 0', 'Choice 1', 'Choice 2', 'Choice 3']
    }

    def setUp(self, *args, **kwargs):
        """
        Additional setup for CheckboxProblemTypeTest
        """
        super(CheckboxProblemTypeTest, self).setUp(*args, **kwargs)
        self.problem_page.a11y_audit.config.set_rules({
            'ignore': [
                'section',  # TODO: AC-491
                'aria-allowed-attr',  # TODO: AC-251
                'aria-valid-attr',  # TODO: AC-251
                'aria-roles',  # TODO: AC-251
                'checkboxgroup',  # TODO: AC-251
            ]
        })

    def answer_problem(self, correct):
        """
        Answer checkbox problem.
        """
        if correct:
            self.problem_page.click_choice("choice_0")
            self.problem_page.click_choice("choice_2")
        else:
            self.problem_page.click_choice("choice_1")


class MultipleChoiceProblemTypeTest(ProblemTypeTestBase, ProblemTypeTestMixin):
    """
    TestCase Class for Multiple Choice Problem Type
    """
    problem_name = 'MULTIPLE CHOICE TEST PROBLEM'
    problem_type = 'multiple choice'

    factory = MultipleChoiceResponseXMLFactory()

    factory_kwargs = {
        'question_text': 'The correct answer is Choice 2',
        'choices': [False, False, True, False],
        'choice_names': ['choice_0', 'choice_1', 'choice_2', 'choice_3'],
    }
    status_indicators = {
        'correct': ['label.choicegroup_correct'],
        'incorrect': ['label.choicegroup_incorrect', 'span.incorrect'],
        'unanswered': ['span.unanswered'],
    }

    def setUp(self, *args, **kwargs):
        """
        Additional setup for MultipleChoiceProblemTypeTest
        """
        super(MultipleChoiceProblemTypeTest, self).setUp(*args, **kwargs)
        self.problem_page.a11y_audit.config.set_rules({
            'ignore': [
                'section',  # TODO: AC-491
                'aria-valid-attr',  # TODO: AC-251
                'radiogroup',  # TODO: AC-251
            ]
        })

    def answer_problem(self, correct):
        """
        Answer multiple choice problem.
        """
        if correct:
            self.problem_page.click_choice("choice_choice_2")
        else:
            self.problem_page.click_choice("choice_choice_1")


class RadioProblemTypeTest(ProblemTypeTestBase, ProblemTypeTestMixin):
    """
    TestCase Class for Radio Problem Type
    """
    problem_name = 'RADIO TEST PROBLEM'
    problem_type = 'radio'

    factory = ChoiceResponseXMLFactory()

    factory_kwargs = {
        'question_text': 'The correct answer is Choice 2',
        'choice_type': 'radio',
        'choices': [False, False, True, False],
        'choice_names': ['Choice 0', 'Choice 1', 'Choice 2', 'Choice 3'],
    }
    status_indicators = {
        'correct': ['label.choicegroup_correct'],
        'incorrect': ['label.choicegroup_incorrect', 'span.incorrect'],
        'unanswered': ['span.unanswered'],
    }

    def setUp(self, *args, **kwargs):
        """
        Additional setup for RadioProblemTypeTest
        """
        super(RadioProblemTypeTest, self).setUp(*args, **kwargs)
        self.problem_page.a11y_audit.config.set_rules({
            'ignore': [
                'section',  # TODO: AC-491
                'aria-valid-attr',  # TODO: AC-292
                'radiogroup',  # TODO: AC-292
            ]
        })

    def answer_problem(self, correct):
        """
        Answer radio problem.
        """
        if correct:
            self.problem_page.click_choice("choice_2")
        else:
            self.problem_page.click_choice("choice_1")


class DropDownProblemTypeTest(ProblemTypeTestBase, ProblemTypeTestMixin):
    """
    TestCase Class for Drop Down Problem Type
    """
    problem_name = 'DROP DOWN TEST PROBLEM'
    problem_type = 'drop down'

    factory = OptionResponseXMLFactory()

    factory_kwargs = {
        'question_text': 'The correct answer is Option 2',
        'options': ['Option 1', 'Option 2', 'Option 3', 'Option 4'],
        'correct_option': 'Option 2'
    }

    def setUp(self, *args, **kwargs):
        """
        Additional setup for DropDownProblemTypeTest
        """
        super(DropDownProblemTypeTest, self).setUp(*args, **kwargs)
        self.problem_page.a11y_audit.config.set_rules({
            'ignore': [
                'section',  # TODO: AC-491
                'label',  # TODO: AC-291
            ]
        })

    def answer_problem(self, correct):
        """
        Answer drop down problem.
        """
        answer = 'Option 2' if correct else 'Option 3'
        selector_element = self.problem_page.q(
            css='.problem .option-input select')
        select_option_by_text(selector_element, answer)


class StringProblemTypeTest(ProblemTypeTestBase, ProblemTypeTestMixin):
    """
    TestCase Class for String Problem Type
    """
    problem_name = 'STRING TEST PROBLEM'
    problem_type = 'string'

    factory = StringResponseXMLFactory()

    factory_kwargs = {
        'question_text': 'The answer is "correct string"',
        'case_sensitive': False,
        'answer': 'correct string',
    }

    status_indicators = {
        'correct': ['div.correct'],
        'incorrect': ['div.incorrect'],
        'unanswered': ['div.unanswered', 'div.unsubmitted'],
    }

    def setUp(self, *args, **kwargs):
        """
        Additional setup for StringProblemTypeTest
        """
        super(StringProblemTypeTest, self).setUp(*args, **kwargs)
        self.problem_page.a11y_audit.config.set_rules({
            'ignore': [
                'section',  # TODO: AC-491
                'label',  # TODO: AC-290
            ]
        })

    def answer_problem(self, correct):
        """
        Answer string problem.
        """
        textvalue = 'correct string' if correct else 'incorrect string'
        self.problem_page.fill_answer(textvalue)


class NumericalProblemTypeTest(ProblemTypeTestBase, ProblemTypeTestMixin):
    """
    TestCase Class for Numerical Problem Type
    """
    problem_name = 'NUMERICAL TEST PROBLEM'
    problem_type = 'numerical'

    factory = NumericalResponseXMLFactory()

    factory_kwargs = {
        'question_text': 'The answer is pi + 1',
        'answer': '4.14159',
        'tolerance': '0.00001',
        'math_display': True,
    }

    status_indicators = {
        'correct': ['div.correct'],
        'incorrect': ['div.incorrect'],
        'unanswered': ['div.unanswered', 'div.unsubmitted'],
    }

    def setUp(self, *args, **kwargs):
        """
        Additional setup for NumericalProblemTypeTest
        """
        super(NumericalProblemTypeTest, self).setUp(*args, **kwargs)
        self.problem_page.a11y_audit.config.set_rules({
            'ignore': [
                'section',  # TODO: AC-491
                'label',  # TODO: AC-289
            ]
        })

    def answer_problem(self, correct):
        """
        Answer numerical problem.
        """
        textvalue = "pi + 1" if correct else str(random.randint(-2, 2))
        self.problem_page.fill_answer(textvalue)


class FormulaProblemTypeTest(ProblemTypeTestBase, ProblemTypeTestMixin):
    """
    TestCase Class for Formula Problem Type
    """
    problem_name = 'FORMULA TEST PROBLEM'
    problem_type = 'formula'

    factory = FormulaResponseXMLFactory()

    factory_kwargs = {
        'question_text': 'The solution is [mathjax]x^2+2x+y[/mathjax]',
        'sample_dict': {'x': (-100, 100), 'y': (-100, 100)},
        'num_samples': 10,
        'tolerance': 0.00001,
        'math_display': True,
        'answer': 'x^2+2*x+y',
    }

    status_indicators = {
        'correct': ['div.correct'],
        'incorrect': ['div.incorrect'],
        'unanswered': ['div.unanswered', 'div.unsubmitted'],
    }

    def setUp(self, *args, **kwargs):
        """
        Additional setup for FormulaProblemTypeTest
        """
        super(FormulaProblemTypeTest, self).setUp(*args, **kwargs)
        self.problem_page.a11y_audit.config.set_rules({
            'ignore': [
                'section',  # TODO: AC-491
                'label',  # TODO: AC-288
            ]
        })

    def answer_problem(self, correct):
        """
        Answer formula problem.
        """
        textvalue = "x^2+2*x+y" if correct else 'x^2'
        self.problem_page.fill_answer(textvalue)


class ScriptProblemTypeTest(ProblemTypeTestBase, ProblemTypeTestMixin):
    """
    TestCase Class for Script Problem Type
    """
    problem_name = 'SCRIPT TEST PROBLEM'
    problem_type = 'script'

    factory = CustomResponseXMLFactory()

    factory_kwargs = {
        'question_text': 'Enter two integers that sum to 10.',
        'cfn': 'test_add_to_ten',
        'expect': '10',
        'num_inputs': 2,
        'script': textwrap.dedent("""
            def test_add_to_ten(expect,ans):
                try:
                    a1=int(ans[0])
                    a2=int(ans[1])
                except ValueError:
                    a1=0
                    a2=0
                return (a1+a2)==int(expect)
        """),
    }
    status_indicators = {
        'correct': ['div.correct'],
        'incorrect': ['div.incorrect'],
        'unanswered': ['div.unanswered', 'div.unsubmitted'],
    }

    def setUp(self, *args, **kwargs):
        """
        Additional setup for ScriptProblemTypeTest
        """
        super(ScriptProblemTypeTest, self).setUp(*args, **kwargs)
        self.problem_page.a11y_audit.config.set_rules({
            'ignore': [
                'section',  # TODO: AC-491
                'label',  # TODO: AC-287
            ]
        })

    def answer_problem(self, correct):
        """
        Answer script problem.
        """
        # Correct answer is any two integers that sum to 10
        first_addend = random.randint(-100, 100)
        second_addend = 10 - first_addend

        # If we want an incorrect answer, then change
        # the second addend so they no longer sum to 10
        if not correct:
            second_addend += random.randint(1, 10)

        self.problem_page.fill_answer(first_addend, input_num=0)
        self.problem_page.fill_answer(second_addend, input_num=1)


class CodeProblemTypeTest(ProblemTypeTestBase, ProblemTypeTestMixin):
    """
    TestCase Class for Code Problem Type
    """
    problem_name = 'CODE TEST PROBLEM'
    problem_type = 'code'

    factory = CodeResponseXMLFactory()

    factory_kwargs = {
        'question_text': 'Submit code to an external grader',
        'initial_display': 'print "Hello world!"',
        'grader_payload': '{"grader": "ps1/Spring2013/test_grader.py"}',
    }

    status_indicators = {
        'correct': ['.grader-status .correct ~ .debug'],
        'incorrect': ['.grader-status .incorrect ~ .debug'],
        'unanswered': ['.grader-status .unanswered ~ .debug'],
    }

    def setUp(self, *args, **kwargs):
        """
        Additional setup for CodeProblemTypeTest
        """
        super(CodeProblemTypeTest, self).setUp(*args, **kwargs)
        self.problem_page.a11y_audit.config.set_rules({
            'ignore': [
                'section',  # TODO: AC-491
                'color-contrast',  # TODO: AC-286
                'label',  # TODO: AC-286
            ]
        })

    def answer_problem(self, correct):
        """
        Answer code problem.
        """
        # The fake xqueue server is configured to respond
        # correct / incorrect no matter what we submit.
        # Furthermore, since the inline code response uses
        # JavaScript to make the code display nicely, it's difficult
        # to programatically input text
        # (there's not <textarea> we can just fill text into)
        # For this reason, we submit the initial code in the response
        # (configured in the problem XML above)
        pass

    def test_answer_incorrectly(self):
        """
        Overridden for script test because the testing grader always responds
        with "correct"
        """
        pass

    def test_submit_blank_answer(self):
        """
        Overridden for script test because the testing grader always responds
        with "correct"
        """
        pass

    def test_cant_submit_blank_answer(self):
        """
        Overridden for script test because the testing grader always responds
        with "correct"
        """
        pass


class ChoiceTextProbelmTypeTestBase(ProblemTypeTestBase):
    """
    Base class for "Choice + Text" Problem Types.
    (e.g. RadioText, CheckboxText)
    """
    choice_type = None

    def _select_choice(self, input_num):
        """
        Selects the nth (where n == input_num) choice of the problem.
        """
        self.problem_page.q(
            css='div.problem input.ctinput[type="{}"]'.format(self.choice_type)
        ).nth(input_num).click()

    def _fill_input_text(self, value, input_num):
        """
        Fills the nth (where n == input_num) text input field of the problem
        with value.
        """
        self.problem_page.q(
            css='div.problem input.ctinput[type="text"]'
        ).nth(input_num).fill(value)

    def answer_problem(self, correct):
        """
        Answer radio text problem.
        """
        choice = 0 if correct else 1
        input_value = "8" if correct else "5"

        self._select_choice(choice)
        self._fill_input_text(input_value, choice)


class RadioTextProblemTypeTest(ChoiceTextProbelmTypeTestBase, ProblemTypeTestMixin):
    """
    TestCase Class for Radio Text Problem Type
    """
    problem_name = 'RADIO TEXT TEST PROBLEM'
    problem_type = 'radio_text'
    choice_type = 'radio'

    factory = ChoiceTextResponseXMLFactory()

    factory_kwargs = {
        'question_text': 'The correct answer is Choice 0 and input 8',
        'type': 'radiotextgroup',
        'choices': [
            ("true", {"answer": "8", "tolerance": "1"}),
            ("false", {"answer": "8", "tolerance": "1"}),
        ],
    }

    status_indicators = {
        'correct': ['section.choicetextgroup_correct'],
        'incorrect': ['section.choicetextgroup_incorrect', 'span.incorrect'],
        'unanswered': ['span.unanswered'],
    }

    def setUp(self, *args, **kwargs):
        """
        Additional setup for RadioTextProblemTypeTest
        """
        super(RadioTextProblemTypeTest, self).setUp(*args, **kwargs)
        self.problem_page.a11y_audit.config.set_rules({
            'ignore': [
                'section',  # TODO: AC-491
                'label',  # TODO: AC-285
                'radiogroup',  # TODO: AC-285
            ]
        })


class CheckboxTextProblemTypeTest(ChoiceTextProbelmTypeTestBase, ProblemTypeTestMixin):
    """
    TestCase Class for Checkbox Text Problem Type
    """
    problem_name = 'CHECKBOX TEXT TEST PROBLEM'
    problem_type = 'checkbox_text'
    choice_type = 'checkbox'

    factory = ChoiceTextResponseXMLFactory()

    factory_kwargs = {
        'question_text': 'The correct answer is Choice 0 and input 8',
        'type': 'checkboxtextgroup',
        'choices': [
            ("true", {"answer": "8", "tolerance": "1"}),
            ("false", {"answer": "8", "tolerance": "1"}),
        ],
    }

    def setUp(self, *args, **kwargs):
        """
        Additional setup for CheckboxTextProblemTypeTest
        """
        super(CheckboxTextProblemTypeTest, self).setUp(*args, **kwargs)
        self.problem_page.a11y_audit.config.set_rules({
            'ignore': [
                'section',  # TODO: AC-491
                'label',  # TODO: AC-284
                'checkboxgroup',  # TODO: AC-284
            ]
        })


class ImageProblemTypeTest(ProblemTypeTestBase, ProblemTypeTestMixin):
    """
    TestCase Class for Image Problem Type
    """
    problem_name = 'IMAGE TEST PROBLEM'
    problem_type = 'image'

    factory = ImageResponseXMLFactory()

    can_submit_blank = True

    factory_kwargs = {
        'src': '/static/images/placeholder-image.png',
        'rectangle': '(0,0)-(50,50)',
    }

    def answer_problem(self, correct):
        """
        Answer image problem.
        """
        offset = 25 if correct else -25
        input_selector = ".imageinput [id^='imageinput_'] img"
        input_element = self.problem_page.q(css=input_selector)[0]

        chain = ActionChains(self.browser)
        chain.move_to_element(input_element)
        chain.move_by_offset(offset, offset)
        chain.click()
        chain.perform()


class SymbolicProblemTypeTest(ProblemTypeTestBase, ProblemTypeTestMixin):
    """
    TestCase Class for Symbolic Problem Type
    """
    problem_name = 'SYMBOLIC TEST PROBLEM'
    problem_type = 'symbolicresponse'

    factory = SymbolicResponseXMLFactory()

    factory_kwargs = {
        'expect': '2*x+3*y',
    }

    status_indicators = {
        'correct': ['span div.correct'],
        'incorrect': ['span div.incorrect'],
        'unanswered': ['span div.unanswered'],
    }

    def setUp(self, *args, **kwargs):
        """
        Additional setup for SymbolicProblemTypeTest
        """
        super(SymbolicProblemTypeTest, self).setUp(*args, **kwargs)
        self.problem_page.a11y_audit.config.set_rules({
            'ignore': [
                'section',  # TODO: AC-491
                'label',  # TODO: AC-294
            ]
        })

    def answer_problem(self, correct):
        """
        Answer symbolic problem.
        """
        choice = "2*x+3*y" if correct else "3*a+4*b"
        self.problem_page.fill_answer(choice)
