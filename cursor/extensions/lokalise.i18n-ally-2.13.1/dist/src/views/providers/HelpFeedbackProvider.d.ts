import { TreeItem, ExtensionContext, TreeDataProvider, Command } from 'vscode';
import { FeedbackItem } from '../items/FeedbackItem';
export interface FeedbackItemDefintion {
    text: string;
    desc?: string;
    icon: string;
    url?: string;
    command?: Command;
}
export declare class HelpFeedbackProvider implements TreeDataProvider<FeedbackItem> {
    private ctx;
    constructor(ctx: ExtensionContext);
    getTreeItem(element: FeedbackItem): TreeItem;
    getChildren(element?: FeedbackItem): Promise<FeedbackItem[]>;
}
