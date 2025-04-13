import { DecorationOptions } from 'vscode';
import { ExtensionModule } from '~/modules';
export declare type DecorationOptionsWithGutter = DecorationOptions & {
    gutterType: string;
};
declare const annotation: ExtensionModule;
export default annotation;
