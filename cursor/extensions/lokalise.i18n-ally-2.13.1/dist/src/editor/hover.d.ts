import { MarkdownString } from 'vscode';
import { LocaleRecord } from '~/core';
export declare function createTable(visibleLocales: string[], records: Record<string, LocaleRecord>, maxLength?: number, keyIndex?: number): string;
export declare function createHover(keypath: string, maxLength?: number, mainLocale?: string, keyIndex?: number): MarkdownString | undefined;
