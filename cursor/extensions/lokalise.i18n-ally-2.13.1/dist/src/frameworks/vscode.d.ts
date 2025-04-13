import { TextDocument } from 'vscode';
import { Framework } from './base';
import { LanguageId } from '~/utils';
declare class VSCodeFramework extends Framework {
    id: string;
    display: string;
    detection: {
        packageJSON: string[];
    };
    enabledParsers: string[];
    languageIds: LanguageId[];
    pathMatcher: () => string;
    usageMatchRegex: (languageIds?: string | undefined, filename?: string | undefined) => "\"%({key})%\"" | "(?:i18n[ (]path=|v-t=['\"`{]|(?:this\\.|\\$|i18n\\.)(?:(?:d|n)\\(.*?,|(?:t|tc|te)\\()\\s*)['\"`]({key})['\"`]";
    refactorTemplates(keypath: string, args?: string[], doc?: TextDocument): string[];
}
export default VSCodeFramework;
