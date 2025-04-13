import { ExtensionContext, TreeItemCollapsibleState, Command } from 'vscode';
import { BaseTreeItem } from './Base';
import { Node } from '~/core';
export declare class LocaleTreeItem extends BaseTreeItem {
    flatten: boolean;
    readonly displayLocale?: string | undefined;
    readonly listedLocales?: string[] | undefined;
    readonly node: Node;
    constructor(ctx: ExtensionContext, node: Node, flatten?: boolean, displayLocale?: string | undefined, listedLocales?: string[] | undefined);
    get tooltip(): string;
    getLabel(): string;
    get collapsibleState(): TreeItemCollapsibleState.None | TreeItemCollapsibleState.Collapsed;
    set collapsibleState(_: TreeItemCollapsibleState);
    get description(): string;
    get iconPath(): string | {
        light: string;
        dark: string;
    } | undefined;
    get contextValue(): string;
    get editorMode(): boolean;
    getChildren(filter?: (node: Node) => boolean): Promise<LocaleTreeItem[]>;
    get command(): Command | undefined;
}
