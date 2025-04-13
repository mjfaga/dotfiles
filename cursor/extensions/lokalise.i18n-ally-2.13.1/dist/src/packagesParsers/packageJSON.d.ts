import { PackageParser } from './base';
export declare class PackageJSONParser extends PackageParser {
    static filename: string;
    protected static parserRaw(raw: string): string[];
}
