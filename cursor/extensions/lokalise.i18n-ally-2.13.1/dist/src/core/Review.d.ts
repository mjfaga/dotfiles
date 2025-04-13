/// <reference types="vscode" />
import { ReviewComment, ReviewCommentWithMeta, TranslationCandidate, TranslationCandidateWithMeta } from './types';
export declare class Reviews {
    private filepath;
    private data;
    private _fileWatcher;
    private mtime;
    private _onDidChange;
    readonly onDidChange: import("vscode").Event<string | undefined>;
    init(rootpath: string): Promise<void>;
    private set;
    private get;
    setDescription(key: string, description?: string): Promise<void> | undefined;
    getDescription(key: string): string | undefined;
    setTranslationCandidates(items: {
        key: string;
        locale: string;
        translation?: TranslationCandidate;
    }[]): Promise<void>;
    getTranslationCandidate(key: string, locale: string): TranslationCandidate | undefined;
    applyTranslationCandidates(candidates: {
        keypath: string;
        locale: string;
    }[]): Promise<void>;
    applyTranslationCandidate(key: string, locale: string, override?: string): Promise<void>;
    discardTranslationCandidate(key: string, locale: string, save?: boolean): Promise<void>;
    promptEditTranslation(key: any, locale: any): Promise<void>;
    getReviews(key: string): {
        description?: string | undefined;
        locales?: Record<string, {
            translation_candidate?: TranslationCandidate | undefined;
            comments?: ReviewComment[] | undefined;
        }> | undefined;
    };
    addComment(key: string, locale: string, comment: Partial<ReviewComment>): Promise<void> | undefined;
    editComment(key: string, locale: string, data: Partial<ReviewComment> & {
        id: string;
    }): Promise<void> | undefined;
    getComments(key: string, locale: string, hideResolved?: boolean): ReviewComment[];
    getCommentById(key: string, locale: string, id: string): ReviewComment | undefined;
    getCommentsByLocale(locale: string, hideResolved?: boolean): ReviewCommentWithMeta[];
    getTranslationCandidatesLocale(locale: string): TranslationCandidateWithMeta[];
    resolveComment(key: string, locale: string, id: string): Promise<ReviewComment | undefined>;
    applySuggestion(key: string, locale: string, id: string): Promise<void>;
    promptEditDescription(keypath: string): Promise<void>;
    private load;
    private save;
}
