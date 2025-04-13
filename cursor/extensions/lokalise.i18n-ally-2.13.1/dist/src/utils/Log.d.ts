import { OutputChannel } from 'vscode';
export declare class Log {
    private static _channel;
    static get outputChannel(): OutputChannel;
    static raw(...values: any[]): void;
    static info(message: string, indent?: number): void;
    static warn(message: string, prompt?: boolean, indent?: number): void;
    static error(err?: Error | string | any, prompt?: boolean, indent?: number): Promise<void>;
    static show(): void;
    static divider(): void;
}
