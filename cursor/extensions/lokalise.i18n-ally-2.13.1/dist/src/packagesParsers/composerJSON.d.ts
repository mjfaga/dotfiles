import { PackageParser } from './base';
export declare class ComposerJSONParser extends PackageParser {
    static filename: string;
    protected static parserRaw(raw: string): string[];
}
