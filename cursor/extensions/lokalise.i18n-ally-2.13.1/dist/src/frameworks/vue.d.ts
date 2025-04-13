import { TextDocument } from 'vscode';
import { Framework } from './base';
import { LanguageId } from '~/utils';
import { DetectionResult } from '~/core';
declare class VueFramework extends Framework {
    id: string;
    display: string;
    detection: {
        packageJSON: string[];
    };
    languageIds: LanguageId[];
    usageMatchRegex: string[];
    refactorTemplates(keypath: string, args?: string[], doc?: TextDocument, detection?: DetectionResult): string[];
    enableFeatures: {
        LinkedMessages: boolean;
    };
    supportAutoExtraction: string[];
    detectHardStrings(doc: TextDocument): DetectionResult[];
}
export default VueFramework;
