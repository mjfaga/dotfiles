import { TextDocument } from 'vscode';
import { Framework, ScopeRange } from './base';
import { LanguageId } from '~/utils';
import { RewriteKeySource, RewriteKeyContext } from '~/core';
declare class ReactI18nextFramework extends Framework {
    id: string;
    display: string;
    namespaceDelimiter: string;
    namespaceDelimiters: string[];
    namespaceDelimitersRegex: RegExp;
    detection: {
        packageJSON: string[];
    };
    languageIds: LanguageId[];
    usageMatchRegex: string[];
    supportAutoExtraction: string[];
    derivedKeyRules: string[];
    detectHardStrings(doc: TextDocument): import("~/core").DetectionResult[];
    refactorTemplates(keypath: string): string[];
    rewriteKeys(key: string, source: RewriteKeySource, context?: RewriteKeyContext): string;
    getScopeRange(document: TextDocument): ScopeRange[] | undefined;
}
export default ReactI18nextFramework;
