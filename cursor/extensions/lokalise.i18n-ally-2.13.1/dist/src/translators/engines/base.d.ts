export interface TranslateEngineConfig {
    timeout?: number;
    apiKey?: string;
}
export interface TranslateOptions {
    text: string;
    from?: string;
    to?: string;
}
export interface TranslateResult {
    text: string;
    from: string;
    to: string;
    response: any;
    linkToResult: string;
    error?: Error;
    result?: string[];
    detailed?: string[];
}
export default abstract class TranslateEngine {
    config: TranslateEngineConfig;
    constructor(config?: TranslateEngineConfig);
    resolve(lang: string): string;
    abstract translate(options: TranslateOptions): Promise<TranslateResult>;
}
