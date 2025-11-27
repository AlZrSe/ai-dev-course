from django.test import TestCase
from django.conf import settings

class SettingsTest(TestCase):
    def test_todo_app_in_installed_apps(self):
        """Test that the todo app is in INSTALLED_APPS"""
        self.assertIn('todo', settings.INSTALLED_APPS)
    
    def test_login_url_setting(self):
        """Test that LOGIN_URL is properly configured"""
        self.assertEqual(settings.LOGIN_URL, '/admin/login/')