module.exports = {
    content: [
        '../templates/**/*.html',
        '../../templates/**/*.html',
        "./**/*.{js,jsx,ts,tsx}",
        '../../**/templates/**/*.html',
        // ...other patterns if needed
    ],
    theme: {
        extend: {},
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
        require("daisyui"),
    ],
    daisyui: {
        themes: ["light", "dark", "cupcake", "bumblebee"],
    },
}
