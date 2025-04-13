import { TreeDataProvider, ExtensionContext, TreeItem, TreeView } from 'vscode';
export declare class UsageReportProvider implements TreeDataProvider<TreeItem> {
    private ctx;
    private _onDidChangeTreeData;
    readonly onDidChangeTreeData: import("vscode").Event<TreeItem | undefined>;
    private usages;
    view: TreeView<TreeItem> | undefined;
    rootItems: TreeItem[];
    constructor(ctx: ExtensionContext);
    private set;
    refresh(): void;
    getTreeItem(element: TreeItem): TreeItem;
    getChildren(element?: TreeItem): Promise<TreeItem[]>;
    getParent(): null;
}
