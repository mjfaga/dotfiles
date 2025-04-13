import { WebviewPanel, ViewColumn, ExtensionContext } from 'vscode';
import { KeyInDocument } from '~/core';
export declare class EditorContext {
    filepath?: string;
    keys?: KeyInDocument[];
}
export declare class EditorPanel {
    /**
     * Track the currently panel. Only allow a single panel to exist at a time.
     */
    static currentPanel: EditorPanel | undefined;
    private static _onDidChanged;
    static onDidChange: import("vscode").Event<boolean>;
    private readonly _panel;
    private readonly _protocol;
    private readonly _ctx;
    private _disposables;
    private _editing_key;
    private _mode;
    get mode(): "standalone" | "currentFile";
    set mode(v: "standalone" | "currentFile");
    static createOrShow(ctx: ExtensionContext, column?: ViewColumn): EditorPanel;
    static revive(ctx: ExtensionContext, panel?: WebviewPanel, column?: ViewColumn): EditorPanel;
    private constructor();
    private reveal;
    setContext(context?: EditorContext): void;
    sendCurrentFileContext(): boolean;
    openKey(keypath: string, locale?: string, index?: number): void;
    navigateKey(data: KeyInDocument & {
        filepath: string;
        keyIndex: number;
    }): Promise<void>;
    dispose(): void;
    init(): void;
    get visible(): boolean;
}
