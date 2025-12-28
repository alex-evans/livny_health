export interface User {
  id: string;
  name: string;
  role: 'physician' | 'nurse' | 'pharmacist' | 'admin';
  specialty?: string;
  avatarUrl?: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
}
