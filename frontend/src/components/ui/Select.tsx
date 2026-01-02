import { cn } from '../../utils/cn';

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps {
  options: SelectOption[];
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  id?: string;
  name?: string;
}

export function Select({
  options,
  value,
  onChange,
  placeholder = 'Select an option',
  disabled = false,
  className,
  id,
  name,
}: SelectProps) {
  return (
    <select
      id={id}
      name={name}
      value={value}
      onChange={(e) => onChange?.(e.target.value)}
      disabled={disabled}
      className={cn(
        'w-full bg-white border border-arctic rounded-md px-normal py-3 text-[15px] text-text-primary',
        'transition-all duration-200',
        'focus:outline-none focus:border-glacier-blue focus:ring-[3px] focus:ring-glacier-blue/10',
        'disabled:bg-frost disabled:text-text-tertiary disabled:cursor-not-allowed',
        'appearance-none cursor-pointer',
        'bg-[url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 fill=%27none%27 viewBox=%270 0 24 24%27 stroke=%27%236B7280%27%3E%3Cpath stroke-linecap=%27round%27 stroke-linejoin=%27round%27 stroke-width=%272%27 d=%27M19 9l-7 7-7-7%27/%3E%3C/svg%3E")] bg-[length:20px] bg-[right_12px_center] bg-no-repeat',
        !value && 'text-text-tertiary',
        className
      )}
    >
      <option value="" disabled>
        {placeholder}
      </option>
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}
