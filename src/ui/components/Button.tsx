import React from 'react';

/**
 * 按钮组件属性接口
 * @interface ButtonProps
 * @property {React.ReactNode} children - 按钮文本或内容
 * @property {() => void} [onClick] - 点击事件处理函数
 * @property {boolean} [disabled=false] - 是否禁用按钮
 * @property {'primary' | 'secondary' | 'danger'} [variant='primary'] - 按钮变体
 */
interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'danger';
}

/**
 * 按钮组件
 * 
 * @component
 * @description 提供基础的按钮交互功能，支持多种变体和状态
 * @example
 * ```tsx
 * // 主要按钮
 * <Button onClick={() => console.log('点击')} variant="primary">
 *   主要按钮
 * </Button>
 * 
 * // 禁用按钮
 * <Button disabled variant="secondary">
 *   禁用按钮
 * </Button>
 * 
 * // 危险操作按钮
 * <Button variant="danger">
 *   危险操作
 * </Button>
 * ```
 * 
 * @param {ButtonProps} props - 按钮属性
 * @returns {JSX.Element} 渲染按钮元素
 */
const Button: React.FC<ButtonProps> = ({ 
  children, 
  onClick, 
  disabled = false,
  variant = 'primary'
}) => {
  return (
    <button 
      data-testid="button"
      className={`button button--${variant}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};

export default Button;
