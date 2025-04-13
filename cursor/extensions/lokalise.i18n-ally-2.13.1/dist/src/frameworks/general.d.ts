import { TextDocument } from 'vscode';
import { Framework } from './base';
import { LanguageId } from '~/utils';
declare class GeneralFramework extends Framework {
    id: string;
    display: string;
    detection: {
        packageJSON: () => boolean;
    };
    languageIds: LanguageId[];
    refactorTemplates(keypath: string, args?: string[]): string[];
    usageMatchRegex: never[];
    supportAutoExtraction: string[];
    detectHardStrings(doc: TextDocument): import("~/core").DetectionResult[];
}
export default GeneralFramework;
