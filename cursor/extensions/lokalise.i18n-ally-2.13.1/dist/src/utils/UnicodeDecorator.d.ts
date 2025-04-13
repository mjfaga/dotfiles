declare const fonts: {
    plain: string;
    math_monospace: string;
    math_sans: string;
    math_sans_bold: string;
    math_sans_italic: string;
    math_sans_bold_italic: string;
    regional_indicator: string;
};
export declare type FontNames = keyof typeof fonts;
export declare function unicodeTransform(text: string, from: FontNames, to: FontNames): string;
export declare function unicodeDecorate(text: string, to: FontNames): string;
export declare function decorateLocale(locale: string): string;
export {};
