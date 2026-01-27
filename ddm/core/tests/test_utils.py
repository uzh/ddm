from django.core.exceptions import ValidationError
from django.template.exceptions import TemplateSyntaxError
from django.test import TestCase

from ddm.core.utils.user_content.template import preprocess_user_content, render_user_content
from ddm.core.utils.validators import validate_safe_regex, validate_regex_pattern


class TestPreprocessUserContent(TestCase):
    def test_replacement(self):
        content = ''
        self.assertEqual(preprocess_user_content(content), '')

        content = '&gt;'
        self.assertEqual(preprocess_user_content(content), '>')

        content = '&lt;'
        self.assertEqual(preprocess_user_content(content), '<')

        content = 'Some text and random&lt;symbol and random&gt;-symbol.'
        self.assertEqual(preprocess_user_content(content), 'Some text and random<symbol and random>-symbol.')


class TestRenderUserContent(TestCase):
    """
    Test ensures that unsafe tags and filters are not added by mistake and that the most important allowed tags and
    filters are available.
    """
    def test_include_tag_is_invalid(self):
        with self.assertRaises(TemplateSyntaxError):
            render_user_content('{% include "something.html" %}')

    def test_load_tag_is_invalid(self):
        with self.assertRaises(TemplateSyntaxError):
            render_user_content('{% load static %}')

    def test_debug_tag_is_invalid(self):
        with self.assertRaises(TemplateSyntaxError):
            render_user_content('{% debug %}')

    def test_csrf_token_tag_is_invalid(self):
        with self.assertRaises(TemplateSyntaxError):
            render_user_content('{% csrf_token %}')

    def test_extends_tag_is_invalid(self):
        with self.assertRaises(TemplateSyntaxError):
            render_user_content('{% extends "something.html" %}')

    def test_autoescape_tag_is_invalid(self):
        with self.assertRaises(TemplateSyntaxError):
            render_user_content('{% autoescape off %}')

    def test_url_tag_is_invalid(self):
        with self.assertRaises(TemplateSyntaxError):
            render_user_content('{% url "some url name" %}')

    def test_safe_filter_is_invalid(self):
        with self.assertRaises(TemplateSyntaxError):
            render_user_content('{{ "<script>function someFun() {}</script>"|safe }}')

    def test_safeseq_filter_is_invalid(self):
        with self.assertRaises(TemplateSyntaxError):
            context = {'some_list': [1, 2, 3]}
            render_user_content('{{ some_list|safeseq }}', context)

    def test_escapejs_filter_is_invalid(self):
        with self.assertRaises(TemplateSyntaxError):
            render_user_content('{{ "value"|escapejs }}')

    def test_if_tag_is_valid(self):
        self.assertEqual('first', render_user_content('{% if 1 < 2 %}first{% endif %}'))

    def test_for_tag_is_valid(self):
        context = {'some_list': [1, 2, 3]}
        self.assertEqual('123', render_user_content('{% for i in some_list %}{{i}}{% endfor %}', context))


class TestValidateRegexPattern(TestCase):
    """Tests for the validate_regex_pattern function."""

    def test_valid_patterns_pass(self):
        from ddm.core.utils.validators import validate_regex_pattern

        valid_patterns = [
            r'[a-z]+',
            r'\d{4}-\d{2}-\d{2}',
            r'.*\.json$',
            r'(foo|bar)',
            r'(\w+)',
            r'^start.*end$',
            r'file_\d+\.txt',
            '',  # Empty pattern should pass
            None,  # None should pass
        ]
        for pattern in valid_patterns:
            with self.subTest(pattern=pattern):
                validate_regex_pattern(pattern)  # Should not raise

    def test_invalid_syntax_raises_error(self):
        invalid_patterns = [
            r'[a-z',        # Unclosed bracket
            r'(foo',        # Unclosed parenthesis
            r'*invalid',    # Quantifier without target
            r'(?P<name',    # Incomplete group
        ]
        for pattern in invalid_patterns:
            with self.subTest(pattern=pattern):
                with self.assertRaises(ValidationError):
                    validate_regex_pattern(pattern)


class TestValidateSafeRegex(TestCase):
    """Tests for the validate_safe_regex function that blocks dangerous patterns."""

    def test_valid_safe_patterns_pass(self):
        safe_patterns = [
            r'[a-z]+',
            r'\d{4}-\d{2}-\d{2}',
            r'.*\.json$',
            r'(foo|bar)',
            r'(\w+)',
            r'^start.*end$',
            r'file_\d+\.txt',
            r'[^/]+/data\.json',
            '',
            None,
        ]
        for pattern in safe_patterns:
            with self.subTest(pattern=pattern):
                validate_safe_regex(pattern)  # Should not raise

    def test_nested_quantifiers_blocked(self):
        dangerous_patterns = [
            r'(a+)+',
            r'(a*)*',
            r'(a+)*',
            r'(a*)+',
            r'(.*)+',
            r'(\d+)+',
            r'([a-z]+)+',
            r'(foo+)+',
        ]
        for pattern in dangerous_patterns:
            with self.subTest(pattern=pattern):
                with self.assertRaises(ValidationError) as ctx:
                    validate_safe_regex(pattern)
                self.assertIn('quantifier', str(ctx.exception).lower())

    def test_adjacent_wildcards_blocked(self):
        dangerous_patterns = [
            r'.*.*',
            r'.+.+',
            r'.*.+',
            r'.+.*',
        ]
        for pattern in dangerous_patterns:
            with self.subTest(pattern=pattern):
                with self.assertRaises(ValidationError) as ctx:
                    validate_safe_regex(pattern)
                self.assertIn('wildcard', str(ctx.exception).lower())

    def test_quantified_backreferences_blocked(self):
        dangerous_patterns = [
            r'(.+)\1+',
            r'(.+)\1*',
            r'(.*)\1+',
        ]
        for pattern in dangerous_patterns:
            with self.subTest(pattern=pattern):
                with self.assertRaises(ValidationError) as ctx:
                    validate_safe_regex(pattern)
                self.assertIn('backreference', str(ctx.exception).lower())

    def test_invalid_syntax_still_caught(self):
        """Syntax errors should be caught before dangerous pattern check."""
        with self.assertRaises(ValidationError) as ctx:
            validate_safe_regex(r'[unclosed')
        self.assertIn('invalid', str(ctx.exception).lower())
