import TranslateEngine, { TranslateOptions, TranslateResult } from './base';
interface DeepLUsage {
    character_count: number;
    character_limit: number;
}
interface DeepLTranslate {
    detected_source_language: string;
    text: string;
}
declare function usage(): Promise<DeepLUsage>;
declare class DeepL extends TranslateEngine {
    translate(options: TranslateOptions): Promise<TranslateResult>;
    transform(res: DeepLTranslate[], options: TranslateOptions): TranslateResult;
}
export default DeepL;
export { usage, };
