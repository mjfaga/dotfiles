import { TextDocument } from 'vscode';
import { LanguageId } from '~/utils';
import { DirStructure, OptionalFeatures, RewriteKeySource, RewriteKeyContext, DataProcessContext, KeyStyle } from '~/core';
import { DetectionResult } from '~/core/types';
export declare type FrameworkDetectionDefine = string[] | {
    none?: string[];
    every?: string[];
    any?: string[];
} | ((packages: string[], root: string) => boolean);
export declare type PackageFileType = 'packageJSON' | 'pubspecYAML' | 'composerJSON' | 'gemfile' | 'none';
export interface ScopeRange {
    start: number;
    end: number;
    namespace: string;
}
export declare abstract class Framework {
    abstract id: string;
    abstract display: string;
    monopoly?: boolean;
    enabledParsers?: string[];
    derivedKeyRules?: string[];
    namespaceDelimiter?: string;
    supportAutoExtraction?: string[];
    /**
     * Packages names determine whether a frameworks should enable or not
     */
    abstract detection: Partial<Record<PackageFileType, FrameworkDetectionDefine>>;
    /**
     * Language Ids to enables annotations
     */
    abstract languageIds: LanguageId[];
    /**
     * Array of regex for detect keys in document
     */
    abstract usageMatchRegex: string | RegExp | (string | RegExp)[] | ((languageId?: string, filepath?: string) => string | RegExp | (string | RegExp)[]);
    /**
     * Return possible choices of replacement for messages extracted from code
     */
    abstract refactorTemplates(keypath: string, args?: string[], document?: TextDocument, detection?: DetectionResult): string[];
    /**
     * Analysis the file and get hard strings
     */
    detectHardStrings(document: TextDocument): DetectionResult[] | undefined;
    /**
     * Tell the key dector how to add prefix scopes
     */
    getScopeRange(document: TextDocument): ScopeRange[] | undefined;
    /**
     * Locale file's name match
     */
    pathMatcher(dirStructure?: DirStructure): string;
    preferredLocalePaths?: string[];
    preferredKeystyle?: KeyStyle;
    preferredDirStructure?: DirStructure;
    enableFeatures?: OptionalFeatures;
    getUsageMatchRegex(languageId?: string, filepath?: string): string | RegExp | (string | RegExp)[];
    rewriteKeys(key: string, source: RewriteKeySource, context?: RewriteKeyContext): string;
    preprocessData(data: object, context: DataProcessContext): object;
    deprocessData(data: object, context: DataProcessContext): object;
}
