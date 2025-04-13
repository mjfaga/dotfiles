import TranslateEngine, { TranslateOptions, TranslateResult } from './base';
export default class GoogleTranslate extends TranslateEngine {
    link: string;
    apiRoot: string;
    apiRootIfUserSuppliedKey: string;
    translate(options: TranslateOptions): Promise<TranslateResult>;
    convertToSupportedLocalesForGoogleCloud(locale: string): string;
    transform(response: any, options: TranslateOptions, apiKeySuppliedByUser: boolean): TranslateResult;
}
