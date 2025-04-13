import { Framework } from './base';
import { RewriteKeySource, RewriteKeyContext } from '~/core';
import { LanguageId } from '~/utils';
declare class I18nextFramework extends Framework {
    id: string;
    display: string;
    namespaceDelimiter: string;
    namespaceDelimiters: string[];
    namespaceDelimitersRegex: RegExp;
    detection: {
        packageJSON: {
            any: string[];
            none: string[];
        };
    };
    languageIds: LanguageId[];
    usageMatchRegex: string[];
    derivedKeyRules: string[];
    refactorTemplates(keypath: string): string[];
    rewriteKeys(key: string, source: RewriteKeySource, context?: RewriteKeyContext): string;
}
export default I18nextFramework;
