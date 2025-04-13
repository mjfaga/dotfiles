import TranslateEngine, { TranslateOptions } from './engines/base';
import GoogleTranslateEngine from './engines/google';
import GoogleTranslateCnEngine from './engines/google-cn';
import DeepLTranslateEngine from './engines/deepl';
import LibreTranslateEngine from './engines/libretranslate';
import BaiduTranslate from './engines/baidu';
import OpenAITranslateEngine from './engines/openai';
export declare class Translator {
    engines: Record<string, TranslateEngine>;
    translate(options: TranslateOptions & {
        engine: string;
    }): Promise<import("./engines/base").TranslateResult>;
}
export { TranslateEngine, GoogleTranslateEngine, GoogleTranslateCnEngine, DeepLTranslateEngine, LibreTranslateEngine, BaiduTranslate, OpenAITranslateEngine, };
export * from './engines/base';
