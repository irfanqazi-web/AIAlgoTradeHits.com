import React, { useState, useEffect } from 'react';
import { Users, UserPlus, Edit, Trash2, X, Save, Mail } from 'lucide-react';
import apiService from '../services/api';

export default function AdminPanel({ onClose }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [newUser, setNewUser] = useState({ email: '', name: '', role: 'user' });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await apiService.getUsers();
      if (response.success) {
        setUsers(response.users);
      } else {
        setError('Failed to load users');
      }
    } catch (err) {
      setError('Error loading users: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async () => {
    try {
      const response = await apiService.createUser(newUser);
      if (response.success) {
        setNewUser({ email: '', name: '', role: 'user' });
        setShowCreateForm(false);
        loadUsers();
      } else {
        alert('Failed to create user: ' + response.error);
      }
    } catch (err) {
      alert('Error creating user: ' + err.message);
    }
  };

  const handleUpdateUser = async (userId, updates) => {
    try {
      const response = await apiService.updateUser(userId, updates);
      if (response.success) {
        setEditingUser(null);
        loadUsers();
      } else {
        alert('Failed to update user: ' + response.error);
      }
    } catch (err) {
      alert('Error updating user: ' + err.message);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!confirm('Are you sure you want to delete this user?')) return;

    try {
      const response = await apiService.deleteUser(userId);
      if (response.success) {
        loadUsers();
      } else {
        alert('Failed to delete user: ' + response.error);
      }
    } catch (err) {
      alert('Error deleting user: ' + err.message);
    }
  };

  const handleSendInvitation = async (userId) => {
    try {
      const response = await apiService.sendInvitation(userId);
      if (response.success) {
        alert(`Invitation email sent successfully!\n\nEmail Details:\nTo: ${response.email_content.to}\nSubject: ${response.email_content.subject}\n\nNote: Copy the email content below and send it manually:\n\n${response.email_content.body}`);
      } else {
        alert('Failed to send invitation: ' + response.error);
      }
    } catch (err) {
      alert('Error sending invitation: ' + err.message);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: '#0a0e27',
      zIndex: 9999,
      overflow: 'auto',
      padding: '20px'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '30px',
          borderBottom: '2px solid #1e293b',
          paddingBottom: '20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Users size={32} color="#10b981" />
            <h1 style={{
              fontSize: '32px',
              fontWeight: 'bold',
              background: 'linear-gradient(135deg, #10b981 0%, #3b82f6 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              margin: 0
            }}>
              User Management
            </h1>
          </div>
          <button
            onClick={onClose}
            style={{
              background: '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              padding: '12px 24px',
              fontSize: '16px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.3s'
            }}
            onMouseOver={(e) => e.target.style.background = '#dc2626'}
            onMouseOut={(e) => e.target.style.background = '#ef4444'}
          >
            <X size={20} />
            Close
          </button>
        </div>

        {/* Create User Button */}
        <div style={{ marginBottom: '20px' }}>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            style={{
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              padding: '12px 24px',
              fontSize: '16px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.3s'
            }}
          >
            <UserPlus size={20} />
            Create New User
          </button>
        </div>

        {/* Create User Form */}
        {showCreateForm && (
          <div style={{
            background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
            borderRadius: '16px',
            padding: '24px',
            border: '1px solid #334155',
            marginBottom: '20px'
          }}>
            <h3 style={{ color: '#10b981', marginBottom: '20px' }}>Create New User</h3>
            <div style={{ display: 'grid', gap: '16px' }}>
              <div>
                <label style={{ color: '#94a3b8', display: 'block', marginBottom: '8px' }}>Email</label>
                <input
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '12px',
                    background: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    color: 'white',
                    fontSize: '16px'
                  }}
                  placeholder="user@example.com"
                />
              </div>
              <div>
                <label style={{ color: '#94a3b8', display: 'block', marginBottom: '8px' }}>Name</label>
                <input
                  type="text"
                  value={newUser.name}
                  onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '12px',
                    background: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    color: 'white',
                    fontSize: '16px'
                  }}
                  placeholder="John Doe"
                />
              </div>
              <div>
                <label style={{ color: '#94a3b8', display: 'block', marginBottom: '8px' }}>Role</label>
                <select
                  value={newUser.role}
                  onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '12px',
                    background: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    color: 'white',
                    fontSize: '16px'
                  }}
                >
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <div style={{ display: 'flex', gap: '12px' }}>
                <button
                  onClick={handleCreateUser}
                  style={{
                    background: '#10b981',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '12px 24px',
                    fontSize: '16px',
                    cursor: 'pointer'
                  }}
                >
                  Create User
                </button>
                <button
                  onClick={() => setShowCreateForm(false)}
                  style={{
                    background: '#64748b',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '12px 24px',
                    fontSize: '16px',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Loading/Error States */}
        {loading && (
          <div style={{ color: 'white', textAlign: 'center', padding: '40px' }}>
            Loading users...
          </div>
        )}

        {error && (
          <div style={{ color: '#ef4444', textAlign: 'center', padding: '40px' }}>
            {error}
          </div>
        )}

        {/* Users Table */}
        {!loading && !error && (
          <div style={{
            background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
            borderRadius: '16px',
            padding: '24px',
            border: '1px solid #334155'
          }}>
            <h3 style={{ color: '#10b981', marginBottom: '20px' }}>Users ({users.length})</h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={{
                width: '100%',
                borderCollapse: 'collapse',
                color: 'white'
              }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #334155' }}>
                    <th style={{ padding: '12px', textAlign: 'left', color: '#94a3b8' }}>Email</th>
                    <th style={{ padding: '12px', textAlign: 'left', color: '#94a3b8' }}>Name</th>
                    <th style={{ padding: '12px', textAlign: 'left', color: '#94a3b8' }}>Role</th>
                    <th style={{ padding: '12px', textAlign: 'left', color: '#94a3b8' }}>Status</th>
                    <th style={{ padding: '12px', textAlign: 'left', color: '#94a3b8' }}>Created</th>
                    <th style={{ padding: '12px', textAlign: 'left', color: '#94a3b8' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.user_id} style={{ borderBottom: '1px solid #334155' }}>
                      <td style={{ padding: '12px' }}>{user.email}</td>
                      <td style={{ padding: '12px' }}>
                        {editingUser === user.user_id ? (
                          <input
                            type="text"
                            defaultValue={user.name}
                            id={`name-${user.user_id}`}
                            style={{
                              background: '#0f172a',
                              border: '1px solid #334155',
                              borderRadius: '4px',
                              color: 'white',
                              padding: '4px 8px'
                            }}
                          />
                        ) : (
                          user.name
                        )}
                      </td>
                      <td style={{ padding: '12px' }}>
                        {editingUser === user.user_id ? (
                          <select
                            defaultValue={user.role}
                            id={`role-${user.user_id}`}
                            style={{
                              background: '#0f172a',
                              border: '1px solid #334155',
                              borderRadius: '4px',
                              color: 'white',
                              padding: '4px 8px'
                            }}
                          >
                            <option value="user">User</option>
                            <option value="admin">Admin</option>
                          </select>
                        ) : (
                          <span style={{
                            background: user.role === 'admin' ? '#7c3aed' : '#3b82f6',
                            padding: '4px 12px',
                            borderRadius: '12px',
                            fontSize: '12px',
                            fontWeight: 'bold'
                          }}>
                            {user.role}
                          </span>
                        )}
                      </td>
                      <td style={{ padding: '12px' }}>
                        <span style={{
                          background: user.is_active ? '#10b981' : '#ef4444',
                          padding: '4px 12px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: 'bold'
                        }}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td style={{ padding: '12px' }}>
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                      <td style={{ padding: '12px' }}>
                        {editingUser === user.user_id ? (
                          <button
                            onClick={() => {
                              const name = document.getElementById(`name-${user.user_id}`).value;
                              const role = document.getElementById(`role-${user.user_id}`).value;
                              handleUpdateUser(user.user_id, { name, role });
                            }}
                            style={{
                              background: '#10b981',
                              color: 'white',
                              border: 'none',
                              borderRadius: '4px',
                              padding: '6px 12px',
                              cursor: 'pointer',
                              marginRight: '8px'
                            }}
                          >
                            <Save size={16} />
                          </button>
                        ) : (
                          <>
                            <button
                              onClick={() => handleSendInvitation(user.user_id)}
                              style={{
                                background: '#10b981',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                padding: '6px 12px',
                                cursor: 'pointer',
                                marginRight: '8px'
                              }}
                              title="Send invitation email"
                            >
                              <Mail size={16} />
                            </button>
                            <button
                              onClick={() => setEditingUser(user.user_id)}
                              style={{
                                background: '#3b82f6',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                padding: '6px 12px',
                                cursor: 'pointer',
                                marginRight: '8px'
                              }}
                            >
                              <Edit size={16} />
                            </button>
                            <button
                              onClick={() => handleDeleteUser(user.user_id)}
                              style={{
                                background: '#ef4444',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                padding: '6px 12px',
                                cursor: 'pointer'
                              }}
                            >
                              <Trash2 size={16} />
                            </button>
                          </>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
