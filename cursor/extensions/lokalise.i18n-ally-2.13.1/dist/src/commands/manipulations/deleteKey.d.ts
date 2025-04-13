import { LocaleTreeItem, UsageReportRootItem } from '~/views';
import { LocaleRecord } from '~/core';
export declare function DeleteRecords(records: LocaleRecord[]): Promise<void>;
export declare function DeleteKey(item: LocaleTreeItem | UsageReportRootItem): Promise<void>;
