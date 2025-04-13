import { ExtensionContext, TreeDataProvider, TreeItem, Event } from 'vscode';
import { BaseTreeItem } from '../items/Base';
export declare class CurrentFileLocalesTreeProvider implements TreeDataProvider<BaseTreeItem> {
    ctx: ExtensionContext;
    protected name: string;
    private _onDidChangeTreeData;
    readonly onDidChangeTreeData: Event<BaseTreeItem | undefined>;
    private _pathsNotFound;
    private _pathsInUse;
    paths: string[];
    pathsExists: string[];
    constructor(ctx: ExtensionContext);
    getTreeItem(element: BaseTreeItem): TreeItem;
    getChildren(element?: BaseTreeItem): Promise<BaseTreeItem[]>;
    protected refresh(): void;
    loadCurrentDocument(): void;
    get pathsInUse(): string[];
    get pathsNotFound(): string[];
    updatePathsExists(): void;
}
