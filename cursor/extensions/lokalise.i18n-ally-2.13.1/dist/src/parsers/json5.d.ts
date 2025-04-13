import { Parser } from './base';
import { KeyStyle } from '~/core';
export declare class Json5Parser extends Parser {
    id: string;
    constructor();
    parse(text: string): Promise<any>;
    dump(object: object): Promise<string>;
    navigateToKey(text: string, keypath: string, keystyle: KeyStyle): {
        start: number;
        end: number;
        key: string;
        quoted: boolean;
    } | undefined;
}
