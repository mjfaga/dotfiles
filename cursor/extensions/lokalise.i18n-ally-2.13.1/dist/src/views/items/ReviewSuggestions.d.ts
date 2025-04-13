import { ExtensionContext } from 'vscode';
import { ReviewSuggestionsItem } from './ReviewSuggestionsItem';
import { BaseTreeItem } from '.';
import { ReviewCommentWithMeta } from '~/core';
export declare class ReviewSuggestions extends BaseTreeItem {
    readonly comments: ReviewCommentWithMeta[];
    constructor(ctx: ExtensionContext, comments: ReviewCommentWithMeta[]);
    get iconPath(): string | {
        light: string;
        dark: string;
    };
    getLabel(): string;
    getChildren(): Promise<ReviewSuggestionsItem[]>;
}
