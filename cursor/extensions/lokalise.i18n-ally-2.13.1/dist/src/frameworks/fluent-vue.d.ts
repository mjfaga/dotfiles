import { TextDocument } from 'vscode';
import { LanguageId } from '../utils';
import { Framework } from './base';
import { DetectionResult } from '~/core';
import { ExtractionRule, ExtractionScore } from '~/extraction';
declare class FluentVueFramework extends Framework {
    id: string;
    display: string;
    detection: {
        packageJSON: string[];
    };
    languageIds: LanguageId[];
    enabledParsers: string[];
    usageMatchRegex: string[];
    refactorTemplates(keypath: string, args?: string[], document?: TextDocument, detection?: DetectionResult): string[];
    supportAutoExtraction: string[];
    detectHardStrings(doc: TextDocument): DetectionResult[];
}
export declare class FluentVueExtractionRule extends ExtractionRule {
    name: string;
    shouldExtract(str: string): ExtractionScore.ShouldInclude | ExtractionScore.MustExclude;
}
export default FluentVueFramework;
