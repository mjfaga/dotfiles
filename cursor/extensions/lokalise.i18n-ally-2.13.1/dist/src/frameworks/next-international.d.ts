import { TextDocument } from 'vscode';
import { Framework, ScopeRange } from './base';
import { LanguageId } from '~/utils';
import { RewriteKeySource, RewriteKeyContext, KeyStyle } from '~/core';
declare class NextInternationalFramework extends Framework {
    id: string;
    display: string;
    namespaceDelimiter: string;
    perferredKeystyle?: KeyStyle;
    namespaceDelimiters: string[];
    namespaceDelimitersRegex: RegExp;
    detection: {
        packageJSON: string[];
    };
    languageIds: LanguageId[];
    supportAutoExtraction: string[];
    usageMatchRegex: string[];
    detectHardStrings(doc: TextDocument): import("~/core").DetectionResult[];
    refactorTemplates(keypath: string): string[];
    rewriteKeys(key: string, source: RewriteKeySource, context?: RewriteKeyContext): string;
    getScopeRange(document: TextDocument): ScopeRange[] | undefined;
}
export default NextInternationalFramework;
