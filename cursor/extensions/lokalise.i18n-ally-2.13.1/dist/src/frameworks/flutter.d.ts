import { Framework } from './base';
import { LanguageId } from '~/utils';
declare class FlutterFramework extends Framework {
    id: string;
    display: string;
    detection: {
        pubspecYAML: string[];
    };
    languageIds: LanguageId[];
    usageMatchRegex: string[];
    refactorTemplates(keypath: string): string[];
}
export default FlutterFramework;
