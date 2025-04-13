import { ExtensionContext } from 'vscode';
import { ReviewRequestChangesItem } from './ReviewRequestChangesItem';
import { BaseTreeItem } from '.';
import { ReviewCommentWithMeta } from '~/core';
export declare class ReviewRequestChangesRoot extends BaseTreeItem {
    readonly comments: ReviewCommentWithMeta[];
    constructor(ctx: ExtensionContext, comments: ReviewCommentWithMeta[]);
    get iconPath(): string | {
        light: string;
        dark: string;
    };
    getLabel(): string;
    getChildren(): Promise<ReviewRequestChangesItem[]>;
}
