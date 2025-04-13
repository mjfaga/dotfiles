import { ExtractionRule, ExtractionScore } from './base';
export declare class BasicExtrationRule extends ExtractionRule {
    name: string;
    shouldExtract(str: string): ExtractionScore.ShouldInclude | ExtractionScore.ShouldExclude | ExtractionScore.MustExclude | undefined;
}
