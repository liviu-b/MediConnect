import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../App';
import {
  Users as UsersIcon,
  Search,
  Shield,
  User,
  Loader2
} from 'lucide-react';

const Users = () => {
  const { t } = useTranslation();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');

  useEffect(() => {
    // This page might not be accessible to regular users
    // For now, we'll show a simple placeholder
    setLoading(false);
  }, []);

  return (
    <div className="space-y-4">
      <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
        <UsersIcon className="w-12 h-12 mx-auto text-gray-300 mb-3" />
        <p className="text-gray-500">{t('auth.noPermission')}</p>
        <p className="text-sm text-gray-400 mt-1">User management is available for system administrators only</p>
      </div>
    </div>
  );
};

export default Users;
