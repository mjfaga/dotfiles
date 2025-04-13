import { Framework } from './base';
import { LanguageId } from '~/utils';
declare class LaravelFramework extends Framework {
    id: string;
    display: string;
    monopoly: boolean;
    detection: {
        composerJSON: string[];
    };
    languageIds: LanguageId[];
    enabledParsers: string[];
    usageMatchRegex: string[];
    refactorTemplates(keypath: string): string[];
    enableFeatures: {
        namespace: boolean;
    };
    pathMatcher: () => string;
    rewriteKeys(keypath: string): string;
}
export default LaravelFramework;
