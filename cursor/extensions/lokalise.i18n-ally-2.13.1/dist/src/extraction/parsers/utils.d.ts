/// <reference types="vscode" />
import { DetectionResult } from '~/core/types';
export declare function shiftDetectionPosition(result: DetectionResult[], offest: number): {
    text: string;
    start: number;
    end: number;
    document?: import("vscode").TextDocument | undefined;
    isDynamic?: boolean | undefined;
    fullText?: string | undefined;
    fullStart?: number | undefined;
    fullEnd?: number | undefined;
    source: import("~/core/types").DetectionSource;
}[];
