import { ExtractionRule, ExtractionScore } from './base';
export declare class NonAsciiExtractionRule extends ExtractionRule {
    name: string;
    shouldExtract(str: string): ExtractionScore.MustInclude | undefined;
}
