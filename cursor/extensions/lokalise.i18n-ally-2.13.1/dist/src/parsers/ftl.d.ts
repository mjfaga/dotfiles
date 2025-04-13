import { Parser } from './base';
export declare class FluentParser extends Parser {
    id: string;
    constructor();
    parse(text: string): Promise<Record<string, string>>;
    dump(): Promise<string>;
    save(filepath: string, object: Record<string, string>): Promise<void>;
}
