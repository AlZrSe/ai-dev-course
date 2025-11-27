from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Todo

# Create your views here.
@login_required
def todo_list(request):
    todos = Todo.objects.filter(owner=request.user)
    return render(request, 'todo/list.html', {'todos': todos})

@login_required
def todo_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        if title:
            Todo.objects.create(
                title=title,
                description=description,
                owner=request.user
            )
            messages.success(request, 'Todo created successfully!')
            return redirect('todo:list')
        else:
            messages.error(request, 'Title is required!')
    
    return render(request, 'todo/create.html')

@login_required
def todo_update(request, pk):
    todo = get_object_or_404(Todo, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        completed = request.POST.get('completed') == 'on'
        
        if title:
            todo.title = title
            todo.description = description
            todo.completed = completed
            todo.save()
            messages.success(request, 'Todo updated successfully!')
            return redirect('todo:list')
        else:
            messages.error(request, 'Title is required!')
    
    return render(request, 'todo/update.html', {'todo': todo})

@login_required
def todo_delete(request, pk):
    todo = get_object_or_404(Todo, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        todo.delete()
        messages.success(request, 'Todo deleted successfully!')
        return redirect('todo:list')
    
    return render(request, 'todo/delete.html', {'todo': todo})

@login_required
def todo_toggle_complete(request, pk):
    todo = get_object_or_404(Todo, pk=pk, owner=request.user)
    todo.completed = not todo.completed
    todo.save()
    return redirect('todo:list')