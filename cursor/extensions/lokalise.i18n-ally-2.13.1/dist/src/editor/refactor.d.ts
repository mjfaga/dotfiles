import { CodeActionProvider, TextDocument, Range, CodeAction, CodeActionContext } from 'vscode';
import { ExtensionModule } from '~/modules';
export declare class Refactor implements CodeActionProvider {
    provideCodeActions(document: TextDocument, range: Range, context: CodeActionContext): CodeAction[] | undefined;
    private createEditQuickFix;
    private createTranslateQuickFix;
}
declare const m: ExtensionModule;
export default m;
