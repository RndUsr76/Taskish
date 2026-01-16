import { api } from './api';
import type { PrivateTodo, TodoStatus } from '../types';

export interface CreateTodoData {
  title: string;
  description?: string;
  status?: TodoStatus;
  due_date?: string;
}

export interface UpdateTodoData {
  title?: string;
  description?: string | null;
  status?: TodoStatus;
  due_date?: string | null;
}

export const todosService = {
  async getAll(): Promise<PrivateTodo[]> {
    const response = await api.get<PrivateTodo[]>('/private-todos');
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error?.message || 'Failed to fetch todos');
  },

  async getById(id: number): Promise<PrivateTodo> {
    const response = await api.get<PrivateTodo>(`/private-todos/${id}`);
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error?.message || 'Failed to fetch todo');
  },

  async create(data: CreateTodoData): Promise<PrivateTodo> {
    const response = await api.post<PrivateTodo>('/private-todos', data);
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error?.message || 'Failed to create todo');
  },

  async update(id: number, data: UpdateTodoData): Promise<PrivateTodo> {
    const response = await api.put<PrivateTodo>(`/private-todos/${id}`, data);
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error?.message || 'Failed to update todo');
  },

  async delete(id: number): Promise<void> {
    const response = await api.delete(`/private-todos/${id}`);
    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to delete todo');
    }
  },
};
