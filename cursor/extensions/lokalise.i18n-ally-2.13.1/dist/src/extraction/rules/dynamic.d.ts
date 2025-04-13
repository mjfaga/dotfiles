import { ExtractionRule, ExtractionScore } from './base';
export declare class DynamicExtractionRule extends ExtractionRule {
    name: string;
    shouldExtract(str: string): ExtractionScore.ShouldInclude | ExtractionScore.MustExclude;
}
