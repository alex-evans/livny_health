import { cn } from '../../utils/cn';

interface InputProps {
  type?: 'text' | 'email' | 'password' | 'search' | 'number';
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  disabled?: boolean;
  className?: string;
  id?: string;
  name?: string;
  autoFocus?: boolean;
  autoComplete?: string;
}

export function Input({
  type = 'text',
  placeholder,
  value,
  onChange,
  disabled = false,
  className,
  id,
  name,
  autoFocus,
  autoComplete,
}: InputProps) {
  return (
    <input
      type={type}
      id={id}
      name={name}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      disabled={disabled}
      autoFocus={autoFocus}
      autoComplete={autoComplete}
      className={cn(
        'w-full bg-white border border-arctic rounded-md px-normal py-3 text-[15px] text-text-primary',
        'placeholder:text-text-tertiary',
        'transition-all duration-200',
        'focus:outline-none focus:border-glacier-blue focus:ring-[3px] focus:ring-glacier-blue/10',
        'disabled:bg-frost disabled:text-text-tertiary disabled:cursor-not-allowed',
        className
      )}
    />
  );
}
