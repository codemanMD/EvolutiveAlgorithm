/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        'cyberpunk-pink': '#FF00FF',
        'cyberpunk-blue': '#00FFFF',
        'cyberpunk-yellow': '#FFFF00',
        'cyberpunk-green': '#00FF00',
      },
      fontFamily: {
        'cyberpunk': ['" futuristic"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
