import { TreeItemCollapsibleState } from 'vscode';
import { CurrentFileLocalesTreeProvider } from '../providers';
import { BaseTreeItem } from './Base';
import { LocaleTreeItem } from '.';
export declare class CurrentFileInUseItem extends BaseTreeItem {
    readonly provider: CurrentFileLocalesTreeProvider;
    constructor(provider: CurrentFileLocalesTreeProvider);
    get iconPath(): string | {
        light: string;
        dark: string;
    };
    getLabel(): string;
    get description(): string;
    getKeys(): string[];
    get collapsibleState(): TreeItemCollapsibleState.None | TreeItemCollapsibleState.Expanded;
    set collapsibleState(_: TreeItemCollapsibleState);
    getChildren(): Promise<LocaleTreeItem[]>;
}
