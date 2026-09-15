/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                teal: {
                    DEFAULT: '#087F72',
                    hover: '#066B60',
                    light: '#E6F4F2',
                    badge: '#087F72'
                },
                charcoal: {
                    DEFAULT: '#142626',
                    dark: '#0E1A1A',
                    card: '#1C3333',
                    border: '#244040'
                },
                canvas: {
                    DEFAULT: '#F7F9F9',
                    card: '#FFFFFF',
                    border: '#E2E8E8'
                },
                workbench: {
                    text: '#172B2B',
                    muted: '#637575',
                    subtle: '#8C9C9C'
                }
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                mono: ['"IBM Plex Mono"', 'monospace']
            },
            borderRadius: {
                card: '12px',
                control: '8px'
            }
        },
    },
    plugins: [],
}
