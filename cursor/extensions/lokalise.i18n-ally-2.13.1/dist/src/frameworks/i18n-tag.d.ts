import { Framework } from './base';
import { LanguageId } from '~/utils';
declare class I18nTagFramework extends Framework {
    id: string;
    display: string;
    detection: {
        packageJSON: string[];
    };
    languageIds: LanguageId[];
    usageMatchRegex: string[];
    refactorTemplates(keypath: string): string[];
}
export default I18nTagFramework;
