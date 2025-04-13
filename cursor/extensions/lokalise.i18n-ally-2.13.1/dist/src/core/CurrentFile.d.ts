/// <reference types="lodash" />
import { ExtensionContext, Uri, EventEmitter } from 'vscode';
import { ComposedLoader } from './loaders/ComposedLoader';
import { VueSfcLoader } from './loaders/VueSfcLoader';
import { FluentVueSfcLoader } from './loaders/FluentVueSfcLoader';
import { DetectionResult } from '~/core/types';
export declare class CurrentFile {
    static _vue_sfc_loader: VueSfcLoader | null;
    static _fluent_vue_sfc_loader: FluentVueSfcLoader | null;
    static _composed_loader: ComposedLoader;
    static _onInvalidate: EventEmitter<boolean>;
    static _onInitialized: EventEmitter<void>;
    static _onHardStringDetected: EventEmitter<DetectionResult[] | undefined>;
    static _currentUri: Uri | undefined;
    static onInvalidate: import("vscode").Event<boolean>;
    static onHardStringDetected: import("vscode").Event<DetectionResult[] | undefined>;
    static onInitialized: import("vscode").Event<void>;
    static get VueSfc(): boolean;
    static get FluentVueSfc(): boolean;
    static watch(ctx: ExtensionContext): void;
    static throttleUpdate: import("lodash").DebouncedFunc<(uri?: Uri | undefined) => void>;
    static update(uri?: Uri): void;
    static updateLoaders(): void;
    static get loader(): ComposedLoader;
    static invalidate(): void;
    static hardStrings: DetectionResult[] | undefined;
    static detectHardStrings(force?: boolean): Promise<DetectionResult[] | undefined>;
}
