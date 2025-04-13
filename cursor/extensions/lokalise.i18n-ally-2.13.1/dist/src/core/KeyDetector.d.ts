import { TextDocument, Position, Range, ExtensionContext } from 'vscode';
import { Loader } from './loaders/Loader';
import { ScopeRange } from '~/frameworks';
import { KeyInDocument } from '~/core';
export interface KeyUsages {
    type: 'code' | 'locale';
    keys: KeyInDocument[];
    locale: string;
    namespace?: string;
}
export declare class KeyDetector {
    static getKeyByContent(text: string): string[];
    static getKeyRange(document: TextDocument, position: Position, dotEnding?: boolean): {
        range: Range;
        key: string;
    } | undefined;
    static getKey(document: TextDocument, position: Position, dotEnding?: boolean): string | undefined;
    static getScopedKey(document: TextDocument, position: Position): string | undefined;
    static getKeyAndRange(document: TextDocument, position: Position, dotEnding?: boolean): {
        range: Range;
        key: string;
    } | undefined;
    static init(ctx: ExtensionContext): void;
    private static _get_keys_cache;
    static getKeys(document: TextDocument | string, regs?: RegExp[], dotEnding?: boolean, scopes?: ScopeRange[]): KeyInDocument[];
    static getUsages(document: TextDocument, loader?: Loader): KeyUsages | undefined;
}
