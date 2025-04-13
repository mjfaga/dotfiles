export declare abstract class PackageParser {
    static filename: string;
    static load(root: string): string[] | undefined;
    protected static loadFile(filepath: string): string;
    protected static parserRaw(raw: string): string[];
}
