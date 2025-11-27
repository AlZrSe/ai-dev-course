from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Todo

class TodoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.todo = Todo.objects.create(
            title='Test Todo',
            description='Test Description',
            completed=False,
            owner=self.user
        )

    def test_todo_creation(self):
        """Test that a todo can be created correctly"""
        self.assertEqual(self.todo.title, 'Test Todo')
        self.assertEqual(self.todo.description, 'Test Description')
        self.assertFalse(self.todo.completed)
        self.assertEqual(self.todo.owner, self.user)
        self.assertIsNotNone(self.todo.created_at)
        self.assertIsNotNone(self.todo.updated_at)

    def test_todo_str_representation(self):
        """Test that the todo string representation is correct"""
        self.assertEqual(str(self.todo), 'Test Todo')

    def test_todo_ordering(self):
        """Test that todos are ordered by creation date (newest first)"""
        todo2 = Todo.objects.create(
            title='Second Todo',
            owner=self.user
        )
        todos = Todo.objects.all()
        self.assertEqual(todos[0], todo2)  # Most recent first
        self.assertEqual(todos[1], self.todo)

    def test_todo_meta_verbose_name(self):
        """Test that the verbose names are set correctly"""
        self.assertEqual(Todo._meta.verbose_name, 'Todo')
        self.assertEqual(Todo._meta.verbose_name_plural, 'Todos')


class TodoViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.todo = Todo.objects.create(
            title='Test Todo',
            description='Test Description',
            completed=False,
            owner=self.user
        )

    def test_todo_list_view_redirects_if_not_logged_in(self):
        """Test that the todo list view redirects to login if user is not authenticated"""
        response = self.client.get(reverse('todo:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_todo_list_view_shows_todos_if_logged_in(self):
        """Test that the todo list view shows todos when user is logged in"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Todo')
        self.assertContains(response, 'Test Description')

    def test_todo_list_view_only_shows_user_todos(self):
        """Test that users only see their own todos"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        other_todo = Todo.objects.create(
            title='Other Todo',
            owner=other_user
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo:list'))
        self.assertContains(response, 'Test Todo')
        self.assertNotContains(response, 'Other Todo')

    def test_todo_create_view_redirects_if_not_logged_in(self):
        """Test that the todo create view redirects to login if user is not authenticated"""
        response = self.client.get(reverse('todo:create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_todo_create_view_get(self):
        """Test that the todo create view shows the form when accessed with GET"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo:create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form')
        self.assertContains(response, 'Create New Todo')

    def test_todo_create_view_post_success(self):
        """Test that a todo can be created successfully via POST"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('todo:create'), {
            'title': 'New Todo',
            'description': 'New Description'
        })
        
        self.assertRedirects(response, reverse('todo:list'))
        self.assertTrue(Todo.objects.filter(title='New Todo').exists())
        new_todo = Todo.objects.get(title='New Todo')
        self.assertEqual(new_todo.description, 'New Description')
        self.assertEqual(new_todo.owner, self.user)

    def test_todo_create_view_post_missing_title(self):
        """Test that creating a todo without a title shows an error"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('todo:create'), {
            'description': 'New Description'
        })
        
        self.assertEqual(response.status_code, 200)  # Stays on same page
        self.assertContains(response, 'Title is required!')

    def test_todo_update_view_redirects_if_not_logged_in(self):
        """Test that the todo update view redirects to login if user is not authenticated"""
        response = self.client.get(reverse('todo:update', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_todo_update_view_get(self):
        """Test that the todo update view shows the form when accessed with GET"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo:update', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form')
        self.assertContains(response, 'Test Todo')
        self.assertContains(response, 'Test Description')

    def test_todo_update_view_post_success(self):
        """Test that a todo can be updated successfully via POST"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('todo:update', args=[self.todo.pk]), {
            'title': 'Updated Todo',
            'description': 'Updated Description',
            'completed': 'on'
        })
        
        self.assertRedirects(response, reverse('todo:list'))
        updated_todo = Todo.objects.get(pk=self.todo.pk)
        self.assertEqual(updated_todo.title, 'Updated Todo')
        self.assertEqual(updated_todo.description, 'Updated Description')
        self.assertTrue(updated_todo.completed)

    def test_todo_update_view_post_missing_title(self):
        """Test that updating a todo without a title shows an error"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('todo:update', args=[self.todo.pk]), {
            'title': '',  # Empty title
            'description': 'Updated Description'
        })
        
        self.assertEqual(response.status_code, 200)  # Stays on same page
        self.assertContains(response, 'Title is required!')
        # Ensure the todo wasn't actually updated
        unchanged_todo = Todo.objects.get(pk=self.todo.pk)
        self.assertEqual(unchanged_todo.title, 'Test Todo')

    def test_todo_delete_view_redirects_if_not_logged_in(self):
        """Test that the todo delete view redirects to login if user is not authenticated"""
        response = self.client.get(reverse('todo:delete', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_todo_delete_view_get_confirmation(self):
        """Test that the delete view shows confirmation page on GET"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo:delete', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete Todo')
        self.assertContains(response, 'Test Todo')

    def test_todo_delete_view_post_success(self):
        """Test that a todo can be deleted successfully via POST"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('todo:delete', args=[self.todo.pk]))
        
        self.assertRedirects(response, reverse('todo:list'))
        self.assertFalse(Todo.objects.filter(pk=self.todo.pk).exists())

    def test_todo_toggle_complete_view(self):
        """Test that toggling a todo's completion status works"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo:toggle_complete', args=[self.todo.pk]))
        
        self.assertRedirects(response, reverse('todo:list'))
        updated_todo = Todo.objects.get(pk=self.todo.pk)
        self.assertTrue(updated_todo.completed)
        
        # Toggle again
        response = self.client.get(reverse('todo:toggle_complete', args=[self.todo.pk]))
        updated_todo = Todo.objects.get(pk=self.todo.pk)
        self.assertFalse(updated_todo.completed)

    def test_user_cannot_access_other_users_todo(self):
        """Test that users cannot access or modify other users' todos"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        other_todo = Todo.objects.create(
            title='Other Todo',
            owner=other_user
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        # Try to access update view for other user's todo
        response = self.client.get(reverse('todo:update', args=[other_todo.pk]))
        self.assertEqual(response.status_code, 404)
        
        # Try to access delete view for other user's todo
        response = self.client.get(reverse('todo:delete', args=[other_todo.pk]))
        self.assertEqual(response.status_code, 404)
        
        # Try to update other user's todo
        response = self.client.post(reverse('todo:update', args=[other_todo.pk]), {
            'title': 'Hacked Todo'
        })
        self.assertEqual(response.status_code, 404)
        other_todo.refresh_from_db()
        self.assertNotEqual(other_todo.title, 'Hacked Todo')