/// <reference types="vscode" />
export interface Message {
    type: string;
    _id?: number;
    keypath?: string;
    locale?: string;
    value?: string;
    route?: string;
    data?: any;
    commentId?: string;
}
export declare class Protocol {
    private readonly _postMessage;
    extendHandler?: ((message: Message) => Thenable<boolean | undefined>) | undefined;
    options?: {
        extendConfig?: any;
    } | undefined;
    ready: boolean;
    pendingMessages: Message[];
    constructor(_postMessage: (message: Message) => Promise<void>, extendHandler?: ((message: Message) => Thenable<boolean | undefined>) | undefined, options?: {
        extendConfig?: any;
    } | undefined);
    get config(): any;
    postMessage(message: Message): Promise<void>;
    updateConfig(): void;
    updateI18nMessages(): void;
    switchToKey(key: string): void;
    handleMessages(message: Message): Promise<void>;
}
