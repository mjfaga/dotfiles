import { ExtensionContext, Range, TextDocument, TreeItemCollapsibleState } from 'vscode';
import { BaseTreeItem } from './Base';
import { DetectionResult } from '~/core/types';
import { ExtractTextOptions } from '~/commands/extractString';
export declare class HardStringDetectResultItem extends BaseTreeItem implements ExtractTextOptions {
    readonly ctx: ExtensionContext;
    readonly detection: DetectionResult;
    collapsibleState: TreeItemCollapsibleState;
    text: string;
    isDynamic?: boolean;
    range: Range;
    rawText?: string;
    args?: string[];
    document: TextDocument;
    isInsert?: boolean | undefined;
    constructor(ctx: ExtensionContext, detection: DetectionResult);
}
