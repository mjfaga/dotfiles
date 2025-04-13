import { Framework } from './base';
import { LanguageId } from '~/utils';
declare class NextTranslateFramework extends Framework {
    id: string;
    display: string;
    detection: {
        packageJSON: string[];
    };
    languageIds: LanguageId[];
    usageMatchRegex: string[];
    refactorTemplates(keypath: string): string[];
    rewriteKeys(key: string): string;
    pathMatcher(): string;
    preferredKeystyle: "nested";
    enableFeatures: {
        namespace: boolean;
    };
}
export default NextTranslateFramework;
