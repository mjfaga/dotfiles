/// <reference types="vscode" />
import { ExtensionModule } from '~/modules';
import { DetectionResult } from '~/core';
export declare function DetectHardStrings(document?: import("vscode").TextDocument | undefined, warn?: boolean): Promise<DetectionResult[] | undefined>;
declare const _default: ExtensionModule;
export default _default;
