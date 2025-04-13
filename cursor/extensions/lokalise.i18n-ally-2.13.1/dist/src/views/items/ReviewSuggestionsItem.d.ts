import { ExtensionContext, Uri } from 'vscode';
import { BaseTreeItem } from '.';
import { ReviewCommentWithMeta } from '~/core';
export declare class ReviewSuggestionsItem extends BaseTreeItem {
    readonly comment: ReviewCommentWithMeta;
    constructor(ctx: ExtensionContext, comment: ReviewCommentWithMeta);
    get iconPath(): Uri;
    getLabel(): string;
    get description(): string;
    set description(_: string);
}
