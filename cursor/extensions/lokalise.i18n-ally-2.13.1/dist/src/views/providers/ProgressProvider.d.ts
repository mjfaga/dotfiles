import { TreeItem, ExtensionContext, TreeDataProvider, Event } from 'vscode';
import { BaseTreeItem } from '../items/Base';
export declare class ProgressProvider implements TreeDataProvider<BaseTreeItem> {
    private ctx;
    protected name: string;
    private _onDidChangeTreeData;
    readonly onDidChangeTreeData: Event<BaseTreeItem | undefined>;
    constructor(ctx: ExtensionContext);
    refresh(): void;
    getTreeItem(element: BaseTreeItem): TreeItem;
    getChildren(element?: BaseTreeItem): Promise<BaseTreeItem[]>;
}
