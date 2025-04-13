import { TreeItemCollapsibleState } from 'vscode';
import { LocaleTreeItem } from './LocaleTreeItem';
import { ProgressBaseItem } from './ProgressBaseItem';
import { ProgressRootItem } from './ProgressRootItem';
export declare abstract class ProgressSubmenuItem extends ProgressBaseItem {
    protected root: ProgressRootItem;
    readonly labelKey: string;
    readonly icon?: string | undefined;
    constructor(root: ProgressRootItem, labelKey: string, icon?: string | undefined);
    get iconPath(): string | {
        light: string;
        dark: string;
    } | undefined;
    getLabel(): string;
    getSuffix(): string;
    abstract getKeys(): string[];
    get collapsibleState(): TreeItemCollapsibleState.None | TreeItemCollapsibleState.Collapsed;
    set collapsibleState(_: TreeItemCollapsibleState);
    getChildren(): Promise<LocaleTreeItem[]>;
}
