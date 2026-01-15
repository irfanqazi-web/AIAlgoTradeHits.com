/**
 * PasswordChangeModal Component - Password update UI
 *
 * Handles password changes using the AuthContext.
 * Styled with Tailwind CSS classes.
 *
 * @version 5.2.0
 */

import { useState } from 'react';
import { useAuth } from '@/context';
import { Lock, X, AlertCircle, CheckCircle, Eye, EyeOff } from 'lucide-react';

export default function PasswordChangeModal({
  onClose,
  onSuccess,
  onChangePassword,
  isFirstLogin = false
}) {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [showOldPassword, setShowOldPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Use AuthContext as fallback if onChangePassword prop not provided
  const { changePassword: contextChangePassword } = useAuth();
  const changePassword = onChangePassword || contextChangePassword;

  const validatePassword = (password) => {
    if (password.length < 8) {
      return 'Password must be at least 8 characters long';
    }
    if (!/[A-Z]/.test(password)) {
      return 'Password must contain at least one uppercase letter';
    }
    if (!/[a-z]/.test(password)) {
      return 'Password must contain at least one lowercase letter';
    }
    if (!/[0-9]/.test(password)) {
      return 'Password must contain at least one number';
    }
    if (!/[!@#$%^&*]/.test(password)) {
      return 'Password must contain at least one special character (!@#$%^&*)';
    }
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (newPassword !== confirmPassword) {
      setError('New passwords do not match');
      return;
    }

    const passwordError = validatePassword(newPassword);
    if (passwordError) {
      setError(passwordError);
      return;
    }

    setLoading(true);

    try {
      const result = await changePassword(oldPassword, newPassword);

      if (result) {
        setSuccess(true);
        setTimeout(() => {
          onSuccess();
        }, 2000);
      } else {
        setError('Failed to change password. Please check your current password.');
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
      console.error('Password change error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-[10000] p-5">
      <div className="w-full max-w-lg bg-gradient-to-br from-slate-800 to-slate-900 rounded-3xl p-8 border border-slate-700 shadow-2xl relative">

        {/* Close Button (only if not first login) */}
        {!isFirstLogin && (
          <button
            onClick={onClose}
            className="absolute top-5 right-5 bg-transparent border-none text-slate-400 cursor-pointer p-2 flex items-center justify-center rounded-lg transition-all hover:bg-slate-700 hover:text-white"
          >
            <X size={24} />
          </button>
        )}

        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-emerald-500 to-blue-500 rounded-2xl mb-4">
            <Lock size={32} className="text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">
            {isFirstLogin ? 'Change Your Password' : 'Update Password'}
          </h2>
          <p className="text-slate-400 text-sm">
            {isFirstLogin
              ? 'For security reasons, please change your password before continuing'
              : 'Enter your current password and choose a new one'}
          </p>
        </div>

        {/* Success Message */}
        {success && (
          <div className="bg-emerald-500/10 border border-emerald-500 rounded-xl p-4 mb-6 flex items-center gap-3">
            <CheckCircle size={20} className="text-emerald-500" />
            <span className="text-emerald-500 text-sm">
              Password changed successfully!
            </span>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-500/10 border border-red-500 rounded-xl p-4 mb-6 flex items-center gap-3">
            <AlertCircle size={20} className="text-red-500" />
            <span className="text-red-500 text-sm">{error}</span>
          </div>
        )}

        {/* Form */}
        {!success && (
          <form onSubmit={handleSubmit}>
            {/* Current Password */}
            <div className="mb-5">
              <label className="block text-slate-400 text-sm font-medium mb-2">
                Current Password
              </label>
              <div className="relative">
                <input
                  type={showOldPassword ? 'text' : 'password'}
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                  required
                  className="w-full py-3 px-3 pr-10 bg-slate-900 border border-slate-700 rounded-lg text-white text-sm outline-none transition-colors focus:border-emerald-500"
                />
                <button
                  type="button"
                  onClick={() => setShowOldPassword(!showOldPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 bg-transparent border-none cursor-pointer p-1 flex items-center"
                >
                  {showOldPassword ? (
                    <EyeOff size={18} className="text-slate-500" />
                  ) : (
                    <Eye size={18} className="text-slate-500" />
                  )}
                </button>
              </div>
            </div>

            {/* New Password */}
            <div className="mb-5">
              <label className="block text-slate-400 text-sm font-medium mb-2">
                New Password
              </label>
              <div className="relative">
                <input
                  type={showNewPassword ? 'text' : 'password'}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  className="w-full py-3 px-3 pr-10 bg-slate-900 border border-slate-700 rounded-lg text-white text-sm outline-none transition-colors focus:border-emerald-500"
                />
                <button
                  type="button"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 bg-transparent border-none cursor-pointer p-1 flex items-center"
                >
                  {showNewPassword ? (
                    <EyeOff size={18} className="text-slate-500" />
                  ) : (
                    <Eye size={18} className="text-slate-500" />
                  )}
                </button>
              </div>
            </div>

            {/* Confirm New Password */}
            <div className="mb-6">
              <label className="block text-slate-400 text-sm font-medium mb-2">
                Confirm New Password
              </label>
              <div className="relative">
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  className="w-full py-3 px-3 pr-10 bg-slate-900 border border-slate-700 rounded-lg text-white text-sm outline-none transition-colors focus:border-emerald-500"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 bg-transparent border-none cursor-pointer p-1 flex items-center"
                >
                  {showConfirmPassword ? (
                    <EyeOff size={18} className="text-slate-500" />
                  ) : (
                    <Eye size={18} className="text-slate-500" />
                  )}
                </button>
              </div>
            </div>

            {/* Password Requirements */}
            <div className="bg-slate-900 border border-slate-700 rounded-lg p-3 mb-6">
              <p className="text-slate-400 text-xs font-semibold mb-2">
                Password must contain:
              </p>
              <ul className="text-slate-500 text-xs list-disc pl-5 space-y-1">
                <li>At least 8 characters</li>
                <li>One uppercase letter</li>
                <li>One lowercase letter</li>
                <li>One number</li>
                <li>One special character (!@#$%^&*)</li>
              </ul>
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3.5 text-white border-none rounded-xl text-base font-semibold transition-all ${
                loading
                  ? 'bg-slate-600 cursor-not-allowed'
                  : 'bg-gradient-to-r from-emerald-500 to-emerald-600 cursor-pointer hover:shadow-lg hover:shadow-emerald-500/30'
              }`}
            >
              {loading ? 'Changing Password...' : 'Change Password'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
