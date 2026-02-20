export const palette = {
    // Brand Colors
    magenta: '#FF0080',
    purple: '#7928CA',
    violet: '#8908CC',
    cyan: '#08B8CC',
    fuchsia: '#CC0884',
    lime: '#A0D800',

    // Neutrals Light
    text: '#252F40',
    textMuted: '#67748E',
    textSoft: '#8392AB',
    border: '#E9ECEF',
    background: '#F8F9FA',
    surface: '#FFFFFF',

    // Neutrals Dark
    darkBackground: '#0B1020',
    darkSurface: '#141B2D',
    darkSurfaceAlt: '#1B2438',
    darkText: '#E6EAF2',
    darkTextMuted: '#B7C0D0',
    darkBorder: '#24324A',

    // System
    error: '#EA0606',
    success: '#2DCE89',
    white: '#FFFFFF',
    black: '#000000',
};

export const lightTheme = {
    mode: 'light',
    colors: {
        primary: palette.magenta,
        secondary: palette.purple,
        accent: palette.cyan,
        success: palette.fuchsia,
        background: palette.background,
        surface: palette.surface,
        surfaceAlt: '#F1F3F7',
        text: palette.text,
        textMuted: palette.textMuted,
        textSoft: palette.textSoft,
        border: palette.border,
        icon: '#56606A',
        shadow: '#000000', // Use solid black for shadow color
    }
};

export const darkTheme = {
    mode: 'dark',
    colors: {
        primary: palette.magenta,
        secondary: palette.purple,
        accent: palette.cyan,
        success: palette.fuchsia,
        background: '#101828', // Dropdown y similares de colores2
        surface: '#1C293A',    // Slightly lighter for definition
        surfaceAlt: '#252F40', // Titulo modulo de colores2
        text: '#FFFFFF',       // Fondo modulos de colores2
        textMuted: '#E5E7EB',  // Borde de modulos de colores2
        textSoft: '#8C8C8C',   // Subtitulo de legajo de colores2
        border: '#4A5565',     // Texto general menu lateral de colores2
        icon: '#56606A',       // Iconos de colores2
        shadow: '#000000',
    }
};
