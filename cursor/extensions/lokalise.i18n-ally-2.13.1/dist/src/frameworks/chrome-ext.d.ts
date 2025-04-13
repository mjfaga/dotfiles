import { RewriteKeySource } from '../core/types';
import { Framework } from './base';
import { LanguageId } from '~/utils';
declare class ChromeExtensionFramework extends Framework {
    id: string;
    display: string;
    detection: {};
    languageIds: LanguageId[];
    usageMatchRegex: string[];
    refactorTemplates(keypath: string): string[];
    rewriteKeys(key: string, source: RewriteKeySource): string;
}
export default ChromeExtensionFramework;
