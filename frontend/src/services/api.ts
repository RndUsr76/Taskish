import axios, { AxiosError, AxiosInstance } from 'axios';
import type { ApiResponse } from '../types';

const API_URL = import.meta.env.VITE_API_URL || '/api';
console.log('API_URL configured as:', API_URL);

class ApiService {
  private client: AxiosInstance;

  constructor() {
    console.log('ApiService constructor called, baseURL:', API_URL);
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      console.log('Request interceptor - token exists:', !!token);
      console.log('Request interceptor - token value (first 50 chars):', token ? token.substring(0, 50) : 'null');
      console.log('Request config:', config.method, config.url);
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
        console.log('Authorization header set:', config.headers.Authorization.substring(0, 60) + '...');
      }
      return config;
    });

    this.client.interceptors.response.use(
      (response) => {
        console.log('Response interceptor - success:', response.status, response.config.url);
        return response;
      },
      (error: AxiosError<ApiResponse<unknown>>) => {
        console.error('Response interceptor - error:', error.response?.status, error.config?.url, error.message);
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string): Promise<ApiResponse<T>> {
    console.log('API GET:', url);
    const response = await this.client.get<ApiResponse<T>>(url);
    console.log('API GET response:', url, response.data);
    return response.data;
  }

  async post<T>(url: string, data?: unknown): Promise<ApiResponse<T>> {
    console.log('API POST:', url, data);
    const response = await this.client.post<ApiResponse<T>>(url, data);
    console.log('API POST response:', url, response.data);
    return response.data;
  }

  async put<T>(url: string, data?: unknown): Promise<ApiResponse<T>> {
    const response = await this.client.put<ApiResponse<T>>(url, data);
    return response.data;
  }

  async patch<T>(url: string, data?: unknown): Promise<ApiResponse<T>> {
    const response = await this.client.patch<ApiResponse<T>>(url, data);
    return response.data;
  }

  async delete<T>(url: string): Promise<ApiResponse<T>> {
    const response = await this.client.delete<ApiResponse<T>>(url);
    return response.data;
  }
}

export const api = new ApiService();
