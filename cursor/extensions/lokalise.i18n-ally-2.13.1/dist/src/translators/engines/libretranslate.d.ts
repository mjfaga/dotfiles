import TranslateEngine, { TranslateOptions, TranslateResult } from './base';
export default class LibreTranslate extends TranslateEngine {
    apiRoot: string;
    translate(options: TranslateOptions): Promise<TranslateResult>;
    transform(response: any, options: TranslateOptions): TranslateResult;
}
