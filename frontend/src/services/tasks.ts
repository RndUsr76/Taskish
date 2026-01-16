import { api } from './api';
import type { TeamTask, SubTask, TaskStatus, TeamMember } from '../types';

export interface CreateTaskData {
  title: string;
  description?: string;
  status?: TaskStatus;
  assigned_user_id?: number;
}

export interface UpdateTaskData {
  title?: string;
  description?: string | null;
  status?: TaskStatus;
  assigned_user_id?: number | null;
}

export interface CreateSubTaskData {
  title: string;
  status?: TaskStatus;
  responsible_user_id?: number;
}

export interface UpdateSubTaskData {
  title?: string;
  status?: TaskStatus;
  responsible_user_id?: number | null;
}

export const tasksService = {
  async getAll(): Promise<TeamTask[]> {
    const response = await api.get<TeamTask[]>('/team-tasks');
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error?.message || 'Failed to fetch tasks');
  },

  async getById(id: number): Promise<TeamTask> {
    const response = await api.get<TeamTask>(`/team-tasks/${id}`);
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error?.message || 'Failed to fetch task');
  },

  async create(data: CreateTaskData): Promise<TeamTask> {
    const response = await api.post<TeamTask>('/team-tasks', data);
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error?.message || 'Failed to create task');
  },

  async update(id: number, data: UpdateTaskData): Promise<TeamTask> {
    const response = await api.put<TeamTask>(`/team-tasks/${id}`, data);
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error?.message || 'Failed to update task');
  },

  async updateStatus(id: number, status: TaskStatus): Promise<TeamTask> {
    const response = await api.patch<TeamTask>(`/team-tasks/${id}/status`, { status });
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error?.message || 'Failed to update status');
  },

  async assign(id: number, userId: number | null): Promise<TeamTask> {
    const response = await api.patch<TeamTask>(`/team-tasks/${id}/assign`, {
      assigned_user_id: userId,
    });
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error?.message || 'Failed to assign task');
  },

  async delete(id: number): Promise<void> {
    const response = await api.delete(`/team-tasks/${id}`);
    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to delete task');
    }
  },

  // Sub-tasks
  async getSubTasks(taskId: number): Promise<SubTask[]> {
    const response = await api.get<SubTask[]>(`/team-tasks/${taskId}/sub-tasks`);
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error?.message || 'Failed to fetch sub-tasks');
  },

  async createSubTask(taskId: number, data: CreateSubTaskData): Promise<SubTask> {
    const response = await api.post<SubTask>(`/team-tasks/${taskId}/sub-tasks`, data);
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error?.message || 'Failed to create sub-task');
  },

  async updateSubTask(
    taskId: number,
    subTaskId: number,
    data: UpdateSubTaskData
  ): Promise<SubTask> {
    const response = await api.put<SubTask>(
      `/team-tasks/${taskId}/sub-tasks/${subTaskId}`,
      data
    );
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error?.message || 'Failed to update sub-task');
  },

  async updateSubTaskStatus(
    taskId: number,
    subTaskId: number,
    status: TaskStatus
  ): Promise<SubTask> {
    const response = await api.patch<SubTask>(
      `/team-tasks/${taskId}/sub-tasks/${subTaskId}/status`,
      { status }
    );
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error?.message || 'Failed to update sub-task status');
  },

  async deleteSubTask(taskId: number, subTaskId: number): Promise<void> {
    const response = await api.delete(`/team-tasks/${taskId}/sub-tasks/${subTaskId}`);
    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to delete sub-task');
    }
  },
};

export const usersService = {
  async getTeamMembers(teamId: number): Promise<TeamMember[]> {
    const response = await api.get<TeamMember[]>(`/teams/${teamId}/users`);
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error?.message || 'Failed to fetch team members');
  },
};
