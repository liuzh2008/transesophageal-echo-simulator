import React, { createContext, useContext, useState } from 'react';

/**
 * 主题配置类型定义
 */
interface Theme {
  primaryColor: string;
  secondaryColor: string;
  backgroundColor: string;
  textColor: string;
  borderRadius: string;
  spacing: {
    small: string;
    medium: string;
    large: string;
  };
}

/**
 * 主题上下文
 */
interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

/**
 * 默认主题配置
 */
const defaultTheme: Theme = {
  primaryColor: '#007bff',
  secondaryColor: '#6c757d',
  backgroundColor: '#ffffff',
  textColor: '#333333',
  borderRadius: '4px',
  spacing: {
    small: '8px',
    medium: '16px',
    large: '24px'
  }
};

/**
 * 主题提供者组件
 */
interface ThemeProviderProps {
  children: React.ReactNode;
  initialTheme?: Theme;
}

const ThemeProvider: React.FC<ThemeProviderProps> = ({ 
  children, 
  initialTheme = defaultTheme 
}) => {
  const [theme, setTheme] = useState<Theme>(initialTheme);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

/**
 * 使用主题的钩子
 */
export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export default ThemeProvider;
