import { ExtensionContext, TextDocument, Diagnostic, Uri } from 'vscode';
import { ExtensionModule } from '~/modules';
import { DetectionResult } from '~/core';
export declare const PROBLEM_CODE_HARD_STRING = "i18n-ally-hard-string";
export declare const PROBLEM_KEY_MISSING = "i18n-ally-key-missing";
export declare const PROBLEM_TRANSLATION_MISSING = "i18n-ally-translation-missing";
export interface DiagnosticWithDetection extends Diagnostic {
    detection?: DetectionResult;
}
export interface DiagnosticWithKey extends Diagnostic {
    key?: string;
}
export declare class ProblemProvider {
    readonly ctx: ExtensionContext;
    private collection;
    constructor(ctx: ExtensionContext);
    update(document?: TextDocument): void;
    clear(): void;
    clearUri(uri: Uri): void;
}
declare const m: ExtensionModule;
export default m;
