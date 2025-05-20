import React from 'react';

interface LoadingProps {
  size?: 'small' | 'medium' | 'large';
  message?: string;
}

const Loading: React.FC<LoadingProps> = ({ size = 'medium', message = 'Laden...' }) => {
  const getSizeClass = () => {
    switch (size) {
      case 'small':
        return 'w-6 h-6';
      case 'large':
        return 'w-12 h-12';
      case 'medium':
      default:
        return 'w-8 h-8';
    }
  };
  
  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className={`${getSizeClass()} border-4 border-gray-300 border-t-primary-500 rounded-full animate-spin`}></div>
      {message && (
        <p className="mt-3 text-gray-600 dark:text-gray-300">{message}</p>
      )}
    </div>
  );
};

export default Loading; 