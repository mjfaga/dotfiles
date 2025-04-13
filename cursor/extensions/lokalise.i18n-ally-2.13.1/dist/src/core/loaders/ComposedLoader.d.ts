import { Disposable } from 'vscode';
import { PendingWrite } from '../types';
import { LocaleTree, LocaleNode, FlattenLocaleTree } from '../Nodes';
import { Loader } from './Loader';
export declare class ComposedLoader extends Loader {
    constructor();
    _loaders: Loader[];
    _watchers: Disposable[];
    _isFlattenLocaleTreeDirty: boolean;
    get files(): import("../types").FileInfo[];
    get loaders(): Loader[];
    set loaders(value: Loader[]);
    get loadersReversed(): Loader[];
    get root(): LocaleTree;
    get flattenLocaleTree(): FlattenLocaleTree;
    get locales(): string[];
    getNamespaceFromFilepath(filepath: string): string | undefined;
    getTreeNodeByKey(keypath: string, tree?: LocaleTree): LocaleNode | LocaleTree | undefined;
    getFilepathByKey(keypath: string, locale?: string): string | undefined;
    getValueByKey(keypath: string, locale?: string, maxLength?: number, stringifySpace?: number): string | undefined;
    fire(src?: string): void;
    write(pendings: PendingWrite | PendingWrite[], triggerFullfilled?: boolean): Promise<void>;
}
