import { ExtensionContext } from 'vscode';
import { ReviewTranslationCandidatesItem } from './ReviewTranslationCandidatesItem';
import { BaseTreeItem } from '.';
import { TranslationCandidateWithMeta } from '~/core';
export declare class ReviewTranslationCandidates extends BaseTreeItem {
    readonly candidates: TranslationCandidateWithMeta[];
    constructor(ctx: ExtensionContext, candidates: TranslationCandidateWithMeta[]);
    get iconPath(): string | {
        light: string;
        dark: string;
    };
    getLabel(): string;
    getChildren(): Promise<ReviewTranslationCandidatesItem[]>;
}
