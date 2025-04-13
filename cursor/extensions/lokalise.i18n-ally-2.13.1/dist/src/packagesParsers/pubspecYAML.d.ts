import { PackageParser } from './base';
export declare class PubspecYAMLParser extends PackageParser {
    static filename: string;
    protected static parserRaw(raw: string): string[];
}
