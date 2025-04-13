import { LocaleTreeItem, ProgressSubmenuItem } from '~/views';
import { Node, LocaleNode, LocaleRecord, ActionSource } from '~/core';
export interface CommandOptions {
    keypath: string;
    locale?: string;
    from?: string;
    locales?: string[];
    keyIndex?: number;
    actionSource?: ActionSource;
}
export declare function getNodeOrRecord(item?: LocaleTreeItem | CommandOptions): LocaleNode | LocaleRecord | undefined;
export declare function getNode(item?: LocaleTreeItem | CommandOptions | ProgressSubmenuItem): LocaleNode | undefined;
export declare function getRecordFromNode(node: Node, defaultLocale?: string): Promise<LocaleRecord | undefined>;
