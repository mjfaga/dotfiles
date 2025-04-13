import TranslateEngine, { TranslateOptions, TranslateResult } from './base';
interface BaiduSignOptions {
    appid: string | null | undefined;
    salt: string;
    secret: string | null | undefined;
    query: string;
}
export default class BaiduTranslate extends TranslateEngine {
    apiLink: string;
    apiRoot: string;
    translate(options: TranslateOptions): Promise<TranslateResult>;
    convertToSupportedLocalesForGoogleCloud(locale: string): string;
    getSign({ appid, salt, query, secret }: BaiduSignOptions): string;
    transform(response: any, options: TranslateOptions): TranslateResult;
}
export {};
