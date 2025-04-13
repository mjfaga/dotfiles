import { Framework } from './base';
import { LanguageId } from '~/utils';
declare class I18js extends Framework {
    id: string;
    display: string;
    namespaceDelimiter: string;
    detection: {
        packageJSON: {
            any: string[];
        };
    };
    languageIds: LanguageId[];
    usageMatchRegex: string[];
    refactorTemplates(keypath: string): string[];
}
export default I18js;
