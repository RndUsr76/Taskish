import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { StatusBadge } from '../components/StatusBadge';
import { Modal } from '../components/Modal';
import { useAuth } from '../context/AuthContext';
import { todosService, CreateTodoData, UpdateTodoData } from '../services/todos';
import { tasksService } from '../services/tasks';
import type { PrivateTodo, TeamTask, TodoStatus } from '../types';

const TODO_STATUSES: TodoStatus[] = ['TODO', 'IN_PROGRESS', 'DONE'];

export function Dashboard() {
  const { user } = useAuth();
  const [todos, setTodos] = useState<PrivateTodo[]>([]);
  const [assignedTasks, setAssignedTasks] = useState<TeamTask[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTodo, setEditingTodo] = useState<PrivateTodo | null>(null);
  const [todoForm, setTodoForm] = useState<CreateTodoData>({
    title: '',
    description: '',
    status: 'TODO',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [todosData, tasksData] = await Promise.all([
        todosService.getAll(),
        tasksService.getAll(),
      ]);
      setTodos(todosData);
      setAssignedTasks(
        tasksData.filter((t) => t.assigned_user_id === user?.id)
      );
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setIsLoading(false);
    }
  };

  const openCreateModal = () => {
    setEditingTodo(null);
    setTodoForm({ title: '', description: '', status: 'TODO' });
    setIsModalOpen(true);
  };

  const openEditModal = (todo: PrivateTodo) => {
    setEditingTodo(todo);
    setTodoForm({
      title: todo.title,
      description: todo.description || '',
      status: todo.status,
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('handleSubmit called');
    console.log('todoForm:', todoForm);
    console.log('editingTodo:', editingTodo);
    try {
      if (editingTodo) {
        console.log('Updating existing todo...');
        const updated = await todosService.update(editingTodo.id, todoForm as UpdateTodoData);
        console.log('Update response:', updated);
        setTodos(todos.map((t) => (t.id === updated.id ? updated : t)));
      } else {
        console.log('Creating new todo...');
        const created = await todosService.create(todoForm);
        console.log('Create response:', created);
        setTodos([created, ...todos]);
      }
      setIsModalOpen(false);
    } catch (err) {
      console.error('Error in handleSubmit:', err);
      setError('Failed to save todo');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this todo?')) return;
    try {
      await todosService.delete(id);
      setTodos(todos.filter((t) => t.id !== id));
    } catch (err) {
      setError('Failed to delete todo');
    }
  };

  const handleStatusChange = async (todo: PrivateTodo, status: TodoStatus) => {
    try {
      const updated = await todosService.update(todo.id, { status });
      setTodos(todos.map((t) => (t.id === updated.id ? updated : t)));
    } catch (err) {
      setError('Failed to update status');
    }
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-8">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
            {error}
          </div>
        )}

        {/* Private Todos Section */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              My Private Todos
            </h2>
            <button
              onClick={openCreateModal}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Add Todo
            </button>
          </div>
          {todos.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              No private todos yet. Create one to get started!
            </p>
          ) : (
            <div className="bg-white shadow rounded-lg divide-y">
              {todos.map((todo) => (
                <div
                  key={todo.id}
                  className="p-4 flex items-center justify-between hover:bg-gray-50"
                >
                  <div className="flex-1 min-w-0 mr-4">
                    <h3 className="text-sm font-medium text-gray-900 truncate">
                      {todo.title}
                    </h3>
                    {todo.description && (
                      <p className="text-sm text-gray-500 truncate">
                        {todo.description}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center space-x-3">
                    <select
                      value={todo.status}
                      onChange={(e) =>
                        handleStatusChange(todo, e.target.value as TodoStatus)
                      }
                      className="text-sm border-gray-300 rounded-md"
                    >
                      {TODO_STATUSES.map((s) => (
                        <option key={s} value={s}>
                          {s.replace('_', ' ')}
                        </option>
                      ))}
                    </select>
                    <button
                      onClick={() => openEditModal(todo)}
                      className="text-indigo-600 hover:text-indigo-800 text-sm"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(todo.id)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Assigned Team Tasks Section */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            My Assigned Team Tasks
          </h2>
          {assignedTasks.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              No team tasks assigned to you yet.
            </p>
          ) : (
            <div className="bg-white shadow rounded-lg divide-y">
              {assignedTasks.map((task) => (
                <Link
                  key={task.id}
                  to={`/tasks/${task.id}`}
                  className="block p-4 hover:bg-gray-50"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0 mr-4">
                      <h3 className="text-sm font-medium text-gray-900">
                        {task.title}
                      </h3>
                      {task.description && (
                        <p className="text-sm text-gray-500 truncate">
                          {task.description}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-indigo-600 h-2 rounded-full"
                          style={{ width: `${task.progress}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-500 w-12">
                        {task.progress}%
                      </span>
                      <StatusBadge status={task.status} />
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </section>
      </div>

      {/* Todo Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingTodo ? 'Edit Todo' : 'Create Todo'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="title"
              className="block text-sm font-medium text-gray-700"
            >
              Title
            </label>
            <input
              type="text"
              id="title"
              required
              value={todoForm.title}
              onChange={(e) =>
                setTodoForm({ ...todoForm, title: e.target.value })
              }
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
          <div>
            <label
              htmlFor="description"
              className="block text-sm font-medium text-gray-700"
            >
              Description
            </label>
            <textarea
              id="description"
              rows={3}
              value={todoForm.description}
              onChange={(e) =>
                setTodoForm({ ...todoForm, description: e.target.value })
              }
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
          <div>
            <label
              htmlFor="status"
              className="block text-sm font-medium text-gray-700"
            >
              Status
            </label>
            <select
              id="status"
              value={todoForm.status}
              onChange={(e) =>
                setTodoForm({
                  ...todoForm,
                  status: e.target.value as TodoStatus,
                })
              }
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
              {TODO_STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s.replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700"
            >
              {editingTodo ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </Modal>
    </Layout>
  );
}
