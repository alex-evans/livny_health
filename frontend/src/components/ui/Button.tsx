import { cn } from '../../utils/cn';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  onClick?: () => void;
  children: React.ReactNode;
  className?: string;
}

export function Button({
  variant = 'primary',
  size = 'md',
  disabled = false,
  type = 'button',
  onClick,
  children,
  className,
}: ButtonProps) {
  const baseStyles = 'font-medium rounded-md transition-all duration-150 ease-out focus:outline-none focus:ring-2 focus:ring-offset-2';

  const variants = {
    primary: 'bg-glacier-blue text-white shadow-[0_2px_4px_rgba(74,144,226,0.2)] hover:bg-[#3A7BC8] hover:shadow-[0_4px_8px_rgba(74,144,226,0.3)] focus:ring-glacier-blue disabled:bg-glacier-blue/50 disabled:shadow-none',
    secondary: 'bg-white text-glacier-blue border border-arctic hover:bg-frost focus:ring-glacier-blue disabled:text-glacier-blue/50',
    danger: 'bg-critical text-white hover:bg-[#C0392B] focus:ring-critical disabled:bg-critical/50',
  };

  const sizes = {
    sm: 'px-4 py-2 text-[13px]',
    md: 'px-6 py-3 text-[15px]',
    lg: 'px-8 py-4 text-[15px]',
  };

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={cn(baseStyles, variants[variant], sizes[size], className)}
    >
      {children}
    </button>
  );
}
