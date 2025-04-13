import { ExtensionContext, TreeItemCollapsibleState } from 'vscode';
import { BaseTreeItem } from './Base';
import { Coverage } from '~/core';
export declare abstract class ProgressBaseItem extends BaseTreeItem {
    readonly ctx: ExtensionContext;
    readonly node: Coverage;
    constructor(ctx: ExtensionContext, node: Coverage);
    getLabel(): string;
    collapsibleState: TreeItemCollapsibleState;
}
