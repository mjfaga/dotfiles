import { Framework } from './base';
import { LanguageId } from '~/utils';
declare class PhpJoomlaFramework extends Framework {
    id: string;
    display: string;
    detection: {
        composerJSON: string[];
    };
    languageIds: LanguageId[];
    enabledParsers: string[];
    usageMatchRegex: string[];
    refactorTemplates(keypath: string): string[];
}
export default PhpJoomlaFramework;
