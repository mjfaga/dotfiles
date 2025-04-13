import { TreeItem, ExtensionContext, TreeDataProvider, Event } from 'vscode';
import { LocaleTreeItem } from '../items/LocaleTreeItem';
import { Loader, LocaleTree, LocaleNode } from '~/core';
export declare class LocalesTreeProvider implements TreeDataProvider<LocaleTreeItem> {
    readonly ctx: ExtensionContext;
    includePaths?: string[] | undefined;
    protected loader: Loader;
    protected name: string;
    private _flatten;
    private _onDidChangeTreeData;
    readonly onDidChangeTreeData: Event<LocaleTreeItem | undefined>;
    constructor(ctx: ExtensionContext, includePaths?: string[] | undefined, flatten?: boolean);
    protected refresh(): void;
    getTreeItem(element: LocaleTreeItem): TreeItem;
    get flatten(): boolean;
    set flatten(value: boolean);
    private filter;
    protected filterNodes(nodes: (LocaleTree | LocaleNode)[]): (LocaleNode | LocaleTree)[];
    protected getRoots(): LocaleTreeItem[];
    sort(elements: LocaleTreeItem[]): LocaleTreeItem[];
    getChildren(element?: LocaleTreeItem): Promise<LocaleTreeItem[]>;
}
