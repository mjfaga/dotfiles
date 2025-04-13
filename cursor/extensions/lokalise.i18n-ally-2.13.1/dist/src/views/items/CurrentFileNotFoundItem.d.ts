import { TreeItemCollapsibleState } from 'vscode';
import { CurrentFileLocalesTreeProvider } from '../providers';
import { BaseTreeItem } from './Base';
import { LocaleTreeItem } from '.';
export declare class CurrentFileNotFoundItem extends BaseTreeItem {
    provider: CurrentFileLocalesTreeProvider;
    constructor(provider: CurrentFileLocalesTreeProvider);
    get iconPath(): string | {
        light: string;
        dark: string;
    };
    get description(): string;
    getLabel(): string;
    getKeys(): string[];
    get collapsibleState(): TreeItemCollapsibleState.None | TreeItemCollapsibleState.Collapsed;
    set collapsibleState(_: TreeItemCollapsibleState);
    getChildren(): Promise<LocaleTreeItem[]>;
}
