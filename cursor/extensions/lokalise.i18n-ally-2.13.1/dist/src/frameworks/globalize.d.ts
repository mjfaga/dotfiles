import { Framework } from './base';
import { LanguageId } from '~/utils';
declare class GlobalizeFramework extends Framework {
    id: string;
    display: string;
    detection: {
        packageJSON: string[];
    };
    languageIds: LanguageId[];
    usageMatchRegex: string[];
    refactorTemplates(keypath: string): string[];
    rewriteKeys(keypath: string): string;
}
export default GlobalizeFramework;
