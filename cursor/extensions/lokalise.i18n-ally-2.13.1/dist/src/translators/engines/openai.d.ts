import TranslateEngine, { TranslateOptions, TranslateResult } from "./base";
export default class OpenAITranslate extends TranslateEngine {
    apiRoot: string;
    systemPrompt: string;
    translate(options: TranslateOptions): Promise<TranslateResult>;
    transform(response: any, options: TranslateOptions): TranslateResult;
    generateUserPrompts(options: TranslateOptions): string;
}
