import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17212B",
        paper: "#F7F5F0",
        teal: "#1C625C",
      },
    },
  },
  plugins: [],
};

export default config;
