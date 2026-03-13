/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Legal professional color palette (律师/法官专业配色)
        claude: {
          // Light mode colors (浅色模式)
          bg: '#FAF8F5',              // Warm white background
          surface: '#FFFFFF',          // Cards, inputs
          surfaceHover: '#F0EBE4',     // Hover state
          surfaceMuted: '#F5F2EE',     // Subtle area distinction
          surfaceInset: '#EBE6DE',     // Inset areas (e.g., input inner)
          border: '#E0D8CC',           // Default border
          borderLight: '#EBE6DE',      // Subtle dividers
          text: '#2C2416',             // Primary text
          textSecondary: '#6B5E4F',    // Secondary text
          // Dark mode colors (暗色模式)
          darkBg: '#1A1612',           // Dark background
          darkSurface: '#2A2420',      // Dark cards
          darkSurfaceHover: '#3A322C', // Dark hover
          darkSurfaceMuted: '#221E1A', // Subtle dark area
          darkSurfaceInset: '#141210', // Dark inset areas
          darkBorder: '#4A4038',       // Dark borders
          darkBorderLight: '#352E28',  // Subtle dark dividers
          darkText: '#F0EDE8',         // Dark primary text
          darkTextSecondary: '#A39B8C', // Dark secondary text
          // Accent (法律专业金棕色)
          accent: '#8B5A2B',           // Deep golden brown (light mode)
          accentHover: '#6B4423',      // Accent hover
          accentLight: '#A67C52',      // Light accent
          accentMuted: 'rgba(139,90,43,0.10)', // Very faint accent background
          // Dark mode accent (暗色模式强调色 - 金色)
          darkAccent: '#C9A962',       // Gold (dark mode)
          darkAccentHover: '#B8954F',  // Gold hover
          darkAccentLight: '#D4B87A',  // Light gold
        },
        primary: {
          DEFAULT: '#8B5A2B',
          dark: '#C9A962'
        },
        secondary: {
          DEFAULT: '#6B5E4F',
          dark: '#4A4038'
        }
      },
      boxShadow: {
        subtle: '0 1px 2px rgba(0,0,0,0.05)',
        card: '0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04)',
        elevated: '0 4px 12px rgba(0,0,0,0.1), 0 1px 3px rgba(0,0,0,0.04)',
        modal: '0 8px 30px rgba(0,0,0,0.16), 0 2px 8px rgba(0,0,0,0.08)',
        popover: '0 4px 20px rgba(0,0,0,0.12), 0 1px 4px rgba(0,0,0,0.05)',
        'glow-accent': '0 0 20px rgba(59,130,246,0.15)',
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in-down': {
          '0%': { opacity: '0', transform: 'translateY(-8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'scale-in': {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.2s ease-out',
        'fade-in-up': 'fade-in-up 0.25s ease-out',
        'fade-in-down': 'fade-in-down 0.2s ease-out',
        'scale-in': 'scale-in 0.2s ease-out',
        shimmer: 'shimmer 1.5s infinite',
      },
      transitionTimingFunction: {
        smooth: 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
      typography: {
        DEFAULT: {
          css: {
            color: '#2C2416',
            a: {
              color: '#8B5A2B',
              '&:hover': {
                color: '#6B4423',
              },
            },
            code: {
              color: '#2C2416',
              backgroundColor: 'rgba(224, 216, 204, 0.5)',
              padding: '0.2em 0.4em',
              borderRadius: '0.25rem',
              fontWeight: '400',
            },
            'code::before': {
              content: '""',
            },
            'code::after': {
              content: '""',
            },
            pre: {
              backgroundColor: '#F0EBE4',
              color: '#2C2416',
              padding: '1em',
              borderRadius: '0.75rem',
              overflowX: 'auto',
            },
            blockquote: {
              borderLeftColor: '#8B5A2B',
              color: '#6B5E4F',
            },
            h1: {
              color: '#2C2416',
            },
            h2: {
              color: '#2C2416',
            },
            h3: {
              color: '#2C2416',
            },
            h4: {
              color: '#2C2416',
            },
            strong: {
              color: '#2C2416',
            },
          },
        },
        dark: {
          css: {
            color: '#F0EDE8',
            a: {
              color: '#C9A962',
              '&:hover': {
                color: '#D4B87A',
              },
            },
            code: {
              color: '#F0EDE8',
              backgroundColor: 'rgba(74, 64, 56, 0.5)',
              padding: '0.2em 0.4em',
              borderRadius: '0.25rem',
              fontWeight: '400',
            },
            pre: {
              backgroundColor: '#2A2420',
              color: '#F0EDE8',
              padding: '1em',
              borderRadius: '0.75rem',
              overflowX: 'auto',
            },
            blockquote: {
              borderLeftColor: '#C9A962',
              color: '#A39B8C',
            },
            h1: {
              color: '#F0EDE8',
            },
            h2: {
              color: '#F0EDE8',
            },
            h3: {
              color: '#F0EDE8',
            },
            h4: {
              color: '#F0EDE8',
            },
            strong: {
              color: '#F0EDE8',
            },
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
