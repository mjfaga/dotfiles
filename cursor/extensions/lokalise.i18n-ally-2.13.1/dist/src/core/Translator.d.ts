import { CancellationToken } from 'vscode';
import { PendingWrite } from './types';
import { LocaleTree, LocaleNode, LocaleRecord, Loader } from '.';
interface TranslatorChangeEvent {
    keypath: string;
    locale: string;
    action: 'start' | 'end';
}
export interface TranslateJob {
    loader: Loader;
    locale: string;
    keypath: string;
    source: string;
    filepath?: string;
    token?: CancellationToken;
}
export declare type AccaptableTranslateItem = LocaleNode | LocaleRecord | {
    locale: string;
    keypath: string;
    type: undefined;
};
export declare class Translator {
    private static translatingKeys;
    private static _onDidChange;
    static readonly onDidChange: import("vscode").Event<TranslatorChangeEvent>;
    private static _translator;
    private static start;
    private static end;
    static isTranslating(node: LocaleNode | LocaleRecord | LocaleTree): boolean;
    private static getValueOfKey;
    static translateNodes(loader: Loader, nodes: AccaptableTranslateItem[], sourceLanguage: string, targetLocales?: string[]): Promise<void>;
    static getTranslateJobs(loader: Loader, nodes: AccaptableTranslateItem[], sourceLanguage: string, targetLocales?: string[], token?: CancellationToken): TranslateJob[];
    static translateJob(job: TranslateJob): Promise<PendingWrite | undefined>;
    private static saveTranslations;
    private static translateText;
}
export {};
