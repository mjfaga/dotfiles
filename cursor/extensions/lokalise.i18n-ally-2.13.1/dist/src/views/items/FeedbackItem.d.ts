import { ExtensionContext } from 'vscode';
import { FeedbackItemDefintion } from '../providers';
import { BaseTreeItem } from './Base';
export declare class FeedbackItem extends BaseTreeItem {
    constructor(ctx: ExtensionContext, define: FeedbackItemDefintion);
}
