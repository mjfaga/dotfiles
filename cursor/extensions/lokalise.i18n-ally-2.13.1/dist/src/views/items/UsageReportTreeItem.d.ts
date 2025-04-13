import { ExtensionContext, TreeItemCollapsibleState } from 'vscode';
import { LocaleTreeItem } from '.';
import { KeyUsage } from '~/core';
export declare class UsageReportTreeItem extends LocaleTreeItem {
    readonly usage: KeyUsage;
    readonly type: string;
    constructor(ctx: ExtensionContext, usage: KeyUsage, type: string);
    get length(): number;
    get label(): string;
    set label(_: string);
    get contextValue(): string;
    get collapsibleState(): TreeItemCollapsibleState.None | TreeItemCollapsibleState.Collapsed;
    set collapsibleState(_: TreeItemCollapsibleState);
}
