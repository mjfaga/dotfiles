import { Parser } from './base';
import { KeyInDocument } from '~/core';
export declare class YamlParser extends Parser {
    id: string;
    constructor();
    parse(text: string): Promise<Object>;
    dump(object: object, sort: boolean, compare: ((x: string, y: string) => number) | undefined): Promise<string>;
    annotationSupported: boolean;
    annotationLanguageIds: string[];
    parseAST(text: string): KeyInDocument[];
}
