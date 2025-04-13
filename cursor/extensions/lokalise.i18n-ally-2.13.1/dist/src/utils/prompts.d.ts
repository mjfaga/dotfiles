import { TextDocument } from 'vscode';
import { DetectionResult } from '~/core';
export declare function promptEdit(keypath: string, locale: string, value?: string): Promise<string | undefined>;
export declare function promptKeys(text: string, locale?: string): Promise<string | undefined>;
export declare function promptTemplates(keypath: string, args?: string[], doc?: TextDocument, detection?: DetectionResult): Promise<string | undefined>;
