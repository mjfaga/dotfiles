import { ExtractionRule } from '../rules';
import { ExtractionHTMLOptions } from './options';
import { DetectionResult } from '~/core/types';
export declare function detect(input: string, rules?: ExtractionRule[], dynamicRules?: ExtractionRule[], userOptions?: ExtractionHTMLOptions, extractScripts?: (script: string, start: number) => DetectionResult[]): DetectionResult[];
