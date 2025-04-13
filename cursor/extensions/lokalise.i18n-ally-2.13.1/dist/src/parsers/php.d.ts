import { Parser } from './base';
export declare class PhpParser extends Parser {
    id: string;
    readonly: boolean;
    constructor();
    parse(text: string): Promise<any>;
    dump(): Promise<string>;
}
