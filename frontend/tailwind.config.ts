import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F5F2EA",
        espresso: "#2C1208",
        primary: {
          DEFAULT: "#1B6040",
          foreground: "#FFFFFF",
          50: "#E6F2EB",
          100: "#BEDFC9",
          200: "#8ECAAB",
          300: "#5CB48C",
          400: "#379E71",
          500: "#1B6040",
          600: "#154D33",
          700: "#0F3925",
          800: "#092618",
          900: "#031208",
        },
        secondary: {
          DEFAULT: "#22C55E",
          foreground: "#FFFFFF",
        },
        accent: {
          DEFAULT: "#1B3020",
          foreground: "#FFFFFF",
          50: "#E6EDE9",
          100: "#BECEC5",
          200: "#8EAD9E",
          300: "#5E8C77",
          400: "#377158",
          500: "#1B3020",
          600: "#15261A",
          700: "#0F1C12",
          800: "#09130C",
          900: "#030906",
        },
        dark: "#1E1E1E",
        card: {
          DEFAULT: "#FFFFFF",
          foreground: "#1E1E1E",
        },
        success: "#22C55E",
        muted: {
          DEFAULT: "#E8F5ED",
          foreground: "#4B6D57",
        },
        border: "#C0DBC9",
        input: "#C0DBC9",
        ring: "#1B6040",
        destructive: {
          DEFAULT: "#DC2626",
          foreground: "#FFFFFF",
        },
      },
      fontFamily: {
        heading: ["Lora", "Georgia", "serif"],
        body: ["Raleway", "system-ui", "sans-serif"],
        sans: ["Raleway", "system-ui", "sans-serif"],
      },
      borderRadius: {
        lg: "0.75rem",
        md: "0.5rem",
        sm: "0.375rem",
        xl: "1rem",
        "2xl": "1.5rem",
        "3xl": "2rem",
      },
      boxShadow: {
        soft: "0 2px 15px rgba(27, 96, 64, 0.08)",
        card: "0 4px 24px rgba(27, 96, 64, 0.10)",
        elevated: "0 8px 40px rgba(27, 96, 64, 0.15)",
        glow: "0 0 30px rgba(27, 96, 64, 0.20)",
      },
      backgroundImage: {
        "warm-gradient": "linear-gradient(135deg, #F5F2EA 0%, #EAF5EE 100%)",
        "card-gradient": "linear-gradient(135deg, #FFFFFF 0%, #F5F2EA 100%)",
        "hero-pattern": "radial-gradient(circle at 20% 50%, rgba(27,96,64,0.08) 0%, transparent 60%), radial-gradient(circle at 80% 20%, rgba(34,197,94,0.12) 0%, transparent 50%)",
      },
      animation: {
        "float": "float 6s ease-in-out infinite",
        "float-delay": "float 6s ease-in-out 2s infinite",
        "float-delay-2": "float 6s ease-in-out 4s infinite",
        "counter": "counter 1s ease-out forwards",
        "slide-up": "slideUp 0.5s ease-out forwards",
        "fade-in": "fadeIn 0.6s ease-out forwards",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-20px)" },
        },
        slideUp: {
          from: { opacity: "0", transform: "translateY(20px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
