import { TextDocument } from 'vscode';
import { ExtractInfo } from './types';
export declare function generateKeyFromText(text: string, filepath?: string, reuseExisting?: boolean, usedKeys?: string[]): string;
export declare function extractHardStrings(document: TextDocument, extracts: ExtractInfo[], saveFile?: boolean): Promise<void>;
