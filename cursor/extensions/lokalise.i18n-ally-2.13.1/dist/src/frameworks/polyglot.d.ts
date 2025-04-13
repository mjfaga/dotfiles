import { Framework } from './base';
import { LanguageId } from '~/utils';
declare class PolyglotFramework extends Framework {
    id: string;
    display: string;
    detection: {
        packageJSON: string[];
    };
    languageIds: LanguageId[];
    usageMatchRegex: string[];
    refactorTemplates(keypath: string): string[];
}
export default PolyglotFramework;
