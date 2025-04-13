import { TextDocument } from 'vscode';
import { Framework } from './base';
import { LanguageId } from '~/utils';
declare class SvelteFramework extends Framework {
    id: string;
    display: string;
    detection: {
        packageJSON: string[];
    };
    languageIds: LanguageId[];
    usageMatchRegex: string[];
    refactorTemplates(keypath: string): string[];
    supportAutoExtraction: string[];
    detectHardStrings(doc: TextDocument): import("~/core").DetectionResult[];
}
export default SvelteFramework;
