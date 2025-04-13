/// <reference types="node" />
interface FileEncoding {
    encoding: string;
    bom: boolean;
}
interface DecodeData {
    encoding: string;
    bom: boolean;
    content: string;
}
export declare class File {
    private static _fileEncoding;
    private static __setFileEncoding;
    private static __getFileEncoding;
    static read(filepath: string, encodingConfig?: string): Promise<string>;
    static readSync(filepath: string, encodingConfig?: string): string;
    static write(filepath: string, data: any, opts?: FileEncoding): Promise<void>;
    static writeSync(filepath: string, data: any, opts?: FileEncoding): void;
    static decode(buffer: Buffer, encoding?: string): DecodeData;
    static encode(string: string, encoding: string, addBOM?: boolean): Buffer;
}
export {};
