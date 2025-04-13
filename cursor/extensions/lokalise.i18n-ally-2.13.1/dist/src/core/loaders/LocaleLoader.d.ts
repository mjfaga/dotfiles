import { WorkspaceEdit } from 'vscode';
import { ParsedFile, PendingWrite, DirStructure } from '../types';
import { Loader } from './Loader';
export declare class LocaleLoader extends Loader {
    readonly rootpath: string;
    private _files;
    private _path_matchers;
    private _dir_structure;
    private _locale_dirs;
    constructor(rootpath: string);
    init(): Promise<void>;
    get localesPaths(): string[] | undefined;
    get files(): ParsedFile[];
    get locales(): string[];
    private throttledFullReload;
    private throttledUpdate;
    private throttledLoadFileWaitingList;
    private throttledLoadFileExecutor;
    private throttledLoadFile;
    private getFilepathsOfLocale;
    guessDirStructure(): Promise<DirStructure>;
    requestMissingFilepath(pending: PendingWrite): Promise<string | void>;
    promptPathToSave(paths: string[], keypath: string): Promise<string | undefined>;
    /**
     * Extract text to current file's previous selected locale file
     * @param fromPath: path of current extracting file
     * @param paths: paths of locale files
     * @param keypath
     */
    handleExtractToFilePrevious(fromPath: string, paths: string[], keypath: string): Promise<string | void>;
    /**
     * Extract text to previous selected locale file (includes selection made in other files)
     * @param paths: paths of locale files
     * @param keypath
     */
    handleExtractToGlobalPrevious(paths: any, keypath: string): Promise<string | void>;
    findBestMatchFile(fromPath: string, paths: string[]): string;
    write(pendings: PendingWrite | PendingWrite[]): Promise<void>;
    canHandleWrites(pending: PendingWrite): boolean;
    renameKey(oldkey: string, newkey: string): Promise<WorkspaceEdit>;
    renameKeyInLocales(oldkey: string, newkey: string): Promise<void>;
    getNamespaceFromFilepath(filepath: string): string | undefined;
    private getFileInfo;
    private loadFile;
    private unsetFile;
    private loadDirectory;
    private getMtime;
    private getRelativePath;
    private onFileChanged;
    private watchOn;
    private updateLocalesTree;
    private update;
    private findLocaleDirs;
    private loadAll;
}
