import { Uri } from 'vscode';
import { SFCI18nBlock, MetaLocaleMessage } from 'vue-i18n-locale-message';
import { PendingWrite } from '../types';
import { Loader } from './Loader';
export declare class VueSfcLoader extends Loader {
    readonly uri: Uri;
    constructor(uri: Uri);
    _parsedSections: SFCI18nBlock[];
    _meta: MetaLocaleMessage | undefined;
    get filepath(): string;
    get files(): never[];
    load(): Promise<void>;
    private getOptions;
    private getSFCFileInfo;
    _locales: Set<string>;
    private updateLocalesTree;
    get locales(): string[];
    write(pendings: PendingWrite | PendingWrite[]): Promise<void>;
    canHandleWrites(pending: PendingWrite): boolean;
}
