import { Range, TextDocument } from 'vscode';
import { ExtensionModule } from '~/modules';
export interface ExtractTextOptions {
    text: string;
    rawText?: string;
    args?: string[];
    range: Range;
    isDynamic?: boolean;
    document: TextDocument;
    isInsert?: boolean;
}
declare const m: ExtensionModule;
export default m;
