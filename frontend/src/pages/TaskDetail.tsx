import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { StatusBadge } from '../components/StatusBadge';
import { Modal } from '../components/Modal';
import { useAuth } from '../context/AuthContext';
import {
  tasksService,
  usersService,
  UpdateTaskData,
  CreateSubTaskData,
  UpdateSubTaskData,
} from '../services/tasks';
import type { TeamTask, SubTask, TaskStatus, TeamMember } from '../types';

const TASK_STATUSES: TaskStatus[] = ['TODO', 'IN_PROGRESS', 'BLOCKED', 'DONE'];

export function TaskDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user, isAdmin } = useAuth();
  const [task, setTask] = useState<TeamTask | null>(null);
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Edit task modal
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [taskForm, setTaskForm] = useState<UpdateTaskData>({});

  // Sub-task modal
  const [isSubTaskModalOpen, setIsSubTaskModalOpen] = useState(false);
  const [editingSubTask, setEditingSubTask] = useState<SubTask | null>(null);
  const [subTaskForm, setSubTaskForm] = useState<CreateSubTaskData>({
    title: '',
    status: 'TODO',
  });

  useEffect(() => {
    if (id) loadData();
  }, [id, user?.team_id]);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [taskData, membersData] = await Promise.all([
        tasksService.getById(Number(id)),
        user?.team_id ? usersService.getTeamMembers(user.team_id) : [],
      ]);
      setTask(taskData);
      setTeamMembers(membersData);
    } catch (err) {
      setError('Failed to load task');
    } finally {
      setIsLoading(false);
    }
  };

  const openEditModal = () => {
    if (!task) return;
    setTaskForm({
      title: task.title,
      description: task.description || '',
      status: task.status,
      assigned_user_id: task.assigned_user_id,
    });
    setIsEditModalOpen(true);
  };

  const handleUpdateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!task) return;
    try {
      const updated = await tasksService.update(task.id, taskForm);
      setTask({ ...updated, sub_tasks: task.sub_tasks });
      setIsEditModalOpen(false);
    } catch (err) {
      setError('Failed to update task');
    }
  };

  const handleDeleteTask = async () => {
    if (!task || !confirm('Are you sure you want to delete this task?')) return;
    try {
      await tasksService.delete(task.id);
      navigate('/board');
    } catch (err) {
      setError('Failed to delete task');
    }
  };

  const handleTaskStatusChange = async (status: TaskStatus) => {
    if (!task) return;
    // Check permission
    if (!isAdmin && task.assigned_user_id !== user?.id) {
      setError('You can only update tasks assigned to you');
      return;
    }
    try {
      const updated = await tasksService.updateStatus(task.id, status);
      setTask({ ...updated, sub_tasks: task.sub_tasks });
    } catch (err) {
      setError('Failed to update status');
    }
  };

  // Sub-task handlers
  const openCreateSubTaskModal = () => {
    setEditingSubTask(null);
    setSubTaskForm({ title: '', status: 'TODO' });
    setIsSubTaskModalOpen(true);
  };

  const openEditSubTaskModal = (subTask: SubTask) => {
    setEditingSubTask(subTask);
    setSubTaskForm({
      title: subTask.title,
      status: subTask.status,
      responsible_user_id: subTask.responsible_user_id || undefined,
    });
    setIsSubTaskModalOpen(true);
  };

  const handleSubmitSubTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!task) return;
    try {
      if (editingSubTask) {
        const updated = await tasksService.updateSubTask(
          task.id,
          editingSubTask.id,
          subTaskForm as UpdateSubTaskData
        );
        setTask({
          ...task,
          sub_tasks: task.sub_tasks?.map((st) =>
            st.id === updated.id ? updated : st
          ),
        });
      } else {
        const created = await tasksService.createSubTask(task.id, subTaskForm);
        setTask({
          ...task,
          sub_tasks: [...(task.sub_tasks || []), created],
        });
      }
      setIsSubTaskModalOpen(false);
      // Reload to get updated progress
      loadData();
    } catch (err) {
      setError('Failed to save sub-task');
    }
  };

  const handleDeleteSubTask = async (subTaskId: number) => {
    if (!task || !confirm('Are you sure you want to delete this sub-task?'))
      return;
    try {
      await tasksService.deleteSubTask(task.id, subTaskId);
      setTask({
        ...task,
        sub_tasks: task.sub_tasks?.filter((st) => st.id !== subTaskId),
      });
      loadData();
    } catch (err) {
      setError('Failed to delete sub-task');
    }
  };

  const handleSubTaskStatusChange = async (
    subTask: SubTask,
    status: TaskStatus
  ) => {
    if (!task) return;
    // Check permission
    if (!isAdmin && subTask.responsible_user_id !== user?.id) {
      setError('You can only update sub-tasks assigned to you');
      return;
    }
    try {
      const updated = await tasksService.updateSubTaskStatus(
        task.id,
        subTask.id,
        status
      );
      setTask({
        ...task,
        sub_tasks: task.sub_tasks?.map((st) =>
          st.id === updated.id ? updated : st
        ),
      });
      loadData();
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

  if (!task) {
    return (
      <Layout>
        <div className="text-center py-12">
          <h2 className="text-xl text-gray-600">Task not found</h2>
        </div>
      </Layout>
    );
  }

  const canUpdateStatus =
    isAdmin || task.assigned_user_id === user?.id;

  return (
    <Layout>
      <div className="space-y-6">
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

        {/* Task Header */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                {task.title}
              </h1>
              {task.description && (
                <p className="text-gray-600 mb-4">{task.description}</p>
              )}
              <div className="flex items-center space-x-4">
                <StatusBadge status={task.status} />
                <div className="flex items-center space-x-2">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-indigo-600 h-2 rounded-full"
                      style={{ width: `${task.progress}%` }}
                    />
                  </div>
                  <span className="text-sm text-gray-500">{task.progress}%</span>
                </div>
                {task.assigned_user && (
                  <span className="text-sm text-gray-500">
                    Assigned to: {task.assigned_user.name}
                  </span>
                )}
              </div>
            </div>
            <div className="flex items-center space-x-3">
              {canUpdateStatus && (
                <select
                  value={task.status}
                  onChange={(e) =>
                    handleTaskStatusChange(e.target.value as TaskStatus)
                  }
                  className="text-sm border-gray-300 rounded-md"
                >
                  {TASK_STATUSES.map((s) => (
                    <option key={s} value={s}>
                      {s.replace('_', ' ')}
                    </option>
                  ))}
                </select>
              )}
              {isAdmin && (
                <>
                  <button
                    onClick={openEditModal}
                    className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                  >
                    Edit
                  </button>
                  <button
                    onClick={handleDeleteTask}
                    className="text-red-600 hover:text-red-800 text-sm font-medium"
                  >
                    Delete
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Sub-Tasks Section */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Sub-Tasks</h2>
            {isAdmin && (
              <button
                onClick={openCreateSubTaskModal}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Add Sub-Task
              </button>
            )}
          </div>
          {!task.sub_tasks || task.sub_tasks.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              No sub-tasks yet.
              {isAdmin && ' Create one to break down this task.'}
            </p>
          ) : (
            <div className="divide-y">
              {task.sub_tasks.map((subTask) => {
                const canUpdateSubTask =
                  isAdmin || subTask.responsible_user_id === user?.id;
                return (
                  <div
                    key={subTask.id}
                    className="py-4 flex items-center justify-between"
                  >
                    <div className="flex-1 min-w-0 mr-4">
                      <h3 className="text-sm font-medium text-gray-900">
                        {subTask.title}
                      </h3>
                      {subTask.responsible_user && (
                        <p className="text-xs text-gray-500">
                          Assigned to: {subTask.responsible_user.name}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center space-x-3">
                      {canUpdateSubTask ? (
                        <select
                          value={subTask.status}
                          onChange={(e) =>
                            handleSubTaskStatusChange(
                              subTask,
                              e.target.value as TaskStatus
                            )
                          }
                          className="text-sm border-gray-300 rounded-md"
                        >
                          {TASK_STATUSES.map((s) => (
                            <option key={s} value={s}>
                              {s.replace('_', ' ')}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <StatusBadge status={subTask.status} />
                      )}
                      {isAdmin && (
                        <>
                          <button
                            onClick={() => openEditSubTaskModal(subTask)}
                            className="text-indigo-600 hover:text-indigo-800 text-sm"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteSubTask(subTask.id)}
                            className="text-red-600 hover:text-red-800 text-sm"
                          >
                            Delete
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Edit Task Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Edit Task"
      >
        <form onSubmit={handleUpdateTask} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Title
            </label>
            <input
              type="text"
              required
              value={taskForm.title || ''}
              onChange={(e) =>
                setTaskForm({ ...taskForm, title: e.target.value })
              }
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              rows={3}
              value={taskForm.description || ''}
              onChange={(e) =>
                setTaskForm({ ...taskForm, description: e.target.value })
              }
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Assign To
            </label>
            <select
              value={taskForm.assigned_user_id || ''}
              onChange={(e) =>
                setTaskForm({
                  ...taskForm,
                  assigned_user_id: e.target.value
                    ? Number(e.target.value)
                    : null,
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
              onClick={() => setIsEditModalOpen(false)}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700"
            >
              Update
            </button>
          </div>
        </form>
      </Modal>

      {/* Sub-Task Modal */}
      <Modal
        isOpen={isSubTaskModalOpen}
        onClose={() => setIsSubTaskModalOpen(false)}
        title={editingSubTask ? 'Edit Sub-Task' : 'Create Sub-Task'}
      >
        <form onSubmit={handleSubmitSubTask} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Title
            </label>
            <input
              type="text"
              required
              value={subTaskForm.title}
              onChange={(e) =>
                setSubTaskForm({ ...subTaskForm, title: e.target.value })
              }
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Status
            </label>
            <select
              value={subTaskForm.status}
              onChange={(e) =>
                setSubTaskForm({
                  ...subTaskForm,
                  status: e.target.value as TaskStatus,
                })
              }
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
              {TASK_STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s.replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Responsible User
            </label>
            <select
              value={subTaskForm.responsible_user_id || ''}
              onChange={(e) =>
                setSubTaskForm({
                  ...subTaskForm,
                  responsible_user_id: e.target.value
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
              onClick={() => setIsSubTaskModalOpen(false)}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700"
            >
              {editingSubTask ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </Modal>
    </Layout>
  );
}
