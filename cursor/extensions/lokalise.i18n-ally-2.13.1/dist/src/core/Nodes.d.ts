import { OptionalFeatures, NodeMeta } from './types';
export interface INode {
    keypath: string;
    keyname?: string;
    filepath?: string;
    shadow?: boolean;
    readonly?: boolean;
    features?: OptionalFeatures;
    meta?: NodeMeta;
}
declare abstract class BaseNode implements INode {
    readonly keypath: string;
    readonly keyname: string;
    readonly filepath?: string;
    readonly shadow?: boolean;
    readonly readonly?: boolean;
    readonly features?: OptionalFeatures;
    readonly meta?: NodeMeta;
    constructor(data: INode);
}
export declare class LocaleRecord extends BaseNode implements ILocaleRecord {
    readonly type: 'record';
    readonly locale: string;
    readonly value: string;
    constructor(data: ILocaleRecord);
}
export declare class LocaleNode extends BaseNode implements ILocaleNode {
    readonly type: 'node';
    readonly locales: Record<string, LocaleRecord>;
    constructor(data: ILocaleNode);
    getValue(locale?: string, interpolate?: boolean, visitedStack?: string[]): string;
    get value(): string;
}
export declare class LocaleTree extends BaseNode implements ILocaleTree {
    readonly type: 'tree';
    readonly children: Record<string | number, LocaleTree | LocaleNode>;
    readonly values: Record<string, object>;
    readonly isCollection: boolean;
    constructor(data: ILocaleTree);
    getChild(key: string): LocaleNode | LocaleTree;
    setChild(key: string, value: LocaleTree | LocaleNode): void;
}
export interface ILocaleRecord extends INode {
    value: string;
    locale: string;
}
export interface ILocaleNode extends INode {
    locales?: Record<string, LocaleRecord>;
}
export interface ILocaleTree extends INode {
    children?: Record<string | number, LocaleTree | LocaleNode>;
    values?: Record<string, object>;
    isCollection?: boolean;
}
export interface FlattenLocaleTree extends Record<string, LocaleNode> {
}
export declare type Node = LocaleNode | LocaleRecord | LocaleTree;
export {};
