import { KeyStyle } from '../core/types';
import { LocaleTree, LocaleNode, LocaleRecord } from '~/core';
export declare function caseInsensitiveMatch(a: string, b: string): boolean;
export declare function getKeyname(keypath: string): string;
export declare function notEmpty<T>(value: T | null | undefined): value is T;
export declare function escapeMarkdown(text: string): string;
export declare function resolveFlattenRootKeypath(keypath: string): string;
export declare function resolveFlattenRoot(node: undefined): undefined;
export declare function resolveFlattenRoot(node: LocaleRecord): LocaleRecord;
export declare function resolveFlattenRoot(node: LocaleTree | LocaleNode): LocaleTree | LocaleNode;
export declare function resolveFlattenRoot(node?: LocaleTree | LocaleNode): LocaleTree | LocaleNode | undefined;
export declare function set(obj: any, key: string, value: any, override?: boolean): any;
export declare function setNested(obj: any, keys: string[], value: any): void;
export declare function applyPendingToObject(obj: any, keypath: string, value: any, keyStyle?: KeyStyle): any;
export declare function abbreviateNumber(value: number): string;
/**
 * Get a locale aware comparison function
 */
export declare function getLocaleCompare(sortLocaleSetting: string | undefined, fileLocale: string): (x: string, y: string) => number;
