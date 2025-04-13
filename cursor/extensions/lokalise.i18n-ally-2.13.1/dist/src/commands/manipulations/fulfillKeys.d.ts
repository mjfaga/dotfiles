import { CommandOptions } from './common';
import { ProgressSubmenuItem, LocaleTreeItem } from '~/views';
import { PendingWrite } from '~/core';
export declare function FulfillMissingKeysForProgress(item: ProgressSubmenuItem): Promise<{
    locale: string;
    value: string;
    filepath: string | undefined;
    keypath: string;
}[] | undefined>;
export declare function FulfillAllMissingKeys(prompt?: boolean, extraKeys?: string[]): Promise<PendingWrite[] | undefined>;
export declare function FulfillKeys(item?: LocaleTreeItem | ProgressSubmenuItem | CommandOptions): Promise<void>;
