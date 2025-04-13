/**
 * 'foo' + bar() + ' is cool' -> `foo${bar()} is cool`
 */
export declare function stringConcatenationToTemplate(text: string): string;
export declare function parseHardString(text?: string, languageId?: string, isDynamic?: boolean): {
    trimmed: string;
    text: string;
    args: string[];
} | null;
