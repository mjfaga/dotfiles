export declare enum ExtractionScore {
    MustInclude = 0,
    ShouldInclude = 1,
    None = 2,
    ShouldExclude = 3,
    MustExclude = 4
}
export declare abstract class ExtractionRule {
    abstract name: string;
    shouldExtract(str: string): ExtractionScore | void;
}
