import { ExtractionRule } from '../rules';
import { ExtractionBabelOptions } from './options';
import { DetectionResult } from '~/core/types';
export declare function detect(input: string, rules?: ExtractionRule[], dynamicRules?: ExtractionRule[], userOptions?: ExtractionBabelOptions, customCallExpression?: (path: any, recordIgnore: (path: any) => void) => void): DetectionResult[];
