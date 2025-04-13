import { Framework } from './base';
import { LanguageId } from '~/utils';
declare class JekyllFramework extends Framework {
    id: string;
    display: string;
    detection: {
        gemfile: string[];
    };
    languageIds: LanguageId[];
    usageMatchRegex: string[];
    preferredKeystyle: "nested";
    refactorTemplates(keypath: string): string[];
}
export default JekyllFramework;
