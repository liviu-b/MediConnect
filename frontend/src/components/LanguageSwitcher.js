import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';

const LanguageSwitcher = ({ compact = false }) => {
  const { i18n } = useTranslation();

  const toggleLanguage = () => {
    const newLang = i18n.language === 'en' ? 'ro' : 'en';
    i18n.changeLanguage(newLang);
    localStorage.setItem('language', newLang);
  };

  return (
    <button
      onClick={toggleLanguage}
      className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all text-sm font-medium text-gray-700 hover:text-blue-600 ${
        compact ? 'px-2' : ''
      }`}
      title={i18n.language === 'en' ? 'Switch to Romanian' : 'Switch to English'}
    >
      <Globe className="w-4 h-4" />
      <span className="uppercase">{i18n.language}</span>
    </button>
  );
};

export default LanguageSwitcher;
