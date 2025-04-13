export default class i18n {
    static language: string;
    static messages: Record<string, string>;
    static init(extensionPath: string): void;
    static format(str: string, args: any[]): string;
    static t(key: string, ...args: any[]): string;
}
