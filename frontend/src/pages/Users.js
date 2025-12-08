import { useTranslation } from 'react-i18next';
import { Users as UsersIcon } from 'lucide-react';

const Users = () => {
  const { t } = useTranslation();

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
