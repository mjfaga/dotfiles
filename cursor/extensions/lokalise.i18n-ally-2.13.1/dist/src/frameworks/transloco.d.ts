import { TextDocument } from 'vscode';
import { Framework, ScopeRange } from './base';
import { LanguageId } from '~/utils';
export default class TranslocoFramework extends Framework {
    id: string;
    display: string;
    detection: {
        packageJSON: string[];
    };
    languageIds: LanguageId[];
    usageMatchRegex: string[];
    refactorTemplates(keypath: string): string[];
    rewriteKeys(key: string): string;
    getScopeRange(document: TextDocument): ScopeRange[] | undefined;
}
