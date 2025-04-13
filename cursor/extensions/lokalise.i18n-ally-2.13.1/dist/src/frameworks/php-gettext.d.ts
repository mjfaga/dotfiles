import { Framework } from './base';
import { LanguageId } from '~/utils';
declare class PhpGettextFramework extends Framework {
    id: string;
    display: string;
    monopoly: boolean;
    detection: {};
    languageIds: LanguageId[];
    enabledParsers: string[];
    usageMatchRegex: string[];
    refactorTemplates(keypath: string): string[];
    enableFeatures: {
        namespace: boolean;
    };
}
export default PhpGettextFramework;
