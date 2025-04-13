import { ExtensionContext } from 'vscode';
import { BaseTreeItem } from '.';
import { KeyUsage } from '~/core';
export declare class UsageReportRootItem extends BaseTreeItem {
    readonly key: 'active' | 'idle' | 'missing';
    readonly keys: KeyUsage[];
    readonly count: number;
    constructor(ctx: ExtensionContext, key: 'active' | 'idle' | 'missing', keys: KeyUsage[]);
    getLabel(): string;
    get contextValue(): string;
    set contextValue(_: string);
}
