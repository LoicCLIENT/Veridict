import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      // Veridict Design System Colors
      colors: {
        // Colores base Veridict
        "veridict-green": {
          900: "#1F3329", // Base - Fondos principales
          800: "#2A4435", // Cards elevadas
          700: "#355541", // Hover states
          600: "#40664D", // Bordes activos
          500: "#4B7759", // Texto secundario
        },
        "veridict-lime": {
          DEFAULT: "#C2E94B", // Acento principal
          hover: "#D4F06A",   // Hover en botones lima
          muted: "rgba(194, 233, 75, 0.2)", // Backgrounds sutiles (20% opacity)
        },
        "veridict-white": "#F5F5F0",  // Texto principal
        "veridict-gray": "#A3A99E",   // Texto secundario/muted
        "veridict-error": "#E94B4B",  // Errores

        // Mapping semantico para shadcn/ui
        background: "#1F3329",
        foreground: "#F5F5F0",
        card: {
          DEFAULT: "#2A4435",
          foreground: "#F5F5F0",
        },
        popover: {
          DEFAULT: "#2A4435",
          foreground: "#F5F5F0",
        },
        primary: {
          DEFAULT: "#C2E94B",
          foreground: "#1F3329",
        },
        secondary: {
          DEFAULT: "#355541",
          foreground: "#F5F5F0",
        },
        muted: {
          DEFAULT: "#2A4435",
          foreground: "#A3A99E",
        },
        accent: {
          DEFAULT: "#C2E94B",
          foreground: "#1F3329",
        },
        destructive: {
          DEFAULT: "#E94B4B",
          foreground: "#F5F5F0",
        },
        border: "rgba(255, 255, 255, 0.12)",
        input: "rgba(255, 255, 255, 0.12)",
        ring: "#C2E94B",
      },

      // Border Radius segun Design System
      borderRadius: {
        sm: "6px",   // Botones pequenos, badges
        md: "8px",   // Cards, inputs
        lg: "12px",  // Modales, paneles grandes
        xl: "16px",  // Cards destacadas
      },

      // Font Family segun Design System
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },

      // Escala tipografica
      fontSize: {
        xs: ["0.75rem", { lineHeight: "1rem" }],      // 12px - Labels, captions
        sm: ["0.875rem", { lineHeight: "1.25rem" }],  // 14px - Body secundario
        base: ["1rem", { lineHeight: "1.5rem" }],     // 16px - Body principal
        lg: ["1.125rem", { lineHeight: "1.75rem" }],  // 18px - Subtitulos
        xl: ["1.25rem", { lineHeight: "1.75rem" }],   // 20px - Titulos seccion
        "2xl": ["1.5rem", { lineHeight: "2rem" }],    // 24px - Titulos pagina
        "3xl": ["2rem", { lineHeight: "2.25rem" }],   // 32px - Headlines
        "4xl": ["2.5rem", { lineHeight: "2.5rem" }],  // 40px - Hero solo landing
      },

      // Espaciado sistema 4px base
      spacing: {
        "1": "4px",
        "2": "8px",
        "3": "12px",
        "4": "16px",
        "5": "20px",
        "6": "24px",
        "8": "32px",
        "10": "40px",
        "12": "48px",
        "16": "64px",
      },

      // Sombras sutiles
      boxShadow: {
        sm: "0 1px 2px rgba(0, 0, 0, 0.2)",
        md: "0 4px 12px rgba(0, 0, 0, 0.25)",
        lg: "0 8px 24px rgba(0, 0, 0, 0.3)",
      },

      // Transiciones
      transitionDuration: {
        fast: "150ms",
        base: "200ms",
        slow: "300ms",
      },

      // Max width para container
      maxWidth: {
        container: "1280px",
      },

      // Animaciones personalizadas
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "slide-up": {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "slide-down": {
          "0%": { opacity: "0", transform: "translateY(-10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "scale-in": {
          "0%": { opacity: "0", transform: "scale(0.95)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        "pulse-lime": {
          "0%, 100%": {
            boxShadow: "0 0 0 0 rgba(194, 233, 75, 0.4)",
            borderColor: "rgba(194, 233, 75, 0.6)"
          },
          "50%": {
            boxShadow: "0 0 0 8px rgba(194, 233, 75, 0)",
            borderColor: "rgba(194, 233, 75, 1)"
          },
        },
        "pulse-soft": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.6" },
        },
        "spin-slow": {
          "0%": { transform: "rotate(0deg)" },
          "100%": { transform: "rotate(360deg)" },
        },
        "thinking-dots": {
          "0%, 80%, 100%": { transform: "scale(0.6)", opacity: "0.5" },
          "40%": { transform: "scale(1)", opacity: "1" },
        },
        "ripple": {
          "0%": { transform: "scale(0.8)", opacity: "1" },
          "100%": { transform: "scale(2.4)", opacity: "0" },
        },
        "glow": {
          "0%, 100%": { filter: "brightness(1)" },
          "50%": { filter: "brightness(1.3)" },
        },
      },
      animation: {
        "fade-in": "fade-in 200ms ease",
        "slide-up": "slide-up 300ms ease",
        "slide-down": "slide-down 300ms ease",
        "scale-in": "scale-in 200ms ease",
        "pulse-lime": "pulse-lime 2s ease-in-out infinite",
        "pulse-soft": "pulse-soft 2s ease-in-out infinite",
        "spin-slow": "spin-slow 3s linear infinite",
        "thinking-dots": "thinking-dots 1.4s ease-in-out infinite",
        "ripple": "ripple 1.5s ease-out infinite",
        "glow": "glow 2s ease-in-out infinite",
      },

      // Background images para gradientes con ruido
      backgroundImage: {
        "gradient-hero":
          "radial-gradient(ellipse 80% 50% at 50% -20%, rgba(42, 68, 53, 0.5) 0%, transparent 50%), " +
          "radial-gradient(ellipse 60% 40% at 100% 100%, rgba(53, 85, 65, 0.125) 0%, transparent 40%), " +
          "#1F3329",
      },
    },
  },
  plugins: [],
};

export default config;
