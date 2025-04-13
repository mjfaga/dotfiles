import { Parser } from './base';
export declare class IniParser extends Parser {
    id: string;
    constructor();
    parse(text: string): Promise<{
        [key: string]: any;
    }>;
    dump(object: object): Promise<string>;
}
