import typography from "@tailwindcss/typography";

// tailwind.config.ts
module.exports = {
  theme: {
    extend: {
      typography: ({ theme }) => ({
        DEFAULT: {
          css: {
            strong: {
              fontWeight: "700",
              color: theme("colors.primary.DEFAULT"), // make bold text stand out with primary color
            },
            h2: {
              fontSize: theme("fontSize.xl"),
              marginTop: theme("spacing.6"),
              marginBottom: theme("spacing.2"),
            },
            ul: {
              paddingLeft: theme("spacing.6"),
            },
            // any other customizations...
          },
        },
      }),
    },
  },
  plugins: [typography],
};
