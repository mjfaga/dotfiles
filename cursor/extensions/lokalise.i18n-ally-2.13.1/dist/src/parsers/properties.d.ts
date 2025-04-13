import { Parser } from './base';
export declare class Properties extends Parser {
    id: string;
    constructor();
    parse(text: string): Promise<any>;
    dump(object: object): Promise<any>;
}
