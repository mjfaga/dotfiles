import { Framework } from './base';
import { LanguageId } from '~/utils';
declare class LinguiFramework extends Framework {
    id: string;
    display: string;
    detection: {
        packageJSON: string[];
    };
    enabledParsers: string[];
    languageIds: LanguageId[];
    usageMatchRegex: string[];
    refactorTemplates(keypath: string): string[];
    pathMatcher(): string;
}
export default LinguiFramework;
