import { Parser } from './base';
export declare class EcmascriptParser extends Parser {
    readonly id: 'js' | 'ts';
    readonly readonly = true;
    constructor(id?: 'js' | 'ts');
    parse(): Promise<{}>;
    dump(): Promise<string>;
    load(filepath: string): Promise<any>;
    save(): Promise<void>;
}
