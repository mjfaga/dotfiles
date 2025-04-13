import { PackageParser } from './base';
export declare class GemfileParser extends PackageParser {
    static filename: string;
    protected static parserRaw(raw: string): string[];
}
