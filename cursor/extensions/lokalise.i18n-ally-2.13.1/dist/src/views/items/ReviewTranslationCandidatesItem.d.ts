import { ExtensionContext } from 'vscode';
import { BaseTreeItem } from '.';
import { TranslationCandidateWithMeta } from '~/core';
export declare class ReviewTranslationCandidatesItem extends BaseTreeItem {
    readonly candidate: TranslationCandidateWithMeta;
    constructor(ctx: ExtensionContext, candidate: TranslationCandidateWithMeta);
    get description(): string;
    get iconPath(): string | {
        light: string;
        dark: string;
    };
    getLabel(): string;
}
