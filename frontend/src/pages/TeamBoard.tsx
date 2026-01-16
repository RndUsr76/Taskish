import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { Modal } from '../components/Modal';
import { useAuth } from '../context/AuthContext';
import { tasksService, usersService, CreateTaskData } from '../services/tasks';
import type { TeamTask, TaskStatus, TeamMember } from '../types';

const COLUMNS: { status: TaskStatus; label: string; color: string }[] = [
  { status: 'TODO', label: 'To Do', color: 'bg-gray-100' },
  { status: 'IN_PROGRESS', label: 'In Progress', color: 'bg-blue-100' },
  { status: 'BLOCKED', label: 'Blocked', color: 'bg-red-100' },
  { status: 'DONE', label: 'Done', color: 'bg-green-100' },
];

export function TeamBoard() {
  const { user, isAdmin } = useAuth();
  const [tasks, setTasks] = useState<TeamTask[]>([]);
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [taskForm, setTaskForm] = useState<CreateTaskData>({
    title: '',
    description: '',
    assigned_user_id: undefined,
  });
  const [draggedTask, setDraggedTask] = useState<TeamTask | null>(null);

  useEffect(() => {
    loadData();
  }, [user?.team_id]);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [tasksData, membersData] = await Promise.all([
        tasksService.getAll(),
        user?.team_id ? usersService.getTeamMembers(user.team_id) : [],
      ]);
      setTasks(tasksData);
      setTeamMembers(membersData);
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await tasksService.create(taskForm);
      setTasks([created, ...tasks]);
      setIsModalOpen(false);
      setTaskForm({ title: '', description: '', assigned_user_id: undefined });
    } catch (err) {
      setError('Failed to create task');
    }
  };

  const handleDragStart = (task: TeamTask) => {
    setDraggedTask(task);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = async (status: TaskStatus) => {
    if (!draggedTask || draggedTask.status === status) {
      setDraggedTask(null);
      return;
    }

    // Check permission: admin can update any, member can update assigned
    if (!isAdmin && draggedTask.assigned_user_id !== user?.id) {
      setError('You can only update tasks assigned to you');
      setDraggedTask(null);
      return;
    }

    try {
      const updated = await tasksService.updateStatus(draggedTask.id, status);
      setTasks(tasks.map((t) => (t.id === updated.id ? updated : t)));
    } catch (err) {
      setError('Failed to update task status');
    }
    setDraggedTask(null);
  };

  const getTasksByStatus = (status: TaskStatus) =>
    tasks.filter((t) => t.status === status);

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
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Team Board</h1>
          {isAdmin && (
            <button
              onClick={() => setIsModalOpen(true)}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Create Task
            </button>
          )}
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
            {error}
            <button
              onClick={() => setError('')}
              className="ml-2 text-red-800 hover:text-red-900"
            >
              &times;
            </button>
          </div>
        )}

        {/* Kanban Board */}
        <div className="grid grid-cols-4 gap-4 min-h-[500px]">
          {COLUMNS.map((column) => (
            <div
              key={column.status}
              className={`${column.color} rounded-lg p-4`}
              onDragOver={handleDragOver}
              onDrop={() => handleDrop(column.status)}
            >
              <h2 className="font-semibold text-gray-700 mb-4 flex items-center justify-between">
                {column.label}
                <span className="bg-white px-2 py-1 rounded text-sm">
                  {getTasksByStatus(column.status).length}
                </span>
              </h2>
              <div className="space-y-3">
                {getTasksByStatus(column.status).map((task) => (
                  <Link
                    key={task.id}
                    to={`/tasks/${task.id}`}
                    draggable
                    onDragStart={() => handleDragStart(task)}
                    className={`block bg-white rounded-lg p-3 shadow-sm hover:shadow-md transition-shadow cursor-pointer ${
                      draggedTask?.id === task.id ? 'opacity-50' : ''
                    }`}
                  >
                    <h3 className="font-medium text-gray-900 text-sm mb-2">
                      {task.title}
                    </h3>
                    {task.description && (
                      <p className="text-xs text-gray-500 mb-2 line-clamp-2">
                        {task.description}
                      </p>
                    )}
                    <div className="flex items-center justify-between">
                      <div className="w-16 bg-gray-200 rounded-full h-1.5">
                        <div
                          className="bg-indigo-600 h-1.5 rounded-full"
                          style={{ width: `${task.progress}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500">
                        {task.progress}%
                      </span>
                    </div>
                    {task.assigned_user && (
                      <div className="mt-2 text-xs text-gray-500">
                        {task.assigned_user.name}
                      </div>
                    )}
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Create Task Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create Team Task"
      >
        <form onSubmit={handleCreateTask} className="space-y-4">
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
              value={taskForm.title}
              onChange={(e) =>
                setTaskForm({ ...taskForm, title: e.target.value })
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
              value={taskForm.description}
              onChange={(e) =>
                setTaskForm({ ...taskForm, description: e.target.value })
              }
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
          <div>
            <label
              htmlFor="assignee"
              className="block text-sm font-medium text-gray-700"
            >
              Assign To
            </label>
            <select
              id="assignee"
              value={taskForm.assigned_user_id || ''}
              onChange={(e) =>
                setTaskForm({
                  ...taskForm,
                  assigned_user_id: e.target.value
                    ? Number(e.target.value)
                    : undefined,
                })
              }
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
              <option value="">Unassigned</option>
              {teamMembers.map((member) => (
                <option key={member.id} value={member.id}>
                  {member.name}
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
              Create
            </button>
          </div>
        </form>
      </Modal>
    </Layout>
  );
}
