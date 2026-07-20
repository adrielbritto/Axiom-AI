import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function ProfilePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [bio, setBio] = useState(user?.avatar_url || '');
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!user) {
      navigate('/login');
    }
  }, [user, navigate]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // TODO: Call API to update profile
      setMessage('Profile updated successfully!');
      setIsEditing(false);
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Failed to update profile');
    } finally {
      setIsSaving(false);
    }
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold text-blue-600">Axiom AI</h1>
            <button
              onClick={() => {
                logout();
                navigate('/login');
              }}
              className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-8">Profile Settings</h2>

        {/* Success Message */}
        {message && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-6">
            {message}
          </div>
        )}

        {/* Profile Card */}
        <div className="bg-white rounded-lg shadow p-8 mb-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Account Information</h3>

          {/* Email (Read-only) */}
          <div className="mb-6">
            <label className="block text-gray-700 font-medium mb-2">Email Address</label>
            <input
              type="email"
              value={user.email}
              disabled
              className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-600 cursor-not-allowed"
            />
            <p className="text-sm text-gray-500 mt-1">Email cannot be changed</p>
          </div>

          {/* Full Name */}
          <div className="mb-6">
            <label className="block text-gray-700 font-medium mb-2">Full Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              disabled={!isEditing}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition disabled:bg-gray-100 disabled:text-gray-600 disabled:cursor-not-allowed"
            />
          </div>

          {/* Bio */}
          <div className="mb-6">
            <label className="block text-gray-700 font-medium mb-2">Bio</label>
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              disabled={!isEditing}
              placeholder="Tell us about yourself..."
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition disabled:bg-gray-100 disabled:text-gray-600 disabled:cursor-not-allowed"
            />
          </div>

          {/* Edit/Save Buttons */}
          <div className="flex gap-4">
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2 rounded-lg transition duration-200"
              >
                Edit Profile
              </button>
            ) : (
              <>
                <button
                  onClick={handleSave}
                  disabled={isSaving}
                  className="bg-green-600 hover:bg-green-700 text-white font-semibold px-6 py-2 rounded-lg transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  onClick={() => {
                    setIsEditing(false);
                    setFullName(user.full_name || '');
                    setBio(user.avatar_url || '');
                  }}
                  className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold px-6 py-2 rounded-lg transition duration-200"
                >
                  Cancel
                </button>
              </>
            )}
          </div>
        </div>

        {/* Danger Zone */}
        <div className="bg-white rounded-lg shadow p-8 border-l-4 border-red-500">
          <h3 className="text-xl font-bold text-red-600 mb-4">Danger Zone</h3>
          <p className="text-gray-600 mb-4">
            Deleting your account will permanently remove all your data and cannot be undone.
          </p>
          <button className="bg-red-600 hover:bg-red-700 text-white font-semibold px-6 py-2 rounded-lg transition duration-200">
            Delete Account
          </button>
        </div>
      </main>
    </div>
  );
}
