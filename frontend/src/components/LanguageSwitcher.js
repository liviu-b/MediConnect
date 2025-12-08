import { useTranslation } from 'react-i18next';

const LanguageSwitcher = () => {
  const { i18n } = useTranslation();

  const languages = [
    { code: 'en', name: 'EN', flag: '🇬🇧' },
    { code: 'ro', name: 'RO', flag: '🇷🇴' }
  ];

  const currentLang = i18n.language?.split('-')[0] || 'en';

  return (
    <div className="flex items-center space-x-1 bg-gray-100 rounded-lg p-1">
      {languages.map((lang) => (
        <button
          key={lang.code}
          onClick={() => i18n.changeLanguage(lang.code)}
          data-testid={`lang-${lang.code}`}
          className={`flex items-center space-x-1 px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
            currentLang === lang.code
              ? 'bg-white shadow-sm text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <span>{lang.flag}</span>
          <span>{lang.name}</span>
        </button>
      ))}
    </div>
  );
};

export default LanguageSwitcher;
