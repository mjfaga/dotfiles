import { Parser } from './base';
export declare class PoParser extends Parser {
    id: string;
    constructor();
    readonly: boolean;
    parse(text: string): Promise<Record<string, string>>;
    dump(object: object): Promise<string>;
}
