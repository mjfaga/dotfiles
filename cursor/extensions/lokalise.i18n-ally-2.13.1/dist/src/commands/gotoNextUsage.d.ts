/// <reference types="vscode" />
import { ExtensionModule } from '~/modules';
export declare function getCurrentUsagePos(): {
    index: number;
    usages: import("~/core").KeyUsages;
    document: import("vscode").TextDocument;
} | undefined;
export declare function GoToNextUsage(): void;
export declare function GoToPrevUsage(): void;
declare const _default: ExtensionModule;
export default _default;
