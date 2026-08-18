/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Neutral surfaces — deliberately near-black / near-white rather
        // than pure #000/#fff so elevation reads through shadows, not
        // harsh contrast jumps.
        canvas: {
          light: "#F7F7F8",
          dark: "#0B0D12",
        },
        surface: {
          light: "#FFFFFF",
          dark: "#14171F",
        },
        border: {
          light: "#E5E5E9",
          dark: "#242832",
        },
        ink: {
          light: "#15161A",
          dark: "#EDEEF2",
        },
        muted: {
          light: "#6B6E76",
          dark: "#8A8F9C",
        },
        // Signature accent: violet -> cyan, representing the fusion of
        // text / voice / document modalities into one input. Used
        // sparingly — send button, focus rings, the assistant mark.
        accent: {
          from: "#7C5CFF",
          to: "#22D3EE",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "sans-serif",
        ],
      },
      boxShadow: {
        floating: "0 8px 30px -8px rgba(0,0,0,0.25)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: 0, transform: "translateY(8px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.4s ease-out",
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
};
