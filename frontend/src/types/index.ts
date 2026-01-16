export type UserRole = 'ADMIN' | 'MEMBER';

export type TodoStatus = 'TODO' | 'IN_PROGRESS' | 'DONE';

export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'BLOCKED' | 'DONE';

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  team_id: number | null;
  team?: Team;
  created_at: string;
  updated_at: string;
}

export interface Team {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface PrivateTodo {
  id: number;
  owner_user_id: number;
  title: string;
  description: string | null;
  status: TodoStatus;
  due_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface TeamTask {
  id: number;
  team_id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  assigned_user_id: number | null;
  assigned_user?: Pick<User, 'id' | 'name' | 'email'> | null;
  progress: number;
  sub_tasks?: SubTask[];
  created_at: string;
  updated_at: string;
}

export interface SubTask {
  id: number;
  team_task_id: number;
  title: string;
  status: TaskStatus;
  responsible_user_id: number | null;
  responsible_user?: Pick<User, 'id' | 'name' | 'email'> | null;
  created_at: string;
  updated_at: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: {
    message: string;
    code: number;
    details?: Record<string, string>;
  };
}

export interface AuthResponse {
  user: User;
  access_token: string;
}

export interface TeamMember {
  id: number;
  name: string;
  email: string;
  role: UserRole;
}
