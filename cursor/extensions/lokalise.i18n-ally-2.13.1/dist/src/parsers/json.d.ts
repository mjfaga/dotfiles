import { Parser } from './base';
export declare class JsonParser extends Parser {
    id: string;
    constructor();
    parse(text: string): Promise<any>;
    dump(object: object, sort: boolean, compare: ((x: string, y: string) => number) | undefined): Promise<string>;
    annotationSupported: boolean;
    annotationLanguageIds: string[];
    parseAST(text: string): {
        quoted: boolean;
        start: any;
        end: number;
        key: string;
    }[];
}
