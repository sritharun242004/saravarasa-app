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
        // ── Organic / Natural palette — forest floor, clay, unbleached paper ──
        background: "#FDFCF8", // Rice paper
        espresso: "#2C2C24", // Deep loam (dark surfaces)
        foreground: "#2C2C24",
        primary: {
          // Brand green — preserved as the signature colour
          DEFAULT: "#1B6040",
          foreground: "#F3F4F1",
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
          // Terracotta / clay — organic warm contrast
          DEFAULT: "#C18C5D",
          foreground: "#FFFFFF",
        },
        accent: {
          // Moss green — positive / success tone (organic green companion)
          DEFAULT: "#5D7052",
          foreground: "#FFFFFF",
          50: "#EEF0EC",
          100: "#D6DCD1",
          200: "#B7C1AE",
          300: "#97A78B",
          400: "#7A8C6E",
          500: "#5D7052",
          600: "#4A5A42",
          700: "#384432",
          800: "#262E22",
          900: "#141811",
        },
        // Organic surface tones
        sand: "#E6DCCD",
        clay: "#C18C5D",
        stone: "#F0EBE5",
        timber: "#DED8CF",
        dark: "#2C2C24", // Deep loam / charcoal
        card: {
          DEFAULT: "#FEFEFA",
          foreground: "#2C2C24",
        },
        success: "#5D7052",
        muted: {
          DEFAULT: "#F0EBE5", // Stone
          foreground: "#78786C", // Dried grass
        },
        border: "#DED8CF", // Raw timber
        input: "#DED8CF",
        ring: "#5D7052",
        destructive: {
          DEFAULT: "#A85448", // Burnt sienna
          foreground: "#FFFFFF",
        },
      },
      fontFamily: {
        heading: ["Fraunces", "Georgia", "serif"],
        body: ["Nunito", "system-ui", "sans-serif"],
        sans: ["Nunito", "system-ui", "sans-serif"],
      },
      borderRadius: {
        lg: "0.75rem",
        md: "0.5rem",
        sm: "0.375rem",
        xl: "1rem",
        "2xl": "1.5rem",
        "3xl": "2rem",
        "4xl": "2.5rem",
        "5xl": "4rem",
      },
      boxShadow: {
        // Soft, diffused, naturally-tinted shadows — never pure black
        soft: "0 4px 20px -2px rgba(27, 96, 64, 0.15)", // green-tinted
        card: "0 8px 30px -6px rgba(27, 96, 64, 0.12)",
        float: "0 10px 40px -10px rgba(193, 140, 93, 0.22)", // clay-tinted
        elevated: "0 20px 40px -10px rgba(27, 96, 64, 0.15)",
        glow: "0 0 30px rgba(93, 112, 82, 0.20)",
      },
      backgroundImage: {
        "warm-gradient": "linear-gradient(135deg, #FDFCF8 0%, #F0EBE5 100%)",
        "card-gradient": "linear-gradient(135deg, #FEFEFA 0%, #F5F1EA 100%)",
        "hero-pattern": "radial-gradient(circle at 18% 40%, rgba(93,112,82,0.10) 0%, transparent 55%), radial-gradient(circle at 82% 18%, rgba(193,140,93,0.12) 0%, transparent 50%)",
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
