import { CommandOptions } from './common';
import { LocaleTreeItem, ProgressSubmenuItem } from '~/views';
import { LocaleNode } from '~/core';
export declare function promptForSourceLocale(defaultLocale: string, node?: LocaleNode): Promise<string | undefined>;
export declare function TranslateKeys(item?: LocaleTreeItem | ProgressSubmenuItem | CommandOptions): Promise<void>;
