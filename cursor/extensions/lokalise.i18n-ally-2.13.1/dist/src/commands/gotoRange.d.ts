import { Range, TextDocument } from 'vscode';
import { ExtensionModule } from '~/modules';
export declare function GoToRange(document: TextDocument, range: Range): Promise<void>;
declare const _default: ExtensionModule;
export default _default;
