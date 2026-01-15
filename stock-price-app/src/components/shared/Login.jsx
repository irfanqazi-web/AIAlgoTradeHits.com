/**
 * Login Component - Authentication UI
 *
 * Handles user authentication using the AuthContext.
 * Styled with Tailwind CSS classes.
 *
 * @version 5.2.0
 */

import { useState } from 'react';
import { useAuth } from '@/context';
import { LogIn, Mail, Lock, AlertCircle, Eye, EyeOff, User } from 'lucide-react';

// Quick login accounts for development
const QUICK_LOGINS = [
  { email: 'irfan.qazi@aialgotradehits.com', name: 'Irfan Qazi', color: 'blue' },
  { email: 'saleem.ahmad@aialgotradehits.com', name: 'Saleem Ahmad', color: 'emerald' }
];

export default function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [localError, setLocalError] = useState('');

  // Use AuthContext for authentication
  const { login, isLoading, error: authError } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalError('');

    const emailLower = email.toLowerCase().trim();

    if (!emailLower || !password) {
      setLocalError('Please enter both email and password.');
      return;
    }

    // Try context-based login first (API)
    const success = await login(emailLower, password);

    if (success) {
      // Notify parent component if provided
      if (onLoginSuccess) {
        onLoginSuccess({ email: emailLower, password });
      }
    } else {
      // AuthContext will set the error
      setLocalError(authError || 'Login failed. Please check your credentials.');
    }
  };

  // Quick login handler
  const quickLogin = (userEmail) => {
    setEmail(userEmail);
    setPassword('Trading2024!');
    setLocalError('');
  };

  const displayError = localError || authError;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-5">
      <div className="w-full max-w-md bg-gradient-to-br from-slate-800 to-slate-900 rounded-3xl p-12 border border-slate-700 shadow-2xl">

        {/* Logo/Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-emerald-500 to-blue-500 rounded-2xl mb-5">
            <LogIn size={40} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-blue-400 bg-clip-text text-transparent mb-2">
            AIAlgoTradeHits
          </h1>
          <p className="text-slate-400 text-base">
            Sign in to your account
          </p>
        </div>

        {/* Error Message */}
        {displayError && (
          <div className="bg-red-500/10 border border-red-500 rounded-xl p-4 mb-6 flex items-center gap-3">
            <AlertCircle size={20} className="text-red-500 shrink-0" />
            <span className="text-red-500 text-sm">{displayError}</span>
          </div>
        )}

        {/* Quick Login Buttons */}
        <div className="mb-6">
          <p className="text-slate-500 text-sm mb-3 text-center">Quick Login:</p>
          <div className="flex gap-3">
            {QUICK_LOGINS.map((user) => (
              <button
                key={user.email}
                type="button"
                onClick={() => quickLogin(user.email)}
                className={`flex-1 p-3 rounded-xl text-sm cursor-pointer flex items-center justify-center gap-2 transition-all duration-200 ${
                  user.color === 'blue'
                    ? 'bg-blue-500/10 border border-blue-500 text-blue-400 hover:bg-blue-500/20'
                    : 'bg-emerald-500/10 border border-emerald-500 text-emerald-400 hover:bg-emerald-500/20'
                }`}
              >
                <User size={16} />
                {user.name}
              </button>
            ))}
          </div>
        </div>

        {/* Divider */}
        <div className="flex items-center my-6 gap-4">
          <div className="flex-1 h-px bg-slate-700" />
          <span className="text-slate-500 text-sm">or enter credentials</span>
          <div className="flex-1 h-px bg-slate-700" />
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit}>
          {/* Email Field */}
          <div className="mb-6">
            <label className="block text-slate-400 text-sm font-medium mb-2">
              Email Address
            </label>
            <div className="relative flex items-center">
              <Mail
                size={20}
                className="absolute left-4 text-slate-500 pointer-events-none"
              />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@aialgotradehits.com"
                className="w-full py-3.5 pl-12 pr-4 bg-slate-900 border border-slate-700 rounded-xl text-white text-base outline-none transition-colors focus:border-emerald-500"
              />
            </div>
          </div>

          {/* Password Field */}
          <div className="mb-8">
            <label className="block text-slate-400 text-sm font-medium mb-2">
              Password
            </label>
            <div className="relative flex items-center">
              <Lock
                size={20}
                className="absolute left-4 text-slate-500 pointer-events-none z-10"
              />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Enter your password"
                className="w-full py-3.5 px-12 bg-slate-900 border border-slate-700 rounded-xl text-white text-base outline-none transition-colors focus:border-emerald-500"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 bg-transparent border-none cursor-pointer p-1 flex items-center justify-center z-10"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? (
                  <EyeOff size={20} className="text-slate-500" />
                ) : (
                  <Eye size={20} className="text-slate-500" />
                )}
              </button>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className={`w-full py-4 text-white border-none rounded-xl text-base font-semibold flex items-center justify-center gap-2 transition-all duration-300 ${
              isLoading
                ? 'bg-slate-600 cursor-not-allowed'
                : 'bg-gradient-to-r from-emerald-500 to-emerald-600 cursor-pointer hover:-translate-y-0.5 hover:shadow-lg hover:shadow-emerald-500/30'
            }`}
          >
            <LogIn size={20} />
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {/* Footer */}
        <div className="mt-8 text-center text-slate-500 text-sm">
          <p>AIAlgoTradeHits.com Trading Platform</p>
          <p className="mt-2 text-slate-600">Authorized users only</p>
        </div>
      </div>
    </div>
  );
}
