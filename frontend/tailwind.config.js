/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Ice/Snow
        'white': '#FFFFFF',
        'snow': '#F8FAFB',
        'frost': '#F0F4F7',
        
        // Nordic Blue
        'glacier-blue': '#4A90E2',
        'deep-ice': '#2E5C8A',
        'arctic': '#E8F2F9',
        
        // Functional
        'critical': '#E74C3C',
        'warning': '#F39C12',
        'success': '#27AE60',
        'info': '#3498DB',
        
        // Text
        'text-primary': '#2C3E50',
        'text-secondary': '#5D6D7E',
        'text-tertiary': '#95A5A6',
      },
      spacing: {
        'tight': '8px',
        'normal': '16px',
        'comfortable': '24px',
        'generous': '32px',
        'section': '48px',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 1px 3px rgba(0, 0, 0, 0.08)',
        'card-hover': '0 4px 12px rgba(0, 0, 0, 0.12)',
      },
    },
  },
  plugins: [],
}
