export declare enum ErrorType {
    translating_same_locale = "errors.translating_same_locale",
    translating_unknown_error = "errors.translating_unknown_error",
    translating_empty_source_value = "errors.translating_empty_source_value",
    unsupported_file_type = "errors.unsupported_file_type",
    keystyle_not_set = "errors.keystyle_not_set",
    write_in_readonly_mode = "errors.write_in_readonly_mode"
}
export declare class AllyError extends Error {
    readonly type: ErrorType;
    readonly error?: Error | undefined;
    readonly args: any[];
    constructor(type: ErrorType, error?: Error | undefined, ...args: any[]);
    get stack(): string | undefined;
}
