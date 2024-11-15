from django.template.exceptions import TemplateSyntaxError
from django.test import TestCase

from ddm.core.utils.user_content.template import preprocess_user_content, render_user_content


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
