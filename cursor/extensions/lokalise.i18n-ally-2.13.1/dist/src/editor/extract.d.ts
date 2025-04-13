import { TextDocument } from 'vscode';
import { ExtensionModule } from '~/modules';
import { ExtractTextOptions } from '~/commands/extractString';
import { DetectionResult } from '~/core/types';
export declare function DetectionResultToExtraction(detection: DetectionResult, document: TextDocument): ExtractTextOptions;
declare const m: ExtensionModule;
export default m;
