import { TextDocument } from 'vscode';
import { KeyStyle, ParserOptions, KeyInDocument } from '~/core';
export declare abstract class Parser {
    readonly languageIds: string[];
    readonly supportedExts: string;
    options: ParserOptions;
    abstract readonly id: string;
    private supportedExtsRegex;
    readonly readonly: boolean;
    constructor(languageIds: string[], supportedExts: string, options?: ParserOptions);
    supports(ext: string): boolean;
    load(filepath: string): Promise<object>;
    save(filepath: string, object: object, sort: boolean, compare: ((x: string, y: string) => number) | undefined): Promise<void>;
    abstract parse(text: string): Promise<object>;
    abstract dump(object: object, sort: boolean, compare: ((x: string, y: string) => number) | undefined): Promise<string>;
    parseAST(text: string): KeyInDocument[];
    navigateToKey(text: string, keypath: string, keystyle: KeyStyle): KeyInDocument | undefined;
    annotationSupported: boolean;
    annotationLanguageIds: string[];
    annotationGetKeys(document: TextDocument): KeyInDocument[];
}
