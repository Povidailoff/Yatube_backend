from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

pages = {
    '/about/author/': reverse('about:author'),
    '/about/tech/': reverse('about:tech'),
}


class StaticPagesURLTests(TestCase):
    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов about/."""

        for page in pages.keys():
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблонов для адресов about/."""

        for page in pages.keys():
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertTemplateUsed(response, page[1:-1] + '.html')


class StaticViewsTests(TestCase):
    def test_about_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени about:name, доступен."""
        for name in pages.values():
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_page_uses_correct_template(self):
        """При запросе к about:name
        применяется шаблон about/name.html."""
        for page, name in pages.items():
            with self.subTest(page=page):
                response = self.client.get(name)
                self.assertTemplateUsed(response, page[1:-1] + '.html')
