import { Uri } from 'vscode';
import { PendingWrite } from '../types';
import { Loader } from './Loader';
export declare class FluentVueSfcLoader extends Loader {
    readonly uri: Uri;
    constructor(uri: Uri);
    get filepath(): string;
    get files(): never[];
    load(): Promise<void>;
    private getOptions;
    _locales: Set<string>;
    private updateLocalesTree;
    get locales(): string[];
    write(pendings: PendingWrite | PendingWrite[]): Promise<void>;
    canHandleWrites(pending: PendingWrite): boolean;
}
