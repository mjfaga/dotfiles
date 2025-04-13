import { ExtensionContext, TreeItem } from 'vscode';
export declare abstract class BaseTreeItem extends TreeItem {
    readonly ctx: ExtensionContext;
    private _label;
    constructor(ctx: ExtensionContext);
    getChildren(): Promise<BaseTreeItem[]>;
    protected getLabel(): string;
    protected setLabel(value: string): void;
    get label(): string;
    set label(v: string);
    getIcon(name: string, themed?: boolean): string | {
        light: string;
        dark: string;
    };
    getFlagIcon(locale: string): string | undefined;
}
