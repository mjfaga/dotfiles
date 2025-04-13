import { ExtensionContext } from 'vscode';
import { Global, Config, KeyDetector, CurrentFile } from '~/core';
import { Commands } from '~/commands';
import { Log } from '~/utils';
export declare function activate(ctx: ExtensionContext): Promise<void>;
export declare function deactivate(): void;
export { Global, CurrentFile, KeyDetector, Config, Log, Commands, };
